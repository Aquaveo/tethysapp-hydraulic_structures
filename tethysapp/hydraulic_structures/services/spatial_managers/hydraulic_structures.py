from tethysext.atcore.services.resource_spatial_manager import ResourceSpatialManager

from .base import DatasetSpatialManager, IrrigationZoneSpatialManager

__all__ = ['HydraulicStructuresSpatialManager', 'HydraulicStructuresDatasetSpatialManager', 'HydraulicStructuresIrrigationZoneSpatialManager']


class HydraulicStructuresSpatialManager(ResourceSpatialManager):
    WORKSPACE = 'hydraulic_structures'
    URI = 'http://app.aquaveo.com/hydraulic_structures'
    DATASTORE = 'hydraulic_structures_primary_db'


class HydraulicStructuresDatasetSpatialManager(DatasetSpatialManager, HydraulicStructuresSpatialManager):
    pass


class HydraulicStructuresIrrigationZoneSpatialManager(IrrigationZoneSpatialManager, HydraulicStructuresSpatialManager):
    pass
