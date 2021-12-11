"""
* Name: irrigation_zone_details.py
* Author: msouffront, htran
* Created On: December 23, 2020
* Copyright: (c) Aquaveo 2020
********************************************************************************
"""
__all__ = ['HydraulicStructuresDatasetResourceDetails']

from tethysext.atcore.controllers.resources import TabbedResourceDetails
from tethysapp.hydraulic_structures.controllers.datasets.tabs import DatasetSummaryTab, DatasetFilesTab


class HydraulicStructuresDatasetResourceDetails(TabbedResourceDetails):
    """
    Controller for Dataset details page(s).
    """
    base_template = 'hydraulic_structures/base.html'
    tabs = (
        {'slug': 'summary', 'title': 'Summary', 'view': DatasetSummaryTab},
        {'slug': 'files', 'title': 'Files', 'view': DatasetFilesTab},
    )
