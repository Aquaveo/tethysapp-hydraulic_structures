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

from tethys_sdk.permissions import permission_required, has_permission
from tethys_gizmos.gizmo_options import TextInput, SelectInput

from tethysapp.hydraulic_structures.controllers.base import ModifyHydraulicStructures
from tethysext.atcore.exceptions import ATCoreException
from tethysext.atcore.gizmos.spatial_reference_select import SpatialReferenceSelect
from tethysext.atcore.services.app_users.decorators import active_user_required
from tethysext.atcore.services.spatial_reference import SpatialReferenceService
from tethysapp.hydraulic_structures.controllers.hydraulic_infrastructures.components.dams_and_resevoirs_context import (
    dams_and_resevoirs_create_context,
)
from tethysapp.hydraulic_structures.controllers.hydraulic_infrastructures.components.diversion_dams_context import (
    diversion_dam_create_context,
)
from tethysapp.hydraulic_structures.controllers.hydraulic_infrastructures.components.hydroelectric_dam_context import (
    hydroelectric_dam_create_context,
)
from tethysapp.hydraulic_structures.controllers.hydraulic_infrastructures.components.irrigation_system_context import (
    drainage_channel_create_context,
    intake_create_context,
    secondary_and_lateral_irrigation_system_create_context,
    intake_storage_pond_create_context,
    main_irrigation_channel_create_context,
)
from tethysapp.hydraulic_structures.controllers.hydraulic_infrastructures.components.river_protection_walls_context import (
    river_protection_wall_create_context,
)

from tethysapp.hydraulic_structures.controllers.infrastructure_resource_types import HYDRAULIC_INFRASTRUCTURE_TYPE


__all__ = ["ModifyHydraulicInfrastructureResource"]
log = logging.getLogger(f"tethys.{__name__}")


class ModifyHydraulicInfrastructureResource(ModifyHydraulicStructures):
    template_name = "hydraulic_structures/resources/modify_hydraulic_infrastructure_resource.html"

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
        hydraulic_structure_type = None
        show_dams_and_resevoirs = False
        show_hydroelectric_dam = False
        show_intake = False
        show_main_irrigation_channel = False
        show_secondary_and_lateral_irrigation_system = False
        show_drainage_channel = False
        show_intake_storage_pond = False
        show_diversion_dam = False
        show_river_protection_wall = False

        # Dams and Resevoirs
        dams_and_resevoirs_purposes_init = []
        dams_and_resevoirs_year_init = datetime.datetime.now().year
        dams_and_resevoirs_height_init = ""
        dams_and_resevoirs_volume_init = ""
        dams_and_resevoirs_purposes = []
        dams_and_resevoirs_year = None
        dams_and_resevoirs_height = None
        dams_and_resevoirs_volume = None
        dams_and_resevoirs_context = {}

        # Hydroelectric Dams
        hydroelectric_dam_year_init = ""
        hydroelectric_dam_year = ""
        hydroelectric_dam_context = {}

        # Irrigation System Intake
        intake_year_init = ""
        intake_year = ""
        intake_context = {}

        # Irrigation System Intake
        main_irrigation_channel_year_init = ""
        main_irrigation_channel_year = ""
        main_irrigation_channel_context = {}

        # Irrigation System secondary and lateral irrigation channels
        secondary_and_lateral_irrigation_channel_year_init = ""
        secondary_and_lateral_irrigation_channel_year = ""
        secondary_and_lateral_irrigation_channel_context = {}

        # Drainage Channels
        drainage_channel_year_init = ""
        drainage_channel_year = ""
        drainage_channel_context = {}

        # Intake Storage Ponds
        intake_storage_pond_year_init = ""
        intake_storage_pond_year = ""
        intake_storage_pond_context = {}

        # diversion_dams
        diversion_dam_year_init = ""
        diversion_dam_year = ""
        diversion_dam_context = {}

        # river protection walls
        river_protection_wall_year_init = ""
        river_protection_wall_year = ""
        river_protection_wall_context = {}

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
                hydraulic_structure_type = post_params.get("hydraulic_structure_type", "")

                files = request.FILES

                # Dam Data
                dams_and_resevoirs_purposes = post_params.getlist("dams_and_resevoirs_purposes", [])
                dams_and_resevoirs_year = post_params.get("dams_and_resevoirs_year", "")
                dams_and_resevoirs_height = post_params.get("dams_and_resevoirs_height", "")
                dams_and_resevoirs_volume = post_params.get("dams_and_resevoirs_volume", "")

                # Hydroelectric Dams
                hydroelectric_dam_year = post_params.get("hydroelectric_dam_year", "")

                # Irrigation System Intake
                intake_year = post_params.get("intake_year", "")

                # Irrigation System Intake
                main_irrigation_channel_year = post_params.get("main_irrigation_channel_year", "")

                # Irrigation System secondary and lateral irrigation channels
                secondary_and_lateral_irrigation_channel_year = post_params.get(
                    "secondary_and_lateral_irrigation_channel_year", ""
                )

                # Drainage Channels
                drainage_channel_year = post_params.get("drainage_channel_year", "")

                # Intake Storage Ponds
                intake_storage_pond_year = post_params.get("intake_storage_pond_year", "")

                # diversion_dams
                diversion_dam_year = post_params.get("on_dam", "")

                # river protection walls
                river_protection_wall_year = post_params.get("river_protection_wall_year", "")

                # Validate
                if not resource_name:
                    valid = False
                    resource_name_error = "Debe especificar el nombre de la {}.".format(
                        _Resource.DISPLAY_TYPE_SINGULAR.lower()
                    )

                # Must assign project to at least one organization
                if len(selected_organizations) < 1:
                    valid = False
                    organization_select_error = "Debe asignar {} a al menos una organización.".format(
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
                    resource.set_attribute(
                        "hydraulic_structure_type", hydraulic_structure_type.replace("_", " ").title()
                    )
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

                    # Dams and Structures
                    if dams_and_resevoirs_purposes:
                        resource.set_attribute("dams_and_resevoirs_purposes", dams_and_resevoirs_purposes)
                    if dams_and_resevoirs_height:
                        resource.set_attribute("dams_and_resevoirs_height", dams_and_resevoirs_height)
                    if dams_and_resevoirs_volume:
                        resource.set_attribute("dams_and_resevoirs_volume", dams_and_resevoirs_volume)
                    if dams_and_resevoirs_year:
                        resource.set_attribute("dams_and_resevoirs_year", dams_and_resevoirs_year)

                    # Hydroelectric Dams
                    if hydroelectric_dam_year:
                        resource.set_attribute("hydroelectric_dam_year", hydroelectric_dam_year)

                    # Irrigation System Intake
                    if intake_year:
                        resource.set_attribute("intake_year", intake_year)

                    # Irrigation System Intake
                    if main_irrigation_channel_year:
                        resource.set_attribute("main_irrigation_channel_year", main_irrigation_channel_year)

                    # Irrigation System secondary and lateral irrigation channels
                    if secondary_and_lateral_irrigation_channel_year:
                        resource.set_attribute(
                            "secondary_and_lateral_irrigation_channel_year",
                            secondary_and_lateral_irrigation_channel_year,
                        )

                    # Drainage Channels
                    if drainage_channel_year:
                        resource.set_attribute("drainage_channel_year", drainage_channel_year)

                    # Intake Storage Ponds
                    if intake_storage_pond_year:
                        resource.set_attribute("intake_storage_pond_year", intake_storage_pond_year)

                    # diversion_dams
                    if diversion_dam_year:
                        resource.set_attribute("diversion_dam_year", diversion_dam_year)

                    # river protection walls
                    if river_protection_wall_year:
                        resource.set_attribute("river_protection_wall_year", river_protection_wall_year)

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
                hydraulic_structure_type = resource.get_attribute("hydraulic_structure_type")
                if hydraulic_structure_type == HYDRAULIC_INFRASTRUCTURE_TYPE["DAMS_AND_RESEVOIRS"].title():
                    show_dams_and_resevoirs = True
                    dams_and_resevoirs_purposes_init = resource.get_attribute("dams_and_resevoirs_purposes")
                    dams_and_resevoirs_year_init = resource.get_attribute("dams_and_resevoirs_year")
                    dams_and_resevoirs_height_init = resource.get_attribute("dams_and_resevoirs_height")
                    dams_and_resevoirs_volume_init = resource.get_attribute("dams_and_resevoirs_volume")
                if hydraulic_structure_type == HYDRAULIC_INFRASTRUCTURE_TYPE["HYDROELECTRIC_DAMS"].title():
                    show_hydroelectric_dam = True
                    hydroelectric_dam_year_init = resource.get_attribute("hydroelectric_dam_year")
                if hydraulic_structure_type == HYDRAULIC_INFRASTRUCTURE_TYPE["IRRIGATION_SYSTEM_INTAKE"].title():
                    show_intake = True
                    intake_year_init = resource.get_attribute("intake_year")
                if (
                    hydraulic_structure_type
                    == HYDRAULIC_INFRASTRUCTURE_TYPE["IRRIGATION_SYSTEM_MAIN_IRRIGATION_CHANNELS"].title()
                ):
                    show_main_irrigation_channel = True
                    main_irrigation_channel_year_init = resource.get_attribute("main_irrigation_channel_year")
                if (
                    hydraulic_structure_type
                    == HYDRAULIC_INFRASTRUCTURE_TYPE[
                        "IRRIGATION_SYSTEM_SECONDARY_AND_LATERAL_IRRIGATION_SYSTEM"
                    ].title()
                ):
                    show_secondary_and_lateral_irrigation_system = True
                    secondary_and_lateral_irrigation_channel_year_init = resource.get_attribute(
                        "secondary_and_lateral_irrigation_channel_year"
                    )
                if (
                    hydraulic_structure_type
                    == HYDRAULIC_INFRASTRUCTURE_TYPE["IRRIGATION_SYSTEM_DRAINAGE_CHANNELS"].title()
                ):
                    show_drainage_channel = True
                    drainage_channel_year_init = resource.get_attribute("drainage_channel_year")
                if (
                    hydraulic_structure_type
                    == HYDRAULIC_INFRASTRUCTURE_TYPE["IRRIGATION_SYSTEM_INTAKE_STORAGE_PONDS"].title()
                ):
                    show_intake_storage_pond = True
                    intake_storage_pond_year_init = resource.get_attribute("intake_storage_pond_year")
                if hydraulic_structure_type == HYDRAULIC_INFRASTRUCTURE_TYPE["DIVERSION_DAMS"].title():
                    show_diversion_dam = True
                    diversion_dam_year_init = resource.get_attribute("diversion_dam_year")
                if hydraulic_structure_type == HYDRAULIC_INFRASTRUCTURE_TYPE["RIVER_PROTECTION_WALLS"].title():
                    show_river_protection_wall = True
                    river_protection_wall_year_init = resource.get_attribute("river_protection_wall_year")

            # Define form
            resource_name_input = TextInput(
                display_text="Nombre",
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
                display_name="Sistema de Referencia Espacial",
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
                display_text="Organizaciones",
                name="assign-organizations",
                multiple=True,
                initial=selected_organizations,
                options=organization_options,
                error=organization_select_error,
            )

            # populate custom type for each hydraulic infrastructure type
            if request.POST and "hydraulic-structure-type" in request.POST:
                mass_upload = True if request.POST.get("mass-upload", None) else False
                if request.POST["hydraulic-structure-type"]:
                    hydraulic_structure_type = request.POST["hydraulic-structure-type"]
                    show_dams_and_resevoirs = True if hydraulic_structure_type == "DAMS_AND_RESEVOIRS" else False
                    show_hydroelectric_dam = True if hydraulic_structure_type == "HYDROELECTRIC_DAMS" else False
                    show_intake = True if hydraulic_structure_type == "IRRIGATION_SYSTEM_INTAKE" else False
                    show_main_irrigation_channel = (
                        True if hydraulic_structure_type == "IRRIGATION_SYSTEM_MAIN_IRRIGATION_CHANNELS" else False
                    )
                    show_secondary_and_lateral_irrigation_system = (
                        True
                        if hydraulic_structure_type == "IRRIGATION_SYSTEM_SECONDARY_AND_LATERAL_IRRIGATION_SYSTEM"
                        else False
                    )
                    show_drainage_channel = (
                        True if hydraulic_structure_type == "IRRIGATION_SYSTEM_DRAINAGE_CHANNELS" else False
                    )
                    show_intake_storage_pond = (
                        True if hydraulic_structure_type == "IRRIGATION_SYSTEM_INTAKE_STORAGE_PONDS" else False
                    )
                    show_diversion_dam = True if hydraulic_structure_type == "DIVERSION_DAMS" else False
                    show_river_protection_wall = (
                        True if hydraulic_structure_type == "RIVER_PROTECTION_WALLS" else False
                    )

            if show_dams_and_resevoirs:
                dams_and_resevoirs_context = dams_and_resevoirs_create_context(
                    dams_and_resevoirs_purposes_init,
                    dams_and_resevoirs_year_init,
                    dams_and_resevoirs_height_init,
                    dams_and_resevoirs_volume_init,
                )
            if show_hydroelectric_dam:
                hydroelectric_dam_context = hydroelectric_dam_create_context(hydroelectric_dam_year_init)
            if show_intake:
                intake_context = intake_create_context(intake_year_init)
            if show_main_irrigation_channel:
                main_irrigation_channel_context = main_irrigation_channel_create_context(
                    main_irrigation_channel_year_init
                )
            if show_secondary_and_lateral_irrigation_system:
                secondary_and_lateral_irrigation_channel_context = (
                    secondary_and_lateral_irrigation_system_create_context(
                        secondary_and_lateral_irrigation_channel_year
                    )
                )
            if show_drainage_channel:
                drainage_channel_context = drainage_channel_create_context(drainage_channel_year_init)
            if show_intake_storage_pond:
                intake_storage_pond_context = intake_storage_pond_create_context(intake_storage_pond_year_init)
            if show_diversion_dam:
                diversion_dam_context = diversion_dam_create_context(diversion_dam_year_init)
            if show_river_protection_wall:
                river_protection_wall_context = river_protection_wall_create_context(river_protection_wall_year_init)

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
            "file_upload_label": self.file_upload_label,
            "file_upload_help": self.file_upload_help,
            "file_upload_accept": self.file_upload_accept,
            "hydraulic_structure_type": hydraulic_structure_type,
            "mass_upload": mass_upload,
            "hydraulic_structure_type_spanish": HYDRAULIC_INFRASTRUCTURE_TYPE[hydraulic_structure_type],
            "show_dams_and_resevoirs": show_dams_and_resevoirs,
            "show_hydroelectric_dam": show_hydroelectric_dam,
            "show_intake": show_intake,
            "show_main_irrigation_channel": show_main_irrigation_channel,
            "show_secondary_and_lateral_irrigation_system": show_secondary_and_lateral_irrigation_system,
            "show_drainage_channel": show_drainage_channel,
            "show_intake_storage_pond": show_intake_storage_pond,
            "show_diversion_dam": show_diversion_dam,
            "show_river_protection_wall": show_river_protection_wall,
            "base_template": self.base_template,
            **dams_and_resevoirs_context,
            **hydroelectric_dam_context,
            **intake_context,
            **main_irrigation_channel_context,
            **secondary_and_lateral_irrigation_channel_context,
            **drainage_channel_context,
            **intake_storage_pond_context,
            **diversion_dam_context,
            **river_protection_wall_context,
        }
        context = self.get_context(context)

        return render(request, self.template_name, context)
