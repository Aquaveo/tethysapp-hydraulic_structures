import logging

from django.shortcuts import render, reverse
from tethys_apps.base.permissions import has_permission
from tethys_apps.decorators import permission_required

from tethysext.atcore.controllers.app_users import ManageResources
from tethysext.atcore.mixins.file_collection_controller_mixin import FileCollectionsControllerMixin
from tethysext.atcore.services.app_users.decorators import active_user_required
from tethysapp.hydraulic_structures.controllers.infrastructure_resource_types import HEALTH_INFRASTRUCTURE_TYPE
from tethysapp.hydraulic_structures.services.spatial_managers.hydraulic_structures import (
    HydraulicStructuresSpatialManager,
)
from tethysext.atcore.services.paginate import paginate

from tethysapp.hydraulic_structures.app import HydraulicStructures as app

log = logging.getLogger(f"tethys.{__name__}")


class ManageHealthInfrastructureResources(ManageResources, FileCollectionsControllerMixin):
    """
    Controller for manage_resources page.
    """

    template_name = "hydraulic_structures/resources/manage_health_infrastructure_resource.html"
    base_template = "hydraulic_structures/base.html"

    @active_user_required()
    @permission_required("view_resources", "view_all_resources", use_or=True)
    def _handle_get(self, request, *args, **kwargs):
        """
        Handle get requests.
        """
        # User setting constants
        _SETTINGS_PAGE = "projects"
        _SETTING_PROJECTS_PER_PAGE = "setting_projects-per-page"
        _SETTING_SORT_PROJECT_BY = "setting_sort-projects-by"

        # Setup
        _AppUser = self.get_app_user_model()

        _Resource = self.get_resource_model()
        make_session = self.get_sessionmaker()
        session = make_session()
        request_app_user = _AppUser.get_app_user_from_request(request, session)

        # GET params
        params = request.GET

        page = int(params.get("page", 1))
        results_per_page = params.get("show", None)
        sort_by_raw = params.get("sort_by", None)

        # Update setting if user made a change
        if results_per_page:
            request_app_user.update_setting(
                session=session, page=_SETTINGS_PAGE, key=_SETTING_PROJECTS_PER_PAGE, value=results_per_page
            )

        # Get the existing user setting if loading for the first time
        else:
            results_per_page = request_app_user.get_setting(
                session=session, page=_SETTINGS_PAGE, key=_SETTING_PROJECTS_PER_PAGE, as_value=True
            )

        # Update setting if user made a change
        if sort_by_raw:
            request_app_user.update_setting(
                session=session, page=_SETTINGS_PAGE, key=_SETTING_SORT_PROJECT_BY, value=sort_by_raw
            )

        # Get the existing user setting if loading for the first time
        else:
            sort_by_raw = request_app_user.get_setting(
                session=session, page=_SETTINGS_PAGE, key=_SETTING_SORT_PROJECT_BY, as_value=True
            )

        # Set default settings if not set
        if not results_per_page:
            results_per_page = 10
        if not sort_by_raw:
            sort_by_raw = "date_created:reverse"

        results_per_page = int(results_per_page)

        sort_reversed = ":reverse" in sort_by_raw
        sort_by = sort_by_raw.split(":")[0]

        # Get the resources
        all_resources = self.get_resources(session, request, request_app_user)

        # Build cards
        resource_cards = []
        for resource in all_resources:
            resource_card = resource.__dict__
            resource_card["editable"] = self.can_edit_resource(session, request, resource)
            resource_card["deletable"] = self.can_delete_resource(session, request, resource)
            resource_card["organizations"] = resource.organizations
            resource_card["debugging"] = resource.attributes
            resource_card["attributes"] = resource.attributes
            resource_card["debugging"]["id"] = str(resource.id)

            # Get resource action parameters
            action_dict = self.get_resource_action(
                session=session, request=request, request_app_user=request_app_user, resource=resource
            )

            resource_card["action"] = action_dict["action"]
            resource_card["action_title"] = action_dict["title"]
            resource_card["action_href"] = action_dict["href"]

            resource_cards.append(resource_card)

        # Only attempt to sort if the sort field is a valid attribute of _Resource
        if hasattr(_Resource, sort_by):
            sorted_resources = sorted(
                resource_cards,
                key=lambda resource_card: (not resource_card[sort_by], resource_card[sort_by]),
                reverse=sort_reversed,
            )
        else:
            sorted_resources = resource_cards

        # Generate pagination
        paginated_resources, pagination_info = paginate(
            objects=sorted_resources,
            results_per_page=results_per_page,
            page=page,
            result_name="projects",
            sort_by_raw=sort_by_raw,
            sort_reversed=sort_reversed,
        )

        # Hydraulic Infrastructure Type
        health_structure_types = dict()
        for key, value in HEALTH_INFRASTRUCTURE_TYPE.items():
            health_structure_types[key] = value

        context = self.get_base_context(request)

        context.update(
            {
                "page_title": _Resource.DISPLAY_TYPE_PLURAL,
                "type_plural": _Resource.DISPLAY_TYPE_PLURAL,
                "type_singular": _Resource.DISPLAY_TYPE_SINGULAR,
                "resource_slug": _Resource.SLUG,
                "base_template": self.base_template,
                "resources": paginated_resources,
                "pagination_info": pagination_info,
                "show_new_button": has_permission(request, "create_resource"),
                "show_debugging_info": request_app_user.is_staff(),
                "load_delete_modal": has_permission(request, "delete_resource"),
                "show_links_to_organizations": has_permission(request, "edit_organizations"),
                "show_users_link": has_permission(request, "modify_users"),
                "show_resources_link": has_permission(request, "view_resources"),
                "show_organizations_link": has_permission(request, "view_organizations"),
                "health_structure_types": health_structure_types,
            }
        )

        session.close()
        return render(request, self.template_name, context)

    def get_launch_url(self, request, resource):
        """
        Get the URL for the Resource Launch button.
        """
        return reverse("health_structures:model_details_tab", args=[resource.id, "summary"])

    def get_error_url(self, request, resource):
        """
        Get the URL for the Resource Launch button.
        """
        return reverse("health_structures:model_details_tab", args=[resource.id, "summary"])

    def perform_custom_delete_operations(self, session, request, resource):
        """
        Hook to perform custom delete operations prior to the resource being deleted.

        Args:
            session(sqlalchemy.session): open sqlalchemy session.
            request(django.Request): the DELETE request object.
            resource(Resource): the sqlalchemy Resource instance to be deleted.

        Raises:
            Exception: raise an appropriate exception if an error occurs. The message will be sent as the 'error' field of the JsonResponse.
        """  # noqa: E501
        self.delete_file_collections(session=session, resource=resource, log=log)

        # Delete extent layer
        gs_engine = app.get_spatial_dataset_service(app.GEOSERVER_NAME, as_engine=True)
        health_structures_spatial_manager = HydraulicStructuresSpatialManager(gs_engine)
        health_structures_spatial_manager.delete_extent_layer(
            datastore_name=HydraulicStructuresSpatialManager.DATASTORE,
            resource_id=str(resource.id),
        )
