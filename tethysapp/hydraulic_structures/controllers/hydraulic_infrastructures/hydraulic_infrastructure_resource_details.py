"""
* Name: irrigation_zone_details.py
* Author: msouffront, htran
* Created On: December 23, 2020
* Copyright: (c) Aquaveo 2020
********************************************************************************
"""
__all__ = ['HydraulicStructuresHydraulicInfrastructureResourceDetails']

from tethysext.atcore.controllers.resources import TabbedResourceDetails
from tethysapp.hydraulic_structures.controllers.hydraulic_infrastructures.tabs import HydraulicInfrastructureSummaryTab, HydraulicInfrastructureFilesTab


class HydraulicStructuresHydraulicInfrastructureResourceDetails(TabbedResourceDetails):
    """
    Controller for HydraulicInfrastructure details page(s).
    """
    base_template = 'hydraulic_structures/base.html'
    tabs = (
        {'slug': 'summary', 'title': 'Summary', 'view': HydraulicInfrastructureSummaryTab},
        {'slug': 'files', 'title': 'Files', 'view': HydraulicInfrastructureFilesTab},
    )
