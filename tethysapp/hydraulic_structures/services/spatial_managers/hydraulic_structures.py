import os
from jinja2 import Template

from tethysext.atcore.services.resource_spatial_manager import ResourceSpatialManager

from .base import HydraulicInfrastructureSpatialManager, ProjectAreaSpatialManager

__all__ = ['HydraulicStructuresSpatialManager', 'HydraulicInfrastructureSpatialManager',
           'HydraulicStructuresProjectAreaSpatialManager', 'HealthInfrastructureSpatialManager']


class HydraulicStructuresSpatialManager(ResourceSpatialManager):
    WORKSPACE = 'hydraulic_structures'
    URI = 'http://app.aquaveo.com/hydraulic_structures'
    DATASTORE = 'hydraulic_structures_primary_db'

    GT_MULTI_POLYGON = 'MultiPolygon'

    def create_extent_layer(self, datastore_name, resource_id, geometry_type=None, srid=4326):
        """
        Creates a GeoServer SQLView Layer for the extent from the resource.

        Args:
            datastore_name(str): name of the PostGIS datastore in GeoServer that contains the layer data.
             For example: app_primary_db.
            resource_id(str): id of the Resources.
            geometry_type(str): type of geometry. Pick from: Polygon, LineString, Point.
            srid(str): Spatial Reference Identifier of the extent. Default to 4326.
        """
        geometry_check_list = [x.lower() for x in [self.GT_MULTI_POLYGON, self.GT_POLYGON, self.GT_LINE, self.GT_POINT]]
        if geometry_type is None:
            geometry_type = self.GT_POLYGON

        if geometry_type.lower() not in geometry_check_list:
            raise ValueError(f'{geometry_type} is an invalid geometry type. The type must be from one of the '
                             f'following: MultiPolygon, Polygon, LineString or Point')

        # Get Default Style Name
        default_style = 'polygon'

        # feature name
        feature_name = self.get_extent_layer_name(resource_id=resource_id)

        sql_context = {
            'resource_id': resource_id,
            'srid': srid,
        }

        # Render SQL
        sql_template_file = os.path.join(self.SQL_PATH, self.VL_EXTENT_VIEW + '.sql')
        with open(sql_template_file, 'r') as sql_template_file:
            text = sql_template_file.read()
            template = Template(text)
            sql = ' '.join(template.render(sql_context).split())

        # Create SQL View
        self.gs_api.create_layer(
            workspace=self.WORKSPACE,
            datastore_name=datastore_name,
            feature_name=feature_name,
            geometry_type=geometry_type,
            srid=srid,
            sql=sql,
            default_style=default_style,
        )


class HydraulicInfrastructureSpatialManager(HydraulicInfrastructureSpatialManager, HydraulicStructuresSpatialManager):
    pass


class HealthInfrastructureSpatialManager(HydraulicInfrastructureSpatialManager, HydraulicStructuresSpatialManager):
    pass


class HydraulicStructuresProjectAreaSpatialManager(ProjectAreaSpatialManager, HydraulicStructuresSpatialManager):
    pass
