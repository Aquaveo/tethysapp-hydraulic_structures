"""
********************************************************************************
* Name: project_area_workflows_tab.py
* Author: gagelarsen
* Created On: April 02, 2022
* Copyright: (c) Aquaveo 2022
********************************************************************************
"""
from tethysext.atcore.controllers.resources import ResourceWorkflowsTab
from tethysapp.hydraulic_structures.models.hydraulic_structures_workflows import HYDRAULICSTRUCTURES_WORKFLOWS
from tethysapp.hydraulic_structures.services.spatial_managers.hydraulic_structures import HydraulicStructuresSpatialManager

from tethysapp.hydraulic_structures.services.map_manager import HydraulicStructuresMapManager


class ProjectAreaWorkflowsTab(ResourceWorkflowsTab):

    @classmethod
    def get_workflow_types(cls):
        return HYDRAULICSTRUCTURES_WORKFLOWS

    def get_map_manager(self):
        return HydraulicStructuresMapManager

    def get_spatial_manager(self):
        return HydraulicStructuresSpatialManager

    def get_sds_setting_name(self):
        return self.get_app().GEOSERVER_NAME
