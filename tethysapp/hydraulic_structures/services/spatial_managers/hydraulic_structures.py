from tethysext.atcore.services.resource_spatial_manager import ResourceSpatialManager

from .base import HydraulicInfrastructureSpatialManager, IrrigationZoneSpatialManager

__all__ = ['HydraulicStructuresSpatialManager', 'HydraulicStructuresHydraulicInfrastructureSpatialManager',
           'HydraulicStructuresIrrigationZoneSpatialManager', 'HydraulicStructuresHealthInfrastructureSpatialManager']


class HydraulicStructuresSpatialManager(ResourceSpatialManager):
    WORKSPACE = 'hydraulic_structures'
    URI = 'http://app.aquaveo.com/hydraulic_structures'
    DATASTORE = 'hydraulic_structures_primary_db'


class HydraulicStructuresHydraulicInfrastructureSpatialManager(HydraulicInfrastructureSpatialManager, HydraulicStructuresSpatialManager):
    pass


class HydraulicStructuresHealthInfrastructureSpatialManager(HydraulicInfrastructureSpatialManager, HydraulicStructuresSpatialManager):
    pass


class HydraulicStructuresIrrigationZoneSpatialManager(IrrigationZoneSpatialManager, HydraulicStructuresSpatialManager):
    pass
