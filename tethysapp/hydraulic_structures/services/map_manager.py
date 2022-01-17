"""
********************************************************************************
* Name: map_manager
* Author: msouffront
* Created On: Nov 11, 2019
* Copyright: (c) Aquaveo 2019
********************************************************************************
"""
import logging

from django.contrib import messages
from tethys_sdk.gizmos import MapView, MVView

from tethysext.atcore.services.map_manager import MapManagerBase
from tethysapp.hydraulic_structures.models.resources import HydraulicStructuresProjectAreaResource, HealthInfrastructureResource, HydraulicInfrastructureResource
from tethysapp.hydraulic_structures.services.spatial_managers.hydraulic_structures import HydraulicStructuresSpatialManager
from tethysapp.hydraulic_structures.app import HydraulicStructures as app


log = logging.getLogger(f'tethys.{__name__}')


class HydraulicStructuresMapManager(MapManagerBase):
    def get_cesium_token(self):
        return app.get_custom_setting('cesium_api_token')

    def get_map_extent(self):
        """
        Get the default view and extent for the project.

        Returns:
            MVView, 4-list<float>: default view and extent of the project.
        """
        extent = [-76.041715, 16.172473, -67.202809, 22.065278]

        # Compute center
        center = self.DEFAULT_CENTER
        if extent and len(extent) >= 4:
            center_x = (extent[0] + extent[2]) / 2.0
            center_y = (extent[1] + extent[3]) / 2.0
            center = [center_x, center_y]

        # Construct the default view
        view = MVView(
            projection='EPSG:4326',
            center=center,
            zoom=self.DEFAULT_ZOOM,
            maxZoom=self.MAX_ZOOM,
            minZoom=self.MIN_ZOOM
        )

        return view, extent

    def compose_map(self, request, resource_id=None, *args, **kwargs):
        session = None
        map_layers = []
        layer_groups = []
        base_extents = [-76.041715, 16.172473, -67.202809, 22.065278]

        # Initialize empty MapView to use if an error occurs
        map_view = MapView(
            height='600px',
            width='100%',
            controls=['ZoomSlider', 'Rotate', 'FullScreen'],
            layers=[],
            view=MVView(
                projection='EPSG:4326',
                center=self.DEFAULT_CENTER,
                zoom=13,
                maxZoom=28,
                minZoom=4,
            ),
            basemap=[
                'Stamen',
                {'Stamen': {'layer': 'toner', 'control_label': 'Black and White'}},
                'OpenStreetMap',
                'ESRI',
            ],
            legend=True
        )

        try:
            Session = app.get_persistent_store_database('primary_db', as_sessionmaker=True)
            session = Session()

            # If resource_id is given, compose map creates a ste mission model view for specific model
            if resource_id:
                project_area = session.query(HydraulicStructuresProjectAreaResource).get(resource_id)
                project_area_layer = self.build_boundary_layer_for_resource(
                    project_area, layer_variable='project_area'
                )
                map_layers.append(project_area_layer)

                layer_groups.append(
                    self.build_layer_group(
                        id='project_area_layers',
                        display_name='Project Area',
                        layers=[project_area_layer],
                        layer_control='checkbox',
                        visible=True,
                    )
                )

                base_extents = project_area_layer.legend_extent

            # If no resource_id, compose map of all mission boundaries with health_infrastructures and hydraulic_infrastructures
            else:
                project_area_layers = []
                health_infrastructure_layers = []
                hydraulic_infrastructure_layers = []

                # Build irrigation zone layers
                project_areas = session.query(HydraulicStructuresProjectAreaResource) \
                    .filter(HydraulicStructuresProjectAreaResource.extent is not None) \
                    .all()
                for project_area in project_areas:
                    project_area_layer = self.build_boundary_layer_for_resource(
                        project_area, layer_variable='project_area', selectable=True
                    )
                    if project_area_layer is not None:
                        project_area_layers.append(project_area_layer)

                map_layers.extend(project_area_layers)

                # Build health_infrastructure layers
                health_infrastructures = session.query(HealthInfrastructureResource) \
                    .filter(HealthInfrastructureResource.extent is not None) \
                    .all()
                for health_infrastructure in health_infrastructures:
                    health_infrastructure_layer = self.build_boundary_layer_for_resource(
                        health_infrastructure, layer_variable='health_infrastructure_resource', selectable=False
                    )
                    if health_infrastructure_layer is not None:
                        health_infrastructure_layers.append(health_infrastructure_layer)

                map_layers.extend(health_infrastructure_layers)

                # Build hydraulic_infrastructure layers
                hydraulic_infrastructures = session.query(HydraulicInfrastructureResource) \
                    .filter(HydraulicInfrastructureResource.extent is not None) \
                    .all()
                for hydraulic_infrastructure in hydraulic_infrastructures:
                    hydraulic_infrastructure_layer = self.build_boundary_layer_for_resource(
                        hydraulic_infrastructure, layer_variable='hydraulic_infrastructure_resource', selectable=False
                    )
                    if hydraulic_infrastructure_layer is not None:
                        hydraulic_infrastructure_layers.append(hydraulic_infrastructure_layer)

                map_layers.extend(hydraulic_infrastructure_layers)

                # Make Layer Groups
                layer_groups.extend([
                    self.build_layer_group(
                        id='project_area_layers',
                        display_name='Project Areas',
                        layers=project_area_layers,
                        layer_control='checkbox',
                        visible=True,
                    ),
                    self.build_layer_group(
                        id='health_infrastructure_layers',
                        display_name='Health Infrastructures',
                        layers=health_infrastructure_layers,
                        layer_control='checkbox',
                        visible=False,
                    ),
                    self.build_layer_group(
                        id='hydraulic_infrastructure_layers',
                        display_name='Hydraulic Infrastructures',
                        layers=hydraulic_infrastructure_layers,
                        layer_control='checkbox',
                        visible=False,
                    ),
                ])

            # Add layers to the MapView
            map_view.layers.extend(map_layers)

        except Exception:
            log.exception('An unexpected error has occurred.')
            messages.error(request, "We're sorry, but an unexpected error has occurred.")
        finally:
            session and session.close()

        return map_view, base_extents, layer_groups

    def build_boundary_layer_for_resource(self, resource, layer_variable="", selectable=False):
        """
        Build the boundary MVLayer object for the given resource.

        Args:
            resource (SpatialResource): the Resource.
            layer_variable (str): the type/class of the layer (e.g.: project_area).
            selectable (bool): Make feature selectable with "Load" pop-up when True.

        Returns:
            MVLayer: the boundary layer.
        """
        extents_geometry = resource.get_extent(extent_type='dict')
        if extents_geometry is None:
            return None

        geojson = {
            'type': 'FeatureCollection',
            'name': resource.name,
            'properties': {},
            'crs': {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:OGC:1.3:CRS84'}},
            'features': [{
                'type': 'Feature',
                'properties': {},
                'geometry': extents_geometry
            }]
        }

        # Compute bbox
        bbox = self.compute_bbox_for_extent(extents_geometry)
        layer_id = str(resource.id)
        layer_name = layer_id
        layer = self.build_geojson_layer(
            geojson=geojson,
            layer_name=layer_name,
            layer_title=resource.name,
            layer_variable=layer_variable,
            layer_id=layer_id,
            selectable=selectable,
            has_action=selectable,
            popup_title=resource.name if selectable else None,
            extent=bbox,
        )
        return layer

    def compute_bbox_for_extent(self, polygon):
        """
        Compute BBOX from GeoJSON Polygon.

        Args:
            polygon (dict): Polygon feature represented as dictionary GeoJSON equivalent.
        returns:
            4-list: bbox [min_x, min_y, max_x, max_y]
        """
        min_x = None
        min_y = None
        max_x = None
        max_y = None

        if polygon.get('type') != 'Polygon':
            return None

        for lat, lon in polygon.get('coordinates')[0]:
            min_x = lat if min_x is None or lat < min_x else min_x
            min_y = lon if min_y is None or lon < min_y else min_y
            max_x = lat if max_x is None or lat > max_x else max_x
            max_y = lon if max_y is None or lon > max_y else max_y
        return [min_x, min_y, max_x, max_y]

    def get_vector_style_map(self):
        """
        Builds the style map for vector layers.

        Returns:
            dict: the style map.
        """
        color = 'red'
        style_map = {
            'Point': {'ol.style.Style': {
                'image': {'ol.style.Circle': {
                    'radius': 5,
                    'fill': {'ol.style.Fill': {
                        'color': color,
                    }},
                    'stroke': {'ol.style.Stroke': {
                        'color': color,
                    }}
                }}
            }},
            'LineString': {'ol.style.Style': {
                'stroke': {'ol.style.Stroke': {
                    'color': color,
                    'width': 2
                }}
            }},
            'Polygon': {'ol.style.Style': {
                'stroke': {'ol.style.Stroke': {
                    'color': color,
                    'width': 2
                }},
                'fill': {'ol.style.Fill': {
                    'color': 'rgba(255, 0, 0, 0.1)'
                }}
            }},
        }

        return style_map

    def compose_raster_layer(self, endpoint, layer, public_name, public=False, extent=None, visible=True,
                             color_ramp_division_kwargs=None):
        """
        Compose layer object.

        Args:
            endpoint (str): URL of geoserver wms service.
            layer (str): geoserver name of layer.
            public_name (str): Human readable name of layer.
            public (bool): Layer will be public if True. Defaults to False.
            extent (list, optional): 4-list of bounding box extents.
            visible (bool): Initial visibility of layer. Visible if True. Defaults to True.
            color_ramp_division_kwargs (dict): arguments from map_manager.generate_custom_color_ramp_divisions
        Returns:
            MVLayer: layer object.
        """
        def replace_colon(text):
            if ":" in text:
                text = text.replace(":", "_")
            return text

        # Compose layer
        mv_layer = self.build_wms_layer(
            endpoint=endpoint,
            layer_name=layer,
            layer_title=public_name,
            layer_variable=replace_colon(layer),
            extent=extent,
            visible=visible,
            public=public,
            color_ramp_division_kwargs=dict() if color_ramp_division_kwargs is None else color_ramp_division_kwargs
        )

        return mv_layer
