"""
********************************************************************************
* Name: project_area_details.py
* Author: gagelarsen
* Created On: December 01, 2020
* Copyright: (c) Aquaveo 2020
********************************************************************************
"""
__all__ = ['ProjectAreaDetails']

import logging
from tethysext.atcore.controllers.resources import TabbedResourceDetails
from tethysapp.hydraulic_structures.controllers.project_areas.tabs import ProjectAreaSummaryTab, ProjectAreaWorkflowsTab, \
    ProjectAreaHydraulicInfrastructuresTab, ProjectAreaHealthInfrastructuresTab, ProjectAreaFilesTab


log = logging.getLogger(f'tethys.{__name__}')


class ProjectAreaDetails(TabbedResourceDetails):
    """
    Controller for irrigation zone details page(s).
    """
    base_template = 'hydraulic_structures/base.html'
    tabs = (
        {'slug': 'summary', 'title': 'Resumen', 'view': ProjectAreaSummaryTab},
        {'slug': 'hydraulic_infrastructures', 'title': 'Estructuras Hidráulicas', 'view': ProjectAreaHydraulicInfrastructuresTab},
        {'slug': 'models', 'title': 'Estructuras Sanitarias', 'view': ProjectAreaHealthInfrastructuresTab},
        {'slug': 'files', 'title': 'Archivos', 'view': ProjectAreaFilesTab},
        {'slug': 'workflows', 'title': 'Workflows', 'view': ProjectAreaWorkflowsTab},
    )
