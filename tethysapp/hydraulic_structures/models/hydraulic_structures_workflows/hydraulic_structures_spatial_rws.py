"""
********************************************************************************
* Name: hydraulic_structures_spatial_input_rws.py
* Author: msouffront
* Created On: May 17, 2022
* Copyright: (c) Aquaveo 2022
********************************************************************************
"""
import param
from tethysext.atcore.models.resource_workflow_steps import SpatialInputRWS


class HydraulicStructuresSpatialInputRWS(SpatialInputRWS):
    CONTROLLER = 'tethysapp.hydraulic_structures.controllers.workflows.hs_spatial_input_mwv.HydraulicStructuresSpatialInputMWV'
    TYPE = 'hydraulic_structures_spatial_input_workflow_step'

    __mapper_args__ = {
        'polymorphic_identity': TYPE
    }
