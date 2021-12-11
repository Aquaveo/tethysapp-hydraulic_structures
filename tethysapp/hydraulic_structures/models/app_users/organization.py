"""
********************************************************************************
* Name: organization.py
* Author: msouffront
* Created On: Nov 8, 2019
* Copyright: (c) Aquaveo 2019
********************************************************************************
"""
from tethysapp.hydraulic_structures.services.licenses import HydraulicStructuresLicenses
from tethysext.atcore.models.app_users import Organization

__all__ = ['HydraulicStructuresOrganization']


class HydraulicStructuresOrganization(Organization):
    """
    Customized Organization model for HYDRAULICSTRUCTURES.
    """
    TYPE = 'hydraulic_structures-organization'
    LICENSES = HydraulicStructuresLicenses()

    # Polymorphism
    __mapper_args__ = {
        'polymorphic_identity': TYPE,
    }
