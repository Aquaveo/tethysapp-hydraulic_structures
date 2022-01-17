import logging
import traceback
import os
import json
import shutil
import zipfile
import datetime

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls.base import reverse
from sqlalchemy.orm.base import PASSIVE_NO_RESULT
from tethys_apps.decorators import permission_required
from tethys_apps.utilities import get_active_app

from tethys_sdk.compute import get_scheduler
from tethys_sdk.workspaces import user_workspace
from tethys_gizmos.gizmo_options import TextInput, SelectInput

from tethysext.atcore.controllers.app_users import ModifyResource
from tethysext.atcore.exceptions import ATCoreException
from tethysext.atcore.gizmos.spatial_reference_select import SpatialReferenceSelect
from tethysext.atcore.services.app_users.decorators import active_user_required
from tethysext.atcore.services.file_database import FileDatabaseClient
from tethysext.atcore.services.spatial_reference import SpatialReferenceService
from tethysapp.hydraulic_structures.controllers.health_infrastructures.components.sewer_context import (
    storm_sewer_create_context,
    sanitary_sewer_create_context,
)
from tethysapp.hydraulic_structures.controllers.health_infrastructures.components.treatment_plant_context import (
    sewer_treatment_plant_create_context,
    water_treatment_plant_create_context,
)
from tethysapp.hydraulic_structures.controllers.health_infrastructures.components.aqueduct_context import (
    hydraulic_dam_create_context,
    well_create_context,
    pipe_line_create_context,
    gravity_pipe_line_create_context,
    distribution_network_create_context,
    storage_tank_create_context,
)
from tethysapp.hydraulic_structures.services.upload import UploadHealthInfrastructureWorkflow
from tethysapp.hydraulic_structures.services.spatial_managers.hydraulic_structures import (
    HydraulicStructuresSpatialManager,
)

from tethysapp.hydraulic_structures.app import HydraulicStructures as app
from tethysapp.hydraulic_structures.controllers.infrastructure_resource_types import HEALTH_INFRASTRUCTURE_TYPE


__all__ = ["ModifyHealthInfrastructureResource"]
log = logging.getLogger(f"tethys.{__name__}")


class ModifyHealthInfrastructureResource(ModifyResource):
    """
    Controller that handles the new and edit pages for HYDRAULICSTRUCTURES health_infrastructure resources.
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
    file_upload_label = "Health Infrastructure Files"
    file_upload_help = (
        "Upload an archive containing the health infrastructure files. Include a __extent__.geojson file  to set "
        "the spatial extent for the health infrastructure."
    )
    file_upload_error = "Must provide file(s)."
    template_name = "hydraulic_structures/resources/modify_health_infrastructure_resource.html"

    @active_user_required()
    @permission_required("create_resource", "edit_resource", use_or=True)
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
        health_structure_type = None
        show_hydraulic_dam = False
        show_well = False
        show_pipe_line = False
        show_storage_tank = False
        show_gravity_pipe_line = False
        show_distribution_network = False
        show_water_treatment_plant = False
        show_sewer_treatment_plant = False
        show_sanitary_sewer = False
        show_storm_sewer = False

        # Dams and Resevoirs
        hydraulic_dam_purposes_init = []
        hydraulic_dam_year_init = datetime.datetime.now().year
        hydraulic_dam_height_init = ""
        hydraulic_dam_volume_init = ""
        hydraulic_dam_purposes = []
        hydraulic_dam_year = None
        hydraulic_dam_height = None
        hydraulic_dam_volume = None
        hydraulic_dam_context = {}

        # Well
        well_year_init = ""
        well_year = ""
        well_context = {}

        # Pipe Line
        pipe_line_year_init = ""
        pipe_line_year = ""
        pipe_line_context = {}

        # Storage Tank
        storage_tank_year_init = ""
        storage_tank_year = ""
        storage_tank_context = {}

        # Gravity Pipe Line
        gravity_pipe_line_year_init = ""
        gravity_pipe_line_year = ""
        gravity_pipe_line_context = {}

        # Distribution Network
        distribution_network_year_init = ""
        distribution_network_year = ""
        distribution_network_context = {}

        # Water Treatment Plant
        water_treatment_plant_year_init = ""
        water_treatment_plant_year = ""
        water_treatment_plant_context = {}

        # Sewer Treatment Plant
        sewer_treatment_plant_year_init = ""
        sewer_treatment_plant_year = ""
        sewer_treatment_plant_context = {}

        # Sanitary Sewer
        sanitary_sewer_year_init = ""
        sanitary_sewer_year = ""
        sanitary_sewer_context = {}

        # Storm Sewer
        storm_sewer_year_init = ""
        storm_sewer_year = ""
        storm_sewer_context = {}

        # GET params
        next_arg = str(request.GET.get("next", ""))
        active_app = get_active_app(request)
        app_namespace = active_app.namespace

        # Set redirect url
        if next_arg == "manage-organizations":
            next_controller = "{}:app_users_manage_organizations".format(app_namespace)
        else:
            next_controller = f"{app_namespace}:{_Resource.SLUG}_manage_resources"

        # If ID is provided, then we are editing, otherwise we are creating a new resource
        editing = resource_id is not None
        creating = not editing

        try:
            # Check if can create resources
            can_create_resource, msg = self.can_create_resource(session, request, request_app_user)

            if creating and not can_create_resource:
                raise ATCoreException(msg)

            # Process form submission
            if request.POST and "modify-resource-submit" in request.POST:
                # POST params
                post_params = request.POST
                resource_name = post_params.get("resource-name", "")
                resource_description = post_params.get("resource-description", "")
                resource_srid = post_params.get("spatial-ref-select", self.srid_default)
                selected_organizations = post_params.getlist("assign-organizations", [])
                health_structure_type = post_params.get("health_structure_type", "")

                files = request.FILES

                # hydraulic dam
                hydraulic_dam_purposes = post_params.getlist("hydraulic_dam_purposes", [])
                hydraulic_dam_year = post_params.get("hydraulic_dam_year", "")
                hydraulic_dam_height = post_params.get("hydraulic_dam_height", "")
                hydraulic_dam_volume = post_params.get("hydraulic_dam_volume", "")

                # well
                well_year = post_params.get("well_year", "")

                # pipe line
                pipe_line_year = post_params.get("pipe_line_year", "")

                # storage tank
                storage_tank_year = post_params.get("storage_tank_year", "")

                # gravity pipe line
                gravity_pipe_line_year = post_params.get("gravity_pipe_line_year", "")

                # distribution network
                distribution_network_year = post_params.get("distribution_network_year", "")

                # water treatment
                water_treatment_plant_year = post_params.get("water_treatment_plant_year", "")

                # sewer treatment
                sewer_treatment_plant_year = post_params.get("sewer_treatment_plant_year", "")

                # sanitary sewer
                sanitary_sewer_year = post_params.get("sanitary_sewer_year", "")

                # storm sewer
                storm_sewer_year = post_params.get("storm_sewer_year", "")

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

                if (
                    creating
                    and self.include_file_upload
                    and self.file_upload_required
                    and "input-file-upload" not in files
                ):
                    valid = False
                    file_upload_error = self.file_upload_error

                if creating and self.include_srid and self.srid_required and not resource_srid:
                    valid = False
                    resource_srid_error = self.srid_error

                if valid:
                    # Look up existing resource
                    if editing:
                        resource = session.query(_Resource).get(resource_id)

                        if not resource:
                            raise ATCoreException("Unable to find {}".format(_Resource.DISPLAY_TYPE_SINGULAR.lower()))

                        # Reset the organizations
                        resource.organizations = []

                    # Otherwise create a new project
                    else:
                        resource = _Resource()

                    # Assign name and description and hydraulic structure type
                    resource.name = resource_name
                    resource.set_attribute("health_structure_type", health_structure_type.replace("_", " ").title())
                    resource.description = resource_description

                    # Assign project to organizations
                    for organization_id in selected_organizations:
                        organization = session.query(_Organization).get(organization_id)
                        if organization:
                            resource.organizations.append(organization)

                    # Assign spatial reference id, handling change if editing
                    if self.include_srid:
                        old_srid = resource.get_attribute("srid")
                        srid_changed = resource_srid != old_srid
                        resource.set_attribute("srid", resource_srid)

                        if editing and srid_changed:
                            self.handle_srid_changed(
                                session, request, request_app_user, resource, old_srid, resource_srid
                            )

                    # hydraulic dam
                    if hydraulic_dam_purposes:
                        resource.set_attribute("hydraulic_dam_purposes", hydraulic_dam_purposes)
                    if hydraulic_dam_height:
                        resource.set_attribute("hydraulic_dam_height", hydraulic_dam_height)
                    if hydraulic_dam_volume:
                        resource.set_attribute("hydraulic_dam_volume", hydraulic_dam_volume)
                    if hydraulic_dam_year:
                        resource.set_attribute("hydraulic_dam_year", hydraulic_dam_year)

                    # well
                    if well_year:
                        resource.set_attribute("well_year", well_year)

                    # pipe line
                    if pipe_line_year:
                        resource.set_attribute("pipe_line_year", pipe_line_year)

                    # storage tank
                    if storage_tank_year:
                        resource.set_attribute("storage_tank_year", storage_tank_year)

                    # gravity pipe line
                    if gravity_pipe_line_year:
                        resource.set_attribute(
                            "gravity_pipe_line_year",
                            gravity_pipe_line_year,
                        )

                    # distribution network
                    if distribution_network_year:
                        resource.set_attribute("distribution_network_year", distribution_network_year)

                    # water treatment plant
                    if water_treatment_plant_year:
                        resource.set_attribute("water_treatment_plant_year", water_treatment_plant_year)

                    # sewer treatment plant
                    if sewer_treatment_plant_year:
                        resource.set_attribute("sewer_treatment_plant_year", sewer_treatment_plant_year)

                    # sanitary sewer
                    if sanitary_sewer_year:
                        resource.set_attribute("sanitary_sewer_year", sanitary_sewer_year)

                    # storm sewer
                    if storm_sewer_year:
                        resource.set_attribute("storm_sewer_year", storm_sewer_year)

                    # Only do the following if creating a new project
                    if creating:
                        # Set created by
                        resource.created_by = request_app_user.username

                        # Save resource
                        session.commit()

                        # Handle file upload
                        if self.include_file_upload:
                            self.handle_file_upload(session, request, request_app_user, files, resource)

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
                    resource_srid = resource.get_attribute("srid")

                # Get organizations of user
                for organization in resource.organizations:
                    if organization.active or request.user.is_staff or has_permission(request, "has_app_admin_role"):
                        selected_organizations.append(str(organization.id))

                # edit hydraulic infrastructure type
                health_structure_type = resource.get_attribute("health_structure_type")
                if health_structure_type == HEALTH_INFRASTRUCTURE_TYPE["HYDRAULIC_DAMS"].title():
                    show_hydraulic_dam = True
                    hydraulic_dam_purposes_init = resource.get_attribute("hydraulic_dam_purposes")
                    hydraulic_dam_year_init = resource.get_attribute("hydraulic_dam_year")
                    hydraulic_dam_height_init = resource.get_attribute("hydraulic_dam_height")
                    hydraulic_dam_volume_init = resource.get_attribute("hydraulic_dam_volume")
                if health_structure_type == HEALTH_INFRASTRUCTURE_TYPE["WELLS"].title():
                    show_well = True
                    well_year_init = resource.get_attribute("well_year")
                if health_structure_type == HEALTH_INFRASTRUCTURE_TYPE["PIPE_LINE"].title():
                    show_pipe_line = True
                    pipe_line_year_init = resource.get_attribute("pipe_line_year")
                if health_structure_type == HEALTH_INFRASTRUCTURE_TYPE["STORAGE_TANK"].title():
                    show_storage_tank = True
                    storage_tank_year_init = resource.get_attribute("storage_tank_year")
                if health_structure_type == HEALTH_INFRASTRUCTURE_TYPE["GRAVITY_PIPE_LINE"].title():
                    show_gravity_pipe_line = True
                    gravity_pipe_line_year_init = resource.get_attribute("gravity_pipe_line_year")
                if health_structure_type == HEALTH_INFRASTRUCTURE_TYPE["DISTRIBUTION_NETWORK"].title():
                    show_distribution_network = True
                    distribution_network_year_init = resource.get_attribute("distribution_network_year")
                if health_structure_type == HEALTH_INFRASTRUCTURE_TYPE["WATER_TREATMENT_PLANTS"].title():
                    show_water_treatment_plant = True
                    water_treatment_plant_year_init = resource.get_attribute("water_treatment_plant_year")
                if health_structure_type == HEALTH_INFRASTRUCTURE_TYPE["SEWER_TREATMENT_PLANTS"].title():
                    show_sewer_treatment_plant = True
                    sewer_treatment_plant_year_init = resource.get_attribute("sewer_treatment_plant_year")
                if health_structure_type == HEALTH_INFRASTRUCTURE_TYPE["SANITARY_SEWERS"].title():
                    show_sanitary_sewer = True
                    sanitary_sewer_year_init = resource.get_attribute("sanitary_sewer_year")
                if health_structure_type == HEALTH_INFRASTRUCTURE_TYPE["STORM_SEWERS"].title():
                    show_storm_sewer = True
                    storm_sewer_year_init = resource.get_attribute("storm_sewer_year")

            # Define form
            resource_name_input = TextInput(
                display_text="Name",
                name="resource-name",
                placeholder="e.g.: My {}".format(_Resource.DISPLAY_TYPE_SINGULAR.title()),
                initial=resource_name,
                error=resource_name_error,
            )

            # Initial spatial reference value
            srid_initial = None

            if resource_srid:
                srs = SpatialReferenceService(session)
                possible_srids = srs.get_spatial_reference_system_by_srid(resource_srid)["results"]
                resource_srid_text = possible_srids[0]["text"] if len(possible_srids) > 0 else ""

            if resource_srid_text and resource_srid:
                srid_initial = (resource_srid_text, resource_srid)

            # Spatial reference service/url
            spatial_reference_controller = "{}:atcore_query_spatial_reference".format(app_namespace)
            spatial_reference_url = reverse(spatial_reference_controller)

            # Spatial reference select gizmo
            spatial_reference_select = SpatialReferenceSelect(
                display_name="Spatial Reference System",
                name="spatial-ref-select",
                placeholder="Spatial Reference System",
                min_length=2,
                query_delay=500,
                initial=srid_initial,
                error=resource_srid_error,
                spatial_reference_service=spatial_reference_url,
            )

            # Populate organizations select
            organization_options = request_app_user.get_organizations(session, request, as_options=True)

            organization_select = SelectInput(
                display_text="Organization(s)",
                name="assign-organizations",
                multiple=True,
                initial=selected_organizations,
                options=organization_options,
                error=organization_select_error,
            )

            # populate custom type for each hydraulic infrastructure type
            if request.POST and "health-structure-type" in request.POST:
                if request.POST["health-structure-type"]:
                    health_structure_type = request.POST["health-structure-type"]
                    show_hydraulic_dam = True if health_structure_type == "HYDRAULIC_DAMS" else False
                    show_well = True if health_structure_type == "WELLS" else False
                    show_pipe_line = True if health_structure_type == "PIPE_LINE" else False
                    show_storage_tank = True if health_structure_type == "STORAGE_TANK" else False
                    show_gravity_pipe_line = True if health_structure_type == "GRAVITY_PIPE_LINE" else False
                    show_distribution_network = True if health_structure_type == "DISTRIBUTION_NETWORK" else False
                    show_water_treatment_plant = True if health_structure_type == "WATER_TREATMENT_PLANTS" else False
                    show_sewer_treatment_plant = True if health_structure_type == "SEWER_TREATMENT_PLANTS" else False
                    show_sanitary_sewer = True if health_structure_type == "SANITARY_SEWERS" else False
                    show_storm_sewer = True if health_structure_type == "STORM_SEWERS" else False

            if show_hydraulic_dam:
                hydraulic_dam_context = hydraulic_dam_create_context(
                    hydraulic_dam_purposes_init,
                    hydraulic_dam_year_init,
                    hydraulic_dam_height_init,
                    hydraulic_dam_volume_init,
                )
            if show_well:
                well_context = well_create_context(well_year_init)
            if show_pipe_line:
                pipe_line_context = pipe_line_create_context(pipe_line_year_init)
            if show_storage_tank:
                storage_tank_context = storage_tank_create_context(storage_tank_year_init)
            if show_gravity_pipe_line:
                gravity_pipe_line_context = gravity_pipe_line_create_context(gravity_pipe_line_year_init)
            if show_distribution_network:
                distribution_network_context = distribution_network_create_context(distribution_network_year_init)
            if show_water_treatment_plant:
                water_treatment_plant_context = water_treatment_plant_create_context(water_treatment_plant_year_init)
            if show_sewer_treatment_plant:
                sewer_treatment_plant_context = sewer_treatment_plant_create_context(sewer_treatment_plant_year_init)
            if show_sanitary_sewer:
                sanitary_sewer_context = sanitary_sewer_create_context(sanitary_sewer_year_init)
            if show_storm_sewer:
                storm_sewer_context = storm_sewer_create_context(storm_sewer_year_init)

        except Exception as e:
            session and session.rollback()

            if type(e) is ATCoreException:
                error_message = str(e)
            else:
                traceback.print_exc()
                error_message = (
                    "An unexpected error occurred while uploading your project. Please try again or "
                    "contact support@aquaveo.com for further assistance."
                )
            log.exception(error_message)
            messages.error(request, error_message)

            # Sessions closed in finally block
            return redirect(reverse(next_controller))

        finally:
            # Close sessions
            session and session.close()

        context = {
            "next_controller": next_controller,
            "editing": editing,
            "type_singular": _Resource.DISPLAY_TYPE_SINGULAR,
            "type_plural": _Resource.DISPLAY_TYPE_PLURAL,
            "resource_name_input": resource_name_input,
            "organization_select": organization_select,
            "resource_description": resource_description,
            "show_srid_field": self.include_srid,
            "spatial_reference_select": spatial_reference_select,
            "show_file_upload_field": self.include_file_upload and creating,
            "file_upload_multiple": self.file_upload_multiple,
            "file_upload_error": file_upload_error,
            "file_upload_label": f"{HEALTH_INFRASTRUCTURE_TYPE[health_structure_type]} Files",
            "file_upload_help": self.file_upload_help,
            "file_upload_accept": self.file_upload_accept,
            "health_structure_type": health_structure_type,
            "health_structure_type_spanish": HEALTH_INFRASTRUCTURE_TYPE[health_structure_type],
            "show_hydraulic_dam": show_hydraulic_dam,
            "show_well": show_well,
            "show_pipe_line": show_pipe_line,
            "show_storage_tank": show_storage_tank,
            "show_gravity_pipe_line": show_gravity_pipe_line,
            "show_distribution_network": show_distribution_network,
            "show_water_treatment_plant": show_water_treatment_plant,
            "show_sewer_treatment_plant": show_sewer_treatment_plant,
            "show_sanitary_sewer": show_sanitary_sewer,
            "show_storm_sewer": show_storm_sewer,
            "base_template": self.base_template,
            **hydraulic_dam_context,
            **well_context,
            **pipe_line_context,
            **storage_tank_context,
            **gravity_pipe_line_context,
            **distribution_network_context,
            **water_treatment_plant_context,
            **sewer_treatment_plant_context,
            **sanitary_sewer_context,
            **storm_sewer_context,
        }

        context = self.get_context(context)

        return render(request, self.template_name, context)

    @user_workspace
    def handle_resource_finished_processing(
        self, session, request, request_app_user, resource, editing, user_workspace
    ):
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
            files = resource.get_attribute("files")
            file_dir = os.path.dirname(files[0])
            with zipfile.ZipFile(files[0], "r") as zip_ref:
                zip_ref.extractall(file_dir)
            # Remove zip file
            os.remove(files[0])

            # Get file database id
            file_database_id = app.get_custom_setting("file_database_id")

            # Create file collection and relationship with health_infrastructure resource
            file_database = FileDatabaseClient(session, app.get_file_database_root(), file_database_id)
            file_collection = file_database.new_collection(meta={"display_name": "Hydraulic Infrastructure Files"})
            resource.file_collections.append(file_collection.instance)

            for item in os.listdir(file_dir):
                # Store file in FileCollection
                file_collection.add_item(os.path.join(file_dir, item))

                if item == "__extent__.geojson":
                    with open(os.path.join(file_dir, item), "r") as geojson_file:
                        geojson_data = json.load(geojson_file)
                        # Use the first feature as extent.
                        extent_dict = geojson_data["features"][0]["geometry"]
                        srid = resource.get_attribute("srid")
                        resource.set_extent(obj=extent_dict, object_format="dict", srid=srid)

            # Remove orginal upload directory data.
            shutil.rmtree(file_dir)
            resource.set_attribute("files", "")

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
            job = UploadHealthInfrastructureWorkflow(
                app=app,
                user=request.user,
                workflow_name=f"upload_health_infrastructure_{resource_id}",
                workspace_path=job_path,
                resource_db_url=app.get_persistent_store_database(app.DATABASE_NAME, as_url=True),
                resource=resource,
                gs_engine=gs_engine,
                job_manager=app.get_job_manager(),
                scheduler=get_scheduler(app.SCHEDULER_NAME),
                spatial_manager=HydraulicStructuresSpatialManager,
                status_keys=[],  # DO NOT REMOVE
            )

            job.run_job()
            log.info("PROJECT UPLOAD job submitted to HTCondor")

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
