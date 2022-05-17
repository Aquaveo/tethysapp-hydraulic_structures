import logging
from tethysapp.hydraulic_structures.services.spatial_managers.base import HydraulicStructureSpatialManager

log = logging.getLogger(f'tethys.{__name__}')


class ProjectAreaSpatialManager(HydraulicStructureSpatialManager):
    """Base SpatialManager class for HydraulicStructuresProjectAreaResources with methods specific to HydraulicStructuresProjectAreaResources. Subclasses need to define WORKSPACE and URI properties."""  # noqa: E501
    pass
