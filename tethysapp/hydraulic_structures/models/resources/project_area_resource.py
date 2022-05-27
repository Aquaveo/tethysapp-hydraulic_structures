"""
********************************************************************************
* Name: project_area_resource.py
* Author: msouffront
* Created On: April 23, 2022
* Copyright: (c) Aquaveo 2022
********************************************************************************
"""
from django.utils.decorators import classproperty

from sqlalchemy.orm import backref, relationship

from tethysext.atcore.models.app_users import SpatialResource
from tethysext.atcore.models.file_database import FileCollection, resource_file_collection_association
from tethysext.atcore.mixins.file_collection_mixin import FileCollectionMixin


class HydraulicStructuresProjectAreaResource(SpatialResource, FileCollectionMixin):
    # Resource Types
    TYPE = 'project_area_resource'
    DISPLAY_TYPE_SINGULAR = 'Área de División'
    DISPLAY_TYPE_PLURAL = 'Áreas de División'

    file_collections = relationship(FileCollection, secondary=resource_file_collection_association,
                                    backref=backref('project_area', uselist=False))

    # Polymorphism
    __mapper_args__ = {
        'polymorphic_identity': TYPE,
    }

    @classproperty
    def SLUG(self):
        return 'project_areas'
