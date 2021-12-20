"""
********************************************************************************
* Name: irrigation_zone_details.py
* Author: gagelarsen
* Created On: December 01, 2020
* Copyright: (c) Aquaveo 2020
********************************************************************************
"""
__all__ = ['IrrigationZoneDetails']

import logging
from tethysext.atcore.controllers.resources import TabbedResourceDetails
from tethysapp.hydraulic_structures.controllers.irrigation_zones.tabs import IrrigationZoneSummaryTab, IrrigationZoneWorkflowsTab, \
    IrrigationZoneHydraulicInfrastructuresTab, IrrigationZoneHealthInfrastructuresTab, IrrigationZoneFilesTab


log = logging.getLogger(f'tethys.{__name__}')


class IrrigationZoneDetails(TabbedResourceDetails):
    """
    Controller for irrigation zone details page(s).
    """
    base_template = 'hydraulic_structures/base.html'
    tabs = (
        {'slug': 'summary', 'title': 'Summary', 'view': IrrigationZoneSummaryTab},
        {'slug': 'models', 'title': 'Health Infrastructures', 'view': IrrigationZoneHealthInfrastructuresTab},
        {'slug': 'hydraulic_infrastructures', 'title': 'Hydraulic Infrastructures', 'view': IrrigationZoneHydraulicInfrastructuresTab},
        {'slug': 'files', 'title': 'Files', 'view': IrrigationZoneFilesTab},
        {'slug': 'workflows', 'title': 'Workflows', 'view': IrrigationZoneWorkflowsTab},
    )
