from tethysext.atcore.services.resource_spatial_manager import ResourceSpatialManager

from .base import HydraulicInfrastructureSpatialManager, ProjectAreaSpatialManager

__all__ = ['HydraulicStructuresSpatialManager', 'HydraulicInfrastructureSpatialManager',
           'HydraulicStructuresProjectAreaSpatialManager', 'HealthInfrastructureSpatialManager']


class HydraulicStructuresSpatialManager(ResourceSpatialManager):
    WORKSPACE = 'hydraulic_structures'
    URI = 'http://app.aquaveo.com/hydraulic_structures'
    DATASTORE = 'hydraulic_structures_primary_db'


class HydraulicInfrastructureSpatialManager(HydraulicInfrastructureSpatialManager, HydraulicStructuresSpatialManager):
    pass


class HealthInfrastructureSpatialManager(HydraulicInfrastructureSpatialManager, HydraulicStructuresSpatialManager):
    pass


class HydraulicStructuresProjectAreaSpatialManager(ProjectAreaSpatialManager, HydraulicStructuresSpatialManager):
    def get_extent_for_project(self, datastore_name, resource_id):
        """
        Get the extent. This will return the list of the extent in EPSG 4326.
        The query in resource_extent_layer_view transforms all features to 4326.

        Args:
            For example: app_primary_db.
            resource_id(str): id of the Resources.
        """
        # feature name
        feature_name = self.get_extent_layer_name(resource_id)

        extent = self.gs_api.get_layer_extent(
            workspace=self.WORKSPACE,
            datastore_name=feature_name,
            feature_name=feature_name,
        )

        return extent
