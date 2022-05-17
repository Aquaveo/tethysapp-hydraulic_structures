import logging
from tethysext.atcore.services.resource_spatial_manager import ResourceSpatialManager

log = logging.getLogger(f'tethys.{__name__}')


class HydraulicStructureSpatialManager(ResourceSpatialManager):
    """Base SpatialManager class for Hydraulic Structures app with methods. Subclasses need to define WORKSPACE and URI properties."""  # noqa: E501
    def get_resource_extent_wms_url(self, resource):
        """
        Get url for map preview image.
        Returns:
            str: preview image url.
        """
        # Default image url
        layer_preview_url = None
        layer_name = f'{self.WORKSPACE}:{self.get_extent_layer_name(resource.id)}'
        try:
            extent = self.get_extent_for_project(datastore_name=self.DATASTORE,
                                                 resource_id=str(resource.id))

            # Calculate preview layer height and width ratios
            if extent:
                # Calculate image dimensions
                long_dif = abs(extent[0] - extent[2])
                lat_dif = abs(extent[1] - extent[3])
                hw_ratio = float(long_dif) / float(lat_dif)
                max_dim = 300

                if hw_ratio < 1:
                    width_resolution = int(hw_ratio * max_dim)
                    height_resolution = max_dim
                else:
                    height_resolution = int(max_dim / hw_ratio)
                    width_resolution = max_dim

                wms_endpoint = self.get_wms_endpoint()

                srid = resource.get_attribute('srid') or '4326'

                layer_preview_url = f'{wms_endpoint}?service=WMS&version=1.1.0&request=GetMap&layers={layer_name}' \
                                    f'&bbox={extent[0]},{extent[1]},{extent[2]},{extent[3]}&width={width_resolution}' \
                                    f'&height={height_resolution}&srs=EPSG:{srid}&format=image%2Fpng'
        except Exception:
            log.exception('An error occurred while trying to generate the preview image.')

        return layer_preview_url
