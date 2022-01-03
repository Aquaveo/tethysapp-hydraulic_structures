from tethysext.atcore.services.resource_spatial_manager import ResourceSpatialManager

from .base import HydraulicInfrastructureSpatialManager, ProjectAreaSpatialManager

__all__ = ['HydraulicStructuresSpatialManager', 'HydraulicStructuresHydraulicInfrastructureSpatialManager',
           'HydraulicStructuresProjectAreaSpatialManager', 'HydraulicStructuresHealthInfrastructureSpatialManager']


class HydraulicStructuresSpatialManager(ResourceSpatialManager):
    WORKSPACE = 'hydraulic_structures'
    URI = 'http://app.aquaveo.com/hydraulic_structures'
    DATASTORE = 'hydraulic_structures_primary_db'


class HydraulicStructuresHydraulicInfrastructureSpatialManager(HydraulicInfrastructureSpatialManager, HydraulicStructuresSpatialManager):
    pass


class HydraulicStructuresHealthInfrastructureSpatialManager(HydraulicInfrastructureSpatialManager, HydraulicStructuresSpatialManager):
    pass


class HydraulicStructuresProjectAreaSpatialManager(ProjectAreaSpatialManager, HydraulicStructuresSpatialManager):
    pass
