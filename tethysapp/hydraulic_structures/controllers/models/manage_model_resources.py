import logging

from django.shortcuts import reverse

from tethysext.atcore.controllers.app_users import ManageResources
from tethysext.atcore.mixins.file_collection_controller_mixin import FileCollectionsControllerMixin
from tethysapp.hydraulic_structures.services.spatial_managers.hydraulic_structures import HydraulicStructuresSpatialManager

from tethysapp.hydraulic_structures.app import HydraulicStructures as app

log = logging.getLogger(f'tethys.{__name__}')


class ManageHydraulicStructuresModelResources(ManageResources, FileCollectionsControllerMixin):
    """
    Controller for manage_resources page.
    """
    base_template = 'hydraulic_structures/base.html'
    MODEL_ENGINE_SPATIAL_MANAGER_LOOKUP = {'CropWat': HydraulicStructuresSpatialManager}

    def get_launch_url(self, request, resource):
        """
        Get the URL for the Resource Launch button.
        """
        return reverse('hydraulic_structures:model_details_tab', args=[resource.id, 'summary'])

    def get_error_url(self, request, resource):
        """
        Get the URL for the Resource Launch button.
        """
        return reverse('hydraulic_structures:model_details_tab', args=[resource.id, 'summary'])

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
        self.delete_file_collections(
            session=session,
            resource=resource,
            log=log
        )

        # Get geoserver engine and remove geoserver layers.
        gs_engine = app.get_spatial_dataset_service(app.GEOSERVER_NAME, as_engine=True)

        # Delete model elevations for a given model.
        model_engine = 'CropWat'
        x_spatial_manager = self.MODEL_ENGINE_SPATIAL_MANAGER_LOOKUP.get(model_engine)(gs_engine)
        x_spatial_manager.delete_all_layers(resource_id=str(resource.id))
