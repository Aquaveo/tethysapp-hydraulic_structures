"""
* Name: irrigation_zone_details.py
* Author: msouffront, htran
* Created On: December 23, 2020
* Copyright: (c) Aquaveo 2020
********************************************************************************
"""
__all__ = ['HydraulicStructuresDamResourceDetails']

from tethysext.atcore.controllers.resources import TabbedResourceDetails
from tethysapp.hydraulic_structures.controllers.dams.tabs import DamSummaryTab, DamFilesTab


class HydraulicStructuresDamResourceDetails(TabbedResourceDetails):
    """
    Controller for Dam details page(s).
    """
    base_template = 'hydraulic_structures/base.html'
    tabs = (
        {'slug': 'summary', 'title': 'Summary', 'view': DamSummaryTab},
        {'slug': 'files', 'title': 'Files', 'view': DamFilesTab},
    )
