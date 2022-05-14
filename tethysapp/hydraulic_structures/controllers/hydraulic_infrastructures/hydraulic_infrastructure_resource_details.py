"""
* Name: project_area_details.py
* Author: msouffront, htran
* Created On: December 23, 2020
* Copyright: (c) Aquaveo 2020
********************************************************************************
"""
__all__ = ['HydraulicInfrastructureResourceDetails']

from tethysext.atcore.controllers.resources import TabbedResourceDetails
from tethysapp.hydraulic_structures.controllers.hydraulic_infrastructures.tabs import HydraulicInfrastructureSummaryTab, HydraulicInfrastructureFilesTab


class HydraulicInfrastructureResourceDetails(TabbedResourceDetails):
    """
    Controller for HydraulicInfrastructure details page(s).
    """
    base_template = 'hydraulic_structures/base.html'
    tabs = (
        {'slug': 'summary', 'title': 'Resumen', 'view': HydraulicInfrastructureSummaryTab},
        {'slug': 'files', 'title': 'Archivos', 'view': HydraulicInfrastructureFilesTab},
    )
