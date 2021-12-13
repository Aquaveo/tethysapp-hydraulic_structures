from tethysext.atcore.services.resource_spatial_manager import ResourceSpatialManager

from .base import DamSpatialManager, IrrigationZoneSpatialManager

__all__ = ['HydraulicStructuresSpatialManager', 'HydraulicStructuresDamSpatialManager', 'HydraulicStructuresIrrigationZoneSpatialManager']


class HydraulicStructuresSpatialManager(ResourceSpatialManager):
    WORKSPACE = 'hydraulic_structures'
    URI = 'http://app.aquaveo.com/hydraulic_structures'
    DATASTORE = 'hydraulic_structures_primary_db'


class HydraulicStructuresDamSpatialManager(DamSpatialManager, HydraulicStructuresSpatialManager):
    pass


class HydraulicStructuresIrrigationZoneSpatialManager(IrrigationZoneSpatialManager, HydraulicStructuresSpatialManager):
    pass
