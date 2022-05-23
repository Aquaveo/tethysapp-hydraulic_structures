"""
********************************************************************************
* Name: modify_project_area.py
* Author: gagelarsen
* Created On: April 01, 2022
* Copyright: (c) Aquaveo 2022
********************************************************************************
"""
import logging
import os
import json
import zipfile
from geoserver.catalog import Catalog as GSCatalog
import geopandas as gpd
from shapely.geometry import shape, MultiPolygon

from tethysext.atcore.services.file_database import FileDatabaseClient
from tethysext.atcore.controllers.app_users import ModifyResource

from tethysapp.hydraulic_structures.services.spatial_managers.hydraulic_structures import HydraulicStructuresSpatialManager
from tethysapp.hydraulic_structures.app import HydraulicStructures as app

__all__ = ['ModifyProjectArea']
log = logging.getLogger(f'tethys.{__name__}')


class ModifyHydraulicStructures(ModifyResource):
    """
    Base Controller that handles the new and edit pages for resources.
    """
    # Srid field options
    include_srid = True
    srid_required = True
    srid_default = ""
    srid_error = "Referencia espacial requerida."

    # File upload options
    include_file_upload = True
    file_upload_required = True
    file_upload_multiple = False
    file_upload_accept = ".zip"
    file_upload_label = "Archivo Compreso (.zip)"
    file_upload_help = "Subir un archivo compreso (.zip) que incluya un shapefile."
    file_upload_error = "Debe proveer un archivo compreso."

    def handle_resource_finished_processing(self, session, request, request_app_user, resource, editing):
        """
        Hook to allow for post processing after the resource has finished being created or updated.
        Args:
            session(sqlalchemy.session): open sqlalchemy session.
            request(django.request): the Django request.
            request_app_user(AppUser): app user that is making the request.
            resource(Resource): The resource being edited or newly created.
            editing(bool): True if editing, False if creating a new resource.
        """
        if not editing:
            files = resource.get_attribute('files')
            file_dir = os.path.dirname(files[0])
            with zipfile.ZipFile(files[0], "r") as zip_ref:
                zip_ref.extractall(file_dir)
            # Remove zip file
            os.remove(files[0])

            # Get file database id
            file_database_id = app.get_custom_setting('file_database_id')

            # Store file in FileCollection
            file_database = FileDatabaseClient(session, app.get_file_database_root(), file_database_id)
            file_collection = file_database.new_collection(meta={'display_name': 'Archivos de Soporte'})

            # Get Spatial Manager
            gs_engine = app.get_spatial_dataset_service(app.GEOSERVER_NAME, as_engine=True)
            spatial_manager = HydraulicStructuresSpatialManager(gs_engine)

            # Get resource id
            resource_id = str(resource.id)

            for filename in os.listdir(file_dir):
                # Add all files and dirs to the file collection
                file_collection.add_item(os.path.join(file_dir, filename))

                if filename.endswith('.shp'):
                    shp_base = filename.replace('.shp', '')
                    shpfile_path = os.path.join(file_dir, filename)
                    json_path = os.path.join(file_dir, '__extent__.geojson')
                    shpfile = gpd.read_file(shpfile_path)
                    shpfile.to_file(json_path, driver='GeoJSON')

                    geometry_type = self.add_extent_to_db(json_path, resource)

                    # try:
                    #     # Create extent layer
                    #     feature_name = f'app_users_resources_extent_{resource_id}'
                    #     res = gs_engine.create_shapefile_resource(
                    #         store_id=f'{HydraulicStructuresSpatialManager.WORKSPACE}:{feature_name}',
                    #         shapefile_base=os.path.join(file_dir, shp_base),
                    #         overwrite=True
                    #     )

                    #     # update declared SRS and projection policy
                    #     gs_catalog = GSCatalog(
                    #         gs_engine.endpoint, username=gs_engine.username, password=gs_engine.password
                    #     )
                    #     shp_layer = gs_catalog.get_resource(
                    #         feature_name, workspace=HydraulicStructuresSpatialManager.WORKSPACE
                    #     )
                    #     shp_layer.projection = 'EPSG:4326'
                    #     shp_layer.projection_policy = 'REPROJECT_TO_DECLARED'
                    #     gs_catalog.save(shp_layer)

                    #     resource.set_attribute('gs_url', res['result']['wfs'])
                    # except Exception as e:
                    #     log.error(
                    #         f'The following error occurred while trying to add shapefile layer to geoserver: {e}'
                    #     )
                elif filename.endswith('.geojson') or filename.endswith('.json'):
                    json_path = os.path.join(file_dir, filename)
                    geometry_type = self.add_extent_to_db(json_path, resource)

            spatial_manager.create_extent_layer(
                datastore_name=spatial_manager.DATASTORE,
                resource_id=resource_id,
                geometry_type=geometry_type,
            )

            # Add bbox on geoserver
            gs_catalog = GSCatalog(
                gs_engine.endpoint, username=gs_engine.username, password=gs_engine.password
            )
            feature_name = f'app_users_resources_extent_{resource_id}'
            lyr_res = gs_catalog.get_resource(
                feature_name, workspace=spatial_manager.WORKSPACE
            )
            # DR bbox in xmin, xmax, ymin, ymax
            dr_bbox = ("-72.0045816157441", "-68.3231310096501", "17.4707186553058", "19.9322727546756", "EPSG:4326")
            lyr_res.native_bbox = dr_bbox
            lyr_res.latlon_bbox = dr_bbox
            gs_catalog.save(lyr_res)

            # Save wms endpoints to db
            extent_lyr = gs_engine.get_layer(feature_name, spatial_manager.DATASTORE)
            ows_endpoint = spatial_manager.gs_api.get_ows_endpoint(spatial_manager.WORKSPACE)
            geojson_url = f'{ows_endpoint}?service=WFS&version=1.0.0&request=GetFeature&typeName= \
                            {spatial_manager.WORKSPACE}:{feature_name}&maxFeatures=50&outputFormat=application%2Fjson'
            resource.set_attribute('gs_url', {
                'wms': extent_lyr['result']['wms'],
                'wfs': {'geojson': geojson_url}
            })

            # Associate file_collection with resource
            resource.file_collections.append(file_collection.instance)

            resource.set_status('create_extent_layer', 'Success')
            session.commit()
            session.close()

            log.info('Layer uploaded.')

    def handle_srid_changed(self, session, request, request_app_user, resource, old_srid, new_srid):
        """
        Handle srid changed event when editing an existing resource.
        Args:
            session(sqlalchemy.session): open sqlalchemy session.
            request(django.request): the Django request.
            request_app_user(AppUser): app user that is making the request.
            resource(Resource): The resource being edited.
            old_srid(str): The old srid.
            new_srid(str): The new srid.
        """
        resource.update_extent_srid(new_srid)

    @staticmethod
    def add_extent_to_db(file_path, resource):
        with open(file_path, 'r') as geojson_file:
            geojson_data = json.load(geojson_file)
            # Use the first feature as extent.
            features = geojson_data['features']

            if "project_area" in resource.type:
                polygon_list = []
                property_list = []
                for feature in features:
                    property_list.append(feature['properties'])
                    if feature['geometry']['type'] == 'Polygon':
                        polygon_list.append(shape(feature['geometry'], ))
                    elif feature['geometry']['type'] == 'MultiPolygon':
                        for polygon in shape(feature['geometry']):
                            polygon_list.append(polygon)
                multi_polygon = MultiPolygon(polygon_list)

                resource.set_attribute('area_properties', property_list)
                srid = resource.get_attribute('srid')
                resource.set_extent(obj=multi_polygon.wkt, object_format='wkt', srid=srid)
                return 'MultiPolygon'

            elif any(type in resource.type for type in ["hydraulic_infrastructure", "health_infrastructure"]):
                srid = resource.get_attribute('srid')
                resource.set_extent(obj=features[0]['geometry'], object_format='dict', srid=srid)
                return features[0]['geometry']['type']
