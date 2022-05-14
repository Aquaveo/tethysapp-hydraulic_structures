"""
********************************************************************************
* Name: modify_project_area.py
* Author: gagelarsen
* Created On: December 01, 2020
* Copyright: (c) Aquaveo 2020
********************************************************************************
"""
import logging
import os
import json
import zipfile
import geopandas as gpd
import traceback

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from tethys_sdk.permissions import permission_required, has_permission
from tethys_sdk.compute import get_scheduler
from tethys_sdk.workspaces import user_workspace
from tethys_apps.utilities import get_active_app
from tethys_gizmos.gizmo_options import TextInput, SelectInput

from tethysext.atcore.services.file_database import FileDatabaseClient
from tethysext.atcore.controllers.app_users import ModifyResource
from tethysext.atcore.services.app_users.decorators import active_user_required
from tethysext.atcore.exceptions import ATCoreException
from tethysext.atcore.gizmos import SpatialReferenceSelect
from tethysext.atcore.services.spatial_reference import SpatialReferenceService

from tethysapp.hydraulic_structures.services.upload import UploadProjectAreaWorkflow
from tethysapp.hydraulic_structures.services.spatial_managers.hydraulic_structures import HydraulicStructuresSpatialManager
from tethysapp.hydraulic_structures.job_scripts import create_extent_layer_executable
from tethysapp.hydraulic_structures.app import HydraulicStructures as app

__all__ = ['ModifyProjectArea']
log = logging.getLogger(f'tethys.{__name__}')


class ModifyProjectArea(ModifyResource):
    """
    Controller that handles the new and edit pages for Project Area resources.
    """
    # Srid field options
    include_srid = True
    srid_required = True
    srid_default = ""
    srid_error = "Referencia espacial requerida."

    # File upload options
    include_file_upload = True
    file_upload_required = True
    file_upload_multiple = False
    file_upload_accept = ".zip"
    file_upload_label = "Project Area Files"
    file_upload_help = "Upload a zipped file including a shapefile or geojson file with the area."
    file_upload_error = "Must provide file(s)."

    template_name = "hydraulic_structures/resources/modify_project_area_resource.html"

    @active_user_required()
    @permission_required('create_resource', 'edit_resource', use_or=True)
    def _handle_modify_resource_requests(self, request, resource_id=None, *args, **kwargs):
        """
        Handle get requests.
        """
        _AppUser = self.get_app_user_model()
        _Organization = self.get_organization_model()
        _Resource = self.get_resource_model()
        make_session = self.get_sessionmaker()
        session = make_session()
        request_app_user = _AppUser.get_app_user_from_request(request, session)

        # Defaults
        valid = True
        resource_name = ""
        resource_name_error = ""
        resource_description = ""
        resource_srid = self.srid_default
        resource_srid_text = ""
        resource_srid_error = ""
        selected_organizations = []
        organization_select_error = ""
        file_upload_error = ""

        # GET params
        next_arg = str(request.GET.get('next', ""))
        active_app = get_active_app(request)
        app_namespace = active_app.namespace

        # Set redirect url
        if next_arg == 'manage-organizations':
            next_controller = '{}:app_users_manage_organizations'.format(app_namespace)
        else:
            next_controller = f'{app_namespace}:{_Resource.SLUG}_manage_resources'

        # If ID is provided, then we are editing, otherwise we are creating a new resource
        editing = resource_id is not None
        creating = not editing

        try:
            # Check if can create resources
            can_create_resource, msg = self.can_create_resource(session, request, request_app_user)

            if creating and not can_create_resource:
                raise ATCoreException(msg)

            # Process form submission
            if request.POST and 'modify-resource-submit' in request.POST:
                # POST params
                post_params = request.POST
                resource_name = post_params.get('resource-name', "")
                resource_description = post_params.get('resource-description', "")
                resource_srid = post_params.get('spatial-ref-select', self.srid_default)
                selected_organizations = post_params.getlist('assign-organizations', [])
                files = request.FILES

                # Validate
                if not resource_name:
                    valid = False
                    resource_name_error = "Must specify a name for the {}.".format(
                        _Resource.DISPLAY_TYPE_SINGULAR.lower()
                    )

                # Must assign project to at least one organization
                if len(selected_organizations) < 1:
                    valid = False
                    organization_select_error = "Must assign {} to at least one organization.".format(
                        _Resource.DISPLAY_TYPE_SINGULAR.lower()
                    )

                if creating and self.include_file_upload and self.file_upload_required \
                   and 'input-file-upload' not in files:
                    valid = False
                    file_upload_error = self.file_upload_error

                if creating and self.include_srid and self.srid_required \
                   and not resource_srid:
                    valid = False
                    resource_srid_error = self.srid_error

                if valid:
                    # Look up existing resource
                    if editing:
                        resource = session.query(_Resource).get(resource_id)

                        if not resource:
                            raise ATCoreException('Unable to find {}'.format(
                                _Resource.DISPLAY_TYPE_SINGULAR.lower()
                            ))

                        # Reset the organizations
                        resource.organizations = []

                    # Otherwise create a new project
                    else:
                        resource = _Resource()

                    # Assign name and description
                    resource.name = resource_name
                    resource.description = resource_description

                    # Assign project to organizations
                    for organization_id in selected_organizations:
                        organization = session.query(_Organization).get(organization_id)
                        if organization:
                            resource.organizations.append(organization)

                    # Assign spatial reference id, handling change if editing
                    if self.include_srid:
                        old_srid = resource.get_attribute('srid')
                        srid_changed = resource_srid != old_srid
                        resource.set_attribute('srid', resource_srid)

                        if editing and srid_changed:
                            self.handle_srid_changed(session, request, request_app_user, resource, old_srid,
                                                     resource_srid)

                    # Only do the following if creating a new project
                    if creating:
                        # Set created by
                        resource.created_by = request_app_user.username

                        # Save resource
                        session.commit()

                        # Handle file upload
                        if self.include_file_upload:
                            self.handle_file_upload(session, request, request_app_user, files, resource)

                        # Add Area type
                        resource.set_attribute('area_type', post_params.get('resource-area-type', ""))

                    session.commit()

                    # Call post processing hook
                    self.handle_resource_finished_processing(session, request, request_app_user, resource, editing)

                    # Sessions are closed in the finally block
                    return redirect(reverse(next_controller))

            # Setup edit form fields
            if editing:
                # Get existing resource
                resource = session.query(_Resource).get(resource_id)
                can_edit_resource, msg = self.can_edit_resource(session, request, request_app_user, resource)

                if not can_edit_resource:
                    raise ATCoreException(msg)

                # Initialize the parameters from the existing consultant
                resource_name = resource.name
                resource_description = resource.description

                if self.include_srid:
                    resource_srid = resource.get_attribute('srid')

                # Get organizations of user
                for organization in resource.organizations:
                    if organization.active or request.user.is_staff or has_permission(request, 'has_app_admin_role'):
                        selected_organizations.append(str(organization.id))

            # Define form
            resource_name_input = TextInput(
                display_text='Name',
                name='resource-name',
                placeholder='e.g.: My {}'.format(_Resource.DISPLAY_TYPE_SINGULAR.title()),
                initial=resource_name,
                error=resource_name_error
            )

            resource_area_type_input = SelectInput(
                display_text='Area Type',
                name='resource-area-type',
                options=[
                    ('Región Hidrográfica', 'hydro_region'),
                    ('Región Hidrogeológica', 'hydrogeo_region'),
                    ('Provincia', 'city'),
                    ('Municipio', 'municipality'),
                    ('Comunidad', 'community')
                ],
                select2_options={'placeholder': 'Select an area type', 'allowClear': True}
            )

            # Initial spatial reference value
            srid_initial = None

            if resource_srid:
                srs = SpatialReferenceService(session)
                possible_srids = srs.get_spatial_reference_system_by_srid(resource_srid)['results']
                resource_srid_text = possible_srids[0]['text'] if len(possible_srids) > 0 else ''

            if resource_srid_text and resource_srid:
                srid_initial = (resource_srid_text, resource_srid)

            # Spatial reference service/url
            spatial_reference_controller = '{}:atcore_query_spatial_reference'.format(app_namespace)
            spatial_reference_url = reverse(spatial_reference_controller)

            # Spatial reference select gizmo
            spatial_reference_select = SpatialReferenceSelect(
                display_name='Spatial Reference System',
                name='spatial-ref-select',
                placeholder='Spatial Reference System',
                min_length=2,
                query_delay=500,
                initial=srid_initial,
                error=resource_srid_error,
                spatial_reference_service=spatial_reference_url
            )

            # Populate organizations select
            organization_options = request_app_user.get_organizations(session, request, as_options=True)

            organization_select = SelectInput(
                display_text='Organization(s)',
                name='assign-organizations',
                multiple=True,
                initial=selected_organizations,
                options=organization_options,
                error=organization_select_error
            )

        except Exception as e:
            session and session.rollback()

            if type(e) is ATCoreException:
                error_message = str(e)
            else:
                traceback.print_exc()
                error_message = ("An unexpected error occurred while uploading your project. Please try again or "
                                 "contact support@aquaveo.com for further assistance.")
            log.exception(error_message)
            messages.error(request, error_message)

            # Sessions closed in finally block
            return redirect(reverse(next_controller))

        finally:
            # Close sessions
            session and session.close()

        context = {
            'next_controller': next_controller,
            'editing': editing,
            'type_singular': _Resource.DISPLAY_TYPE_SINGULAR,
            'type_plural': _Resource.DISPLAY_TYPE_PLURAL,
            'resource_name_input': resource_name_input,
            'resource_area_type': resource_area_type_input,
            'organization_select': organization_select,
            'resource_description': resource_description,
            'show_srid_field': self.include_srid,
            'spatial_reference_select': spatial_reference_select,
            'show_file_upload_field': self.include_file_upload and creating,
            'file_upload_multiple': self.file_upload_multiple,
            'file_upload_error': file_upload_error,
            'file_upload_label': self.file_upload_label,
            'file_upload_help': self.file_upload_help,
            'file_upload_accept': self.file_upload_accept,
            'base_template': self.base_template
        }

        context = self.get_context(context)

        return render(request, self.template_name, context)

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
        if not editing:
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
            file_collection = file_database.new_collection(meta={'display_name': 'Archivos de Soporte'})

            for filename in os.listdir(file_dir):
                if filename == '__extent__.geojson':
                    self.add_extent_to_db(os.path.join(file_dir, filename), resource)
                elif filename.endswith('.shp'):
                    shpfile_path = os.path.join(file_dir, filename)
                    json_path = os.path.join(file_dir, '__extent__.geojson')
                    shpfile = gpd.read_file(shpfile_path)
                    shpfile.to_file(json_path, driver='GeoJSON')

                    self.add_extent_to_db(json_path, resource)

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

            # Create extent layer
            sm_module = HydraulicStructuresSpatialManager.__module__
            sm_basename = HydraulicStructuresSpatialManager.__name__
            create_extent_layer_executable.run(
                datastore_name=HydraulicStructuresSpatialManager.DATASTORE,
                resource_id=str(resource.id),
                resource_db_url=app.get_persistent_store_database(app.DATABASE_NAME, as_url=True),
                geoserver_endpoint=gs_engine.endpoint,
                geoserver_username=gs_engine.username,
                geoserver_password=gs_engine.password,
                spatial_manager=f'{sm_module}.{sm_basename}',
                status_key='create_extent_layer'
            )
            log.info('Project Area uploaded.')

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

    @staticmethod
    def add_extent_to_db(file_path, resource):
        with open(file_path, 'r') as geojson_file:
            geojson_data = json.load(geojson_file)
            # Use the first feature as extent.
            features = geojson_data['features']
            extent_dict = {"type": "GeometryCollection", "geometries": []}
            for feature in features:
                extent_dict['geometries'].append(feature['geometry'])
            srid = resource.get_attribute('srid')
            resource.set_extent(obj=extent_dict, object_format='dict', srid=srid)
