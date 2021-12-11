
from tethysext.atcore.controllers.resources.tabs.files_tab import ResourceFilesTab
from tethysext.atcore.services.file_database import FileDatabaseClient

from tethysapp.hydraulic_structures.app import HydraulicStructures as app


class IrrigationZoneFilesTab(ResourceFilesTab):
    def get_file_collections(self, request, resource, session, *args, **kwargs):
        """
        Get the file_collections

        Returns:
            A list of FileCollection clients.
        """
        file_collections = []
        for file_collection in resource.file_collections:
            file_database_id = app.get_custom_setting('file_database_id')
            file_database = FileDatabaseClient(session, app.get_file_database_root(), file_database_id)
            file_collections.append(file_database.get_collection(file_collection.id))

        return file_collections
