"""
********************************************************************************
* Name: hydraulic_infrastructure_resource.py
* Author: msouffront
* Created On: April 18, 2022
* Copyright: (c) Aquaveo 2022
********************************************************************************
"""
from django.utils.decorators import classproperty
from sqlalchemy.orm import backref, relationship

from tethysext.atcore.models.app_users import SpatialResource
from tethysext.atcore.models.file_database import FileCollection, resource_file_collection_association
from tethysext.atcore.mixins.file_collection_mixin import FileCollectionMixin


class HydraulicInfrastructureResource(SpatialResource, FileCollectionMixin):
    # Resource Types
    TYPE = 'hydraulic_infrastructure_resource'
    DISPLAY_TYPE_SINGULAR = 'Estructura Hidráulica'
    DISPLAY_TYPE_PLURAL = 'Estructuras Hidráulicas'

    file_collections = relationship(FileCollection, secondary=resource_file_collection_association,
                                    backref=backref('hydraulic_infrastructure', uselist=False))

    # Polymorphism
    __mapper_args__ = {
        'polymorphic_identity': TYPE,
    }

    @classproperty
    def SLUG(self):
        return 'hydraulic_infrastructures'
