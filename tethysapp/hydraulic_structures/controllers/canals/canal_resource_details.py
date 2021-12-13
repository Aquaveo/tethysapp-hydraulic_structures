"""
* Name: model_resource_details.py
* Author: msouffront, htran
* Created On: January 26, 2021
* Copyright: (c) Aquaveo 2021
********************************************************************************
"""
__all__ = ['HydraulicStructuresCanalResourceDetails']

from tethysext.atcore.controllers.resources import TabbedResourceDetails
from tethysapp.hydraulic_structures.controllers.canals.tabs import CanalFilesTab, CanalSummaryTab


class HydraulicStructuresCanalResourceDetails(TabbedResourceDetails):
    """
    Controller for Model details page(s).
    """
    base_template = 'hydraulic_structures/base.html'
    tabs = (
        {'slug': 'summary', 'title': 'Summary', 'view': CanalSummaryTab},
        {'slug': 'files', 'title': 'Files', 'view': CanalFilesTab},
    )
