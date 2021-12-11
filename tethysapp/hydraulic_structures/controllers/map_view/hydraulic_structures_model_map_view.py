import logging

from django.shortcuts import reverse

from tethys_sdk.permissions import has_permission

from tethysext.atcore.controllers.map_view import MapView
from tethysext.atcore.services.model_file_database import ModelFileDatabase
from tethysext.atcore.services.model_file_database_connection import ModelFileDatabaseConnection

__all__ = ['HydraulicStructuresModelMapView']
log = logging.getLogger(f'tethys.{__name__}')


class HydraulicStructuresModelMapView(MapView):

    http_method_names = ['get', 'post']
    template_name = 'hydraulic_structures/map_view/irrigation_zone_selection_map_view.html'

    def get_model_db(self, request, resource, *args, **kwargs):
        """
        Hook to get managers. Avoid removing or modifying items in context already to prevent unexpected behavior.

        Args:
            request (HttpRequest): The request.
            resource (Resource): Resource instance or None.

        Returns:
            model_db (ModelDatabase): ModelDatabase instance.
            map_manager (MapManager): Map Manager instance
        """  # noqa: E501
        # If resource_id is given, mapview will be created with specific model instance
        if resource:
            database_id = resource.get_attribute('database_id')
            model_db = ModelFileDatabase(self._app, database_id=database_id)

        # If resource_id is not given, general mapview with all model boundaries will be created
        else:
            model_db = ModelFileDatabaseConnection(db_dir=self._app.get_app_workspace().path)

        return model_db

    def get_managers(self, request, resource, *args, **kwargs):
        """
        Hook to create mangers for specific model instances for modflow model map view
        or general instance for model selection map view

        Args:
            request (HttpRequest): The request.
            resource (ModflowHydraulicStructuresModelResource): Modflow Model Resource or none, depending on model or selection map_view
        """
        gs_engine = self._app.get_spatial_dataset_service(self.geoserver_name, as_engine=True)

        # If resource_id is given, mapview will be created with specific model instance
        if resource:
            # model_version = resource.get_attribute('model_version')
            # database_id = resource.get_attribute('database_id')
            #
            # model_db = ModelFileDatabase(self._app, database_id=database_id)
            # model_file_db_connection = model_db.model_db_connection
            # spatial_manager = self._SpatialManager(gs_engine, model_file_db_connection, model_version)
            # map_manager = self._MapManager(spatial_manager=spatial_manager, model_db=model_db)
            model_db = None
            map_manager = None

        # If resource_id is not given, general mapview with all model boundaries will be created
        else:
            model_db = ModelFileDatabaseConnection(db_dir=self._app.get_app_workspace().path)
            spatial_manager = self._SpatialManager(gs_engine)
            map_manager = self._MapManager(spatial_manager=spatial_manager, model_db=model_db)

        return model_db, map_manager

    def get_context(self, request, session, resource, context, model_db, *args, **kwargs):
        """
        Hook to add additional content to context. Avoid removing or modifying items in context already to prevent unexpected behavior.

        Args:
            request (HttpRequest): The request.
            session (sqlalchemy.Session): the session.
            resource (Resource): the resource for this request.
            context (dict): The context dictionary.
            model_db (ModelDatabase): ModelDatabase instance associated with this request.

        Returns:
            dict: modified context dictionary.
        """  # noqa: E501
        # Run super class get context to get context from MapView
        import pdb; pdb.set_trace()
        context = super().get_context(request, session, resource, context, model_db, *args, **kwargs)
        # create legend scales if resource_id is given
        if resource:
            pass
        # if no resource_id, template and map title are changed for model_selection_map_view
        else:
            self.template_name = 'hydraulic_structures/map_view/irrigation_zone_selection_map_view.html'
            context['nav_title'] = 'Water Demand for Irrigation Map'
            context['show_custom_layer'] = False
            context['show_helpers'] = False

        return context

    def default_back_url(self, request, *args, **kwargs):
        """
        only used on model map view so users can go back to model selection map view

        Args:
            request (HttpRequest): The request.

        Returns:
            redirects to the back controller
        """  # noqa: E501
        return reverse('hydraulic_structures:home')

    def get_permissions(self, request, permissions, model_db, *args, **kwargs):
        """
        Hook to modify permissions.

        Args:
            request (HttpRequest): The request.
            permissions (dict): The permissions dictionary with boolean values.
            model_db (ModelDatabase): ModelDatabase instance associated with this request.

        Returns:
            dict: modified permisssions dictionary.
        """
        admin_user = has_permission(request, 'has_app_admin_role')
        permissions.update({'admin_user': admin_user})
        if has_permission(request, 'view_all_resources'):
            permissions['can_use_plot'] = True
            permissions['can_use_action'] = True
            permissions['can_use_geocode'] = True
            permissions['can_view'] = True

        return permissions
