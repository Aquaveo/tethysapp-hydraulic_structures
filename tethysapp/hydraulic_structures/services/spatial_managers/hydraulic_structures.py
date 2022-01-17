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
    pass
