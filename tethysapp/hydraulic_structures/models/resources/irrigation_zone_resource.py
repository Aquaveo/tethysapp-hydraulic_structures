"""
********************************************************************************
* Name: irrigation_zone_resource.py
* Author: glarsen
* Created On: November 23, 2020
* Copyright: (c) Aquaveo 2020
********************************************************************************
"""
from sqlalchemy.orm import backref, relationship

from tethysext.atcore.models.app_users import SpatialResource
from tethysext.atcore.models.file_database import FileCollection, resource_file_collection_association
from tethysext.atcore.mixins.file_collection_mixin import FileCollectionMixin


class HydraulicStructuresIrrigationZoneResource(SpatialResource, FileCollectionMixin):
    # Resource Types
    TYPE = 'irrigation_zone_resource'
    DISPLAY_TYPE_SINGULAR = 'Irrigation Zone'
    DISPLAY_TYPE_PLURAL = 'Irrigation Zones'

    file_collections = relationship(FileCollection, secondary=resource_file_collection_association,
                                    backref=backref('irrigation_zone', uselist=False))

    models = relationship(
        'HydraulicStructuresModelResource',
        primaryjoin='or_('
                    'func.ST_Contains(foreign(HydraulicStructuresIrrigationZoneResource.extent), '
                    'remote(HydraulicStructuresModelResource.extent)).as_comparison(1, 2)'
                    ','
                    'func.ST_CoveredBy(foreign(HydraulicStructuresIrrigationZoneResource.extent), '
                    'remote(HydraulicStructuresModelResource.extent)).as_comparison(1, 2)'
                    ','
                    'func.ST_Overlaps(foreign(HydraulicStructuresIrrigationZoneResource.extent), '
                    'remote(HydraulicStructuresModelResource.extent)).as_comparison(1, 2)'
                    ')',
        backref=backref('model_irrigation_zones', uselist=True),
        viewonly=True,
        uselist=True,
        sync_backref=False
    )
    datasets = relationship(
        'HydraulicStructuresDatasetResource',
        primaryjoin='or_('
                    'func.ST_Contains(foreign(HydraulicStructuresIrrigationZoneResource.extent), '
                    'remote(HydraulicStructuresDatasetResource.extent)).as_comparison(1, 2)'
                    ','
                    'func.ST_CoveredBy(foreign(HydraulicStructuresIrrigationZoneResource.extent), '
                    'remote(HydraulicStructuresDatasetResource.extent)).as_comparison(1, 2)'
                    ','
                    'func.ST_Overlaps(foreign(HydraulicStructuresIrrigationZoneResource.extent), '
                    'remote(HydraulicStructuresDatasetResource.extent)).as_comparison(1, 2)'
                    ')',
        backref=backref('dataset_irrigation_zones', uselist=True),
        viewonly=True,
        uselist=True,
        sync_backref=False
    )

    # Polymorphism
    __mapper_args__ = {
        'polymorphic_identity': TYPE,
    }
