"""
* Name: model_resource_details.py
* Author: msouffront, htran
* Created On: January 26, 2021
* Copyright: (c) Aquaveo 2021
********************************************************************************
"""
__all__ = ['HydraulicStructuresModelResourceDetails']

from tethysext.atcore.controllers.resources import TabbedResourceDetails
from tethysapp.hydraulic_structures.controllers.models.tabs import ModelFilesTab, ModelSummaryTab


class HydraulicStructuresModelResourceDetails(TabbedResourceDetails):
    """
    Controller for Model details page(s).
    """
    base_template = 'hydraulic_structures/base.html'
    tabs = (
        {'slug': 'summary', 'title': 'Summary', 'view': ModelSummaryTab},
        {'slug': 'files', 'title': 'Files', 'view': ModelFilesTab},
    )
