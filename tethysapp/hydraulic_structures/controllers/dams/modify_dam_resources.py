import logging
import os
import json
import shutil
import zipfile

from tethys_sdk.compute import get_scheduler
from tethys_sdk.workspaces import user_workspace
from tethysext.atcore.controllers.app_users import ModifyResource
from tethysext.atcore.services.file_database import FileDatabaseClient
from tethysapp.hydraulic_structures.services.upload import UploadDamWorkflow
from tethysapp.hydraulic_structures.services.spatial_managers.hydraulic_structures import HydraulicStructuresSpatialManager

from tethysapp.hydraulic_structures.app import HydraulicStructures as app


__all__ = ['ModifyHydraulicStructuresDamResource']
log = logging.getLogger(f'tethys.{__name__}')


class ModifyHydraulicStructuresDamResource(ModifyResource):
    """
    Controller that handles the new and edit pages for HYDRAULICSTRUCTURES dam resources.
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
    file_upload_label = "Dam Files"
    file_upload_help = "Upload an archive containing the dam files. Include a __extent__.geojson file  to set " \
                       "the spatial extent for the dam."
    file_upload_error = "Must provide file(s)."

    @user_workspace
    def handle_resource_finished_processing(self, session, request, request_app_user, resource, editing,
                                            user_workspace):
        """
        Hook to allow for post processing after the resource has finished being created or updated.
        Args:
            session(sqlalchemy.session): open sqlalchemy session.
            request(django.request): the Django request.
            resource(Resource): The resource being edited or newly created.
            editing(bool): True if editing, False if creating a new resource.
        """
        # Only do the following if creating a new project
        if not editing:
            files = resource.get_attribute('files')
            file_dir = os.path.dirname(files[0])
            with zipfile.ZipFile(files[0], "r") as zip_ref:
                zip_ref.extractall(file_dir)
            # Remove zip file
            os.remove(files[0])

            # Get file database id
            file_database_id = app.get_custom_setting('file_database_id')

            # Create file collection and relationship with dam resource
            file_database = FileDatabaseClient(session, app.get_file_database_root(), file_database_id)
            file_collection = file_database.new_collection(meta={'display_name': 'Dam Files'})
            resource.file_collections.append(file_collection.instance)

            for item in os.listdir(file_dir):
                # Store file in FileCollection
                file_collection.add_item(os.path.join(file_dir, item))

                if item == '__extent__.geojson':
                    with open(os.path.join(file_dir, item), 'r') as geojson_file:
                        geojson_data = json.load(geojson_file)
                        # Use the first feature as extent.
                        extent_dict = geojson_data['features'][0]['geometry']
                        srid = resource.get_attribute('srid')
                        resource.set_extent(obj=extent_dict, object_format='dict', srid=srid)

            # Remove orginal upload directory data.
            shutil.rmtree(file_dir)
            resource.set_attribute('files', '')

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
            job = UploadDamWorkflow(
                app=app,
                user=request.user,
                workflow_name=f'upload_dam_{resource_id}',
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
            log.info('PROJECT UPLOAD job submitted to HTCondor')

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
