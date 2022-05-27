"""
********************************************************************************
* Name: manage_project_areas.py
* Author: gagelarsen
* Created On: April 01, 2022
* Copyright: (c) Aquaveo 2022
********************************************************************************
"""
import logging
from sqlalchemy import text

from django.shortcuts import reverse

from tethysext.atcore.controllers.app_users import ManageResources
from tethysext.atcore.mixins.file_collection_controller_mixin import FileCollectionsControllerMixin
from tethysapp.hydraulic_structures.services.spatial_managers.hydraulic_structures import HydraulicStructuresSpatialManager

from tethysapp.hydraulic_structures.app import HydraulicStructures as app


log = logging.getLogger(f'tethys.{__name__}')


class ManageProjectAreas(ManageResources, FileCollectionsControllerMixin):
    """
    Controller for manage_resources page.
    """
    template_name = "hydraulic_structures/resources/manage_project_area_resource.html"
    base_template = 'hydraulic_structures/base.html'

    def get_launch_url(self, request, resource):
        """
        Get the URL for the Resource Launch button.
        """
        return reverse('hydraulic_structures:project_area_details_tab', args=[resource.id, 'summary'])

    def get_error_url(self, request, resource):
        """
        Get the URL for the Resource Launch button.
        """
        return reverse('hydraulic_structures:project_area_details_tab', args=[resource.id, 'summary'])

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
        # Delete file collections
        self.delete_file_collections(session=session, resource=resource, log=log)

        # Delete feature layers table
        sql = text(f'DROP TABLE IF EXISTS "{str(resource.id)}_feature_layers";')
        session.get_bind().execute(sql)

        # Delete geoserver layer
        gs_engine = app.get_spatial_dataset_service(app.GEOSERVER_NAME, as_engine=True)

        resource_id = str(resource.id)
        hydraulic_structures_spatial_manager = HydraulicStructuresSpatialManager(gs_engine)
        hydraulic_structures_spatial_manager.delete_extent_layer(
            datastore_name=HydraulicStructuresSpatialManager.DATASTORE,
            resource_id=resource_id
        )
