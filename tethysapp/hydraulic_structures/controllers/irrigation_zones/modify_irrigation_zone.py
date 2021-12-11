"""
********************************************************************************
* Name: modify_irrigation_zone.py
* Author: gagelarsen
* Created On: December 01, 2020
* Copyright: (c) Aquaveo 2020
********************************************************************************
"""
import logging
import os
import json
import zipfile

from tethys_sdk.compute import get_scheduler
from tethys_sdk.workspaces import user_workspace
from tethysext.atcore.services.file_database import FileDatabaseClient
from tethysext.atcore.controllers.app_users import ModifyResource
from tethysapp.hydraulic_structures.services.upload import UploadIrrigationZoneWorkflow
from tethysapp.hydraulic_structures.services.spatial_managers.hydraulic_structures import HydraulicStructuresSpatialManager

from tethysapp.hydraulic_structures.app import HydraulicStructures as app

__all__ = ['ModifyIrrigationZone']
log = logging.getLogger(f'tethys.{__name__}')


class ModifyIrrigationZone(ModifyResource):
    """
    Controller that handles the new and edit pages for Irrigation Zone resources.
    """
    # Srid field options
    include_srid = True
    srid_required = True
    srid_default = ""
    srid_error = "Spatial reference is required."

    # File upload options
    include_file_upload = True
    file_upload_required = True
    file_upload_multiple = False
    file_upload_accept = ".zip"
    file_upload_label = "Irrigation Zone Files"
    file_upload_help = "Upload an archive containing the irrigation zone files. Please include an __extent__.geojson " \
                       "file that contains a polygon defining the boundary of the irrigation zone."
    file_upload_error = "Must provide file(s)."

    @user_workspace
    def handle_resource_finished_processing(self, session, request, request_app_user, resource, editing,
                                            user_workspace):
        """
        Hook to allow for post processing after the resource has finished being created or updated.
        Args:
            session(sqlalchemy.session): open sqlalchemy session.
            request(django.request): the Django request.
            request_app_user(AppUser): app user that is making the request.
            resource(Resource): The resource being edited or newly created.
            editing(bool): True if editing, False if creating a new resource.
            user_workspace(TethysWorkspace): Workspace for the request user provided by the user_workspace decorator.
        """
        # Only do the following if creating a new irrigation zone
        if not editing:
            # TODO: The logic to unzip the file, set extent from __extent__.geojson, and save in file collection
            # TODO: is copied from ModifyHydraulicStructuresDatasetResource. Refactor to use generalized function in future.
            files = resource.get_attribute('files')
            file_dir = os.path.dirname(files[0])
            with zipfile.ZipFile(files[0], "r") as zip_ref:
                zip_ref.extractall(file_dir)
            # Remove zip file
            os.remove(files[0])

            # Get file database id
            file_database_id = app.get_custom_setting('file_database_id')

            # Store file in FileCollection
            file_database = FileDatabaseClient(session, app.get_file_database_root(), file_database_id)
            file_collection = file_database.new_collection(meta={'display_name': 'Supporting Files'})

            for filename in os.listdir(file_dir):
                if filename == '__extent__.geojson':
                    with open(os.path.join(file_dir, filename), 'r') as geojson_file:
                        geojson_data = json.load(geojson_file)
                        # Use the first feature as extent.
                        extent_dict = geojson_data['features'][0]['geometry']
                        srid = resource.get_attribute('srid')
                        resource.set_extent(obj=extent_dict, object_format='dict', srid=srid)

                # Add all files and dirs to the file collection
                file_collection.add_item(os.path.join(file_dir, filename))

            # Associate file_collection with resource
            resource.file_collections.append(file_collection.instance)

            # Save new project
            session.commit()

            # Upload extent to geoserver
            # Prepare condor job for processing file upload
            user_workspace_path = user_workspace.path
            resource_id = str(resource.id)
            job_path = os.path.join(user_workspace_path, resource_id)

            # Create job directory if it doesn't exist already
            if not os.path.exists(job_path):
                os.makedirs(job_path)

            # Define additional job parameters
            gs_engine = app.get_spatial_dataset_service(app.GEOSERVER_NAME, as_engine=True)

            # Create the condor job and submit
            job = UploadIrrigationZoneWorkflow(
                app=app,
                user=request.user,
                workflow_name=f'upload_irrigation_zone_{resource_id}',
                workspace_path=job_path,
                resource_db_url=app.get_persistent_store_database(app.DATABASE_NAME, as_url=True),
                resource=resource,
                gs_engine=gs_engine,
                job_manager=app.get_job_manager(),
                scheduler=get_scheduler(app.SCHEDULER_NAME),
                spatial_manager=HydraulicStructuresSpatialManager,
                status_keys=[]  # DO NOT REMOVE
            )

            job.run_job()
            log.info('IrrigationZone upload job submitted to HTCondor')

    def handle_srid_changed(self, session, request, request_app_user, resource, old_srid, new_srid):
        """
        Handle srid changed event when editing an existing resource.
        Args:
            session(sqlalchemy.session): open sqlalchemy session.
            request(django.request): the Django request.
            request_app_user(AppUser): app user that is making the request.
            resource(Resource): The resource being edited.
            old_srid(str): The old srid.
            new_srid(str): The new srid.
        """
        resource.update_extent_srid(new_srid)
