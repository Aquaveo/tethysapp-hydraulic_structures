"""
********************************************************************************
* Name: hydraulic_infrastructure_resource.py
* Author: glarsen
* Created On: November 18, 2020
* Copyright: (c) Aquaveo 2020
********************************************************************************
"""
from sqlalchemy.orm import backref, relationship

from tethysext.atcore.models.app_users import SpatialResource
from tethysext.atcore.models.file_database import FileCollection, resource_file_collection_association
from tethysext.atcore.mixins.file_collection_mixin import FileCollectionMixin


class HydraulicStructuresHydraulicInfrastructureResource(SpatialResource, FileCollectionMixin):
    # Resource Types
    TYPE = 'hydraulic_structures_hydraulic_infrastructure_resource'
    DISPLAY_TYPE_SINGULAR = 'Hydraulic Infrastructure'
    DISPLAY_TYPE_PLURAL = 'Hydraulic Infrastructures'

    file_collections = relationship(FileCollection, secondary=resource_file_collection_association,
                                    backref=backref('hydraulic_structures_hydraulic_infrastructure', uselist=False))

    # Polymorphism
    __mapper_args__ = {
        'polymorphic_identity': TYPE,
    }
