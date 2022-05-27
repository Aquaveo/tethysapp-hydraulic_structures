"""
********************************************************************************
* Name: hydraulic_infrastructure_summary_tab.py
* Author: msouffront, htran
* Created On: April 23, 2022
* Copyright: (c) Aquaveo 2022
********************************************************************************
"""
import os
from tethysext.atcore.controllers.resources import ResourceSummaryTab
from tethysext.atcore.services.file_database import FileDatabaseClient
from tethysext.atcore.mixins.file_collection_controller_mixin import FileCollectionsControllerMixin

from tethysapp.hydraulic_structures.services.spatial_managers.hydraulic_structures import HydraulicInfrastructureSpatialManager
from tethysapp.hydraulic_structures.services.map_manager import HydraulicStructuresMapManager


class HydraulicInfrastructureSummaryTab(ResourceSummaryTab, FileCollectionsControllerMixin):
    has_preview_image = True
    preview_image_title = "Cobertura"

    def get_map_manager(self):
        return HydraulicStructuresMapManager

    def get_spatial_manager(self):
        return HydraulicInfrastructureSpatialManager

    def get_summary_tab_info(self, request, session, resource, *args, **kwargs):
        """
        Define GSSHA specific summary info.
        """
        # Tab layout
        column1 = []  # Auto-populated with default extent and description
        column2 = []

        tab_content = [column1, column2]
        # Generate details about file collections and add to column 2
        fc_details = self.get_file_collections_details(session, resource)
        column2.extend(fc_details)

        properties = ("", {'Propiedades': resource.get_attribute('area_properties')})
        column2.append(properties)

        return tab_content

    def get_file_collections_details(self, session, resource):
        """
        Build summary details for each FileCollection associated with the given resource.

        Args:
            session (Session): the SQLAlchemy session.
            resource (Resource): a Resource with a file_collections relationship property.

        Returns:
            list: a list of summary details table tuples, one for each FileCollection.
        """
        all_details = []
        file_collections = resource.file_collections
        app = self.get_app()

        for file_collection in file_collections:
            file_database_id = app.get_custom_setting(app.FILE_DATABASE_ID_NAME)
            file_database = FileDatabaseClient(session, app.get_file_database_root(), file_database_id)
            file_collection_client = file_database.get_collection(file_collection.id)

            file_count = -1
            total_size = 0
            # Get file count and total size
            for relative_root, dirs, files in file_collection_client.walk():
                file_count += len(files)

                for file in files:
                    file_path = os.path.join(file_collection_client.path, relative_root, file)
                    total_size += os.path.getsize(file_path)

            # Make total size human readable
            for unit in ['Bytes', 'KB', 'MB', 'GB', 'TB']:
                if total_size < 1024:
                    break
                total_size /= 1024.0
            total_size = f"{total_size:.2f} {unit}"

            # Create file collection details tuple
            file_collection_details = ('Detalles de Colección de Archivos', {
                'ID': file_collection.id,
                'Cantidad de Archivos': file_count,
                'Espacio Total': total_size,
            })

            # # Append meta dict
            # file_collection_details[1].update(file_collection.meta)

            all_details.append(file_collection_details)

        return all_details

    def get_preview_image_url(self, request, resource, *args, **kwargs):
        """
        Get URL from GeoServer that will generate a PNG of the default layers.
        """

        gs_engine = self.get_app().get_spatial_dataset_service(self.get_app().GEOSERVER_NAME, as_engine=True)
        spatial_manager = self.get_spatial_manager()(geoserver_engine=gs_engine)
        layer_preview_url = spatial_manager.get_resource_extent_wms_url(resource=resource)

        return layer_preview_url

    def get_context(self, request, session, resource, context, *args, **kwargs):
        """
        Build context for the ProjectAreaSummaryTab template that is used to generate the tab content.
        """
        if self.has_preview_image:
            context['has_preview_image'] = self.has_preview_image
            context['preview_image_title'] = self.preview_image_title

        general_summary_tab_info = (
            'Descripción',
            {
                'Nombre': resource.name,
                'Descripción': resource.description,
                'Creado Por': 'staff' if resource.created_by == '_staff_user' else resource.created_by,
                'Fecha Creado': resource.date_created
            }
        )

        # Add general_summary_tab_info as first item in first columns
        summary_tab_info = self.get_summary_tab_info(request, session, resource)
        if len(summary_tab_info) == 0:
            summary_tab_info = [[general_summary_tab_info]]
        else:
            summary_tab_info[0].insert(0, general_summary_tab_info)

        # Debug Section
        if request.user.is_staff:
            debug_atts = {'SRID': resource.attributes['srid'], 'Locked': resource.is_user_locked}

            if resource.is_user_locked:
                debug_atts['Locked By'] = 'All Users' if resource.is_locked_for_all_users else resource.user_lock
            else:
                debug_atts['Locked By'] = 'N/A'

            debug_summary_tab_info = ('Debug Info', debug_atts)
            summary_tab_info[-1].append(debug_summary_tab_info)

        context['columns'] = summary_tab_info

        return context
