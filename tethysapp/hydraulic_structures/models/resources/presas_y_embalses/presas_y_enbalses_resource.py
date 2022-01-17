from sqlalchemy.orm import backref, relationship
from tethysext.atcore.models.file_database import resource_file_collection_association
from tethysext.atcore.models.file_database.file_collection import FileCollection
from hydraulic_infrastructure_resource import HydraulicInfrastructureResource

class PresasYEmbalses (HydraulicInfrastructureResource):
    TYPE = 'Presas Y Embalses'

    DISPLAY_TYPE_SINGULAR = 'Presa Y Embalse'
    DISPLAY_TYPE_PLURAL = 'Presas Y Embalses'

    file_collections = relationship(FileCollection, secondary=resource_file_collection_association,
                                    backref=backref('presas_y_embalses', uselist=False))

    # Polymorphism
    __mapper_args__ = {
        'polymorphic_identity': TYPE,
    }