"""
********************************************************************************
* Name: __init__.py
* Author: glarsen
* Created On: January 07, 2020
* Copyright: (c) Aquaveo 2020
********************************************************************************
"""
from .prepare_cropwat_demo import PrepareCropWatWorkflow  # noqa:F401, E501

HYDRAULICSTRUCTURES_WORKFLOWS = {
    PrepareCropWatWorkflow.TYPE: PrepareCropWatWorkflow,
}
