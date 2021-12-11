import os

import django
from sqlalchemy.exc import StatementError
from tethys_apps.exceptions import TethysAppSettingNotAssigned
from tethys_dataset_services.engines import GeoServerSpatialDatasetEngine

from tethysext.atcore.utilities import parse_url
from tethysext.atcore.services.file_database import FileDatabaseClient
from tethysext.atcore.cli.cli_helpers import print_header, print_success, print_info, print_error
from tethysext.atcore.exceptions import FileDatabaseNotFoundError, UnboundFileDatabaseError
from tethysapp.hydraulic_structures.services.spatial_managers.hydraulic_structures import HydraulicStructuresSpatialManager

RESOURCES = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'resources')


def init_hydraulic_structures(arguments):
    """
    Commandline interface for initializing the hydraulic_structures app.
    """
    os.environ['DJANGO_SETTINGS_MODULE'] = 'tethys_portal.settings'
    django.setup()

    from tethysapp.hydraulic_structures.app import HydraulicStructures as app
    from tethys_sdk.app_settings import CustomSetting

    fdb_errors_occurred = False
    gs_errors_occurred = False

    print_header('Initializing HYDRAULICSTRUCTURES...')

    # Initialize file database
    print_info('Initializing HYDRAULICSTRUCTURES File Database...')

    Session = app.get_persistent_store_database(app.DATABASE_NAME, as_sessionmaker=True)
    session = Session()

    # Setup root directory
    file_database_root = app.get_file_database_root()
    if not os.path.exists(file_database_root):
        os.makedirs(file_database_root)

    try:
        fdb_name = app.FILE_DATABASE_ID_NAME
        fdb_id = app.get_custom_setting(name=fdb_name)
        if fdb_id is None:
            raise TethysAppSettingNotAssigned

        fdb_instance = FileDatabaseClient(session, file_database_root, fdb_id).instance
        if fdb_instance:
            print_info(f'Using existing File Database with ID: {fdb_id}.')
    except TethysAppSettingNotAssigned:
        print_info('Creating new HYDRAULICSTRUCTURES File Database.')
        fdb_new_instance = FileDatabaseClient.new(session, file_database_root).instance
        fdb_id = fdb_new_instance.id

        print_info(f'Assigning File Database ID: {fdb_id} to {fdb_name} custom setting.')
        custom_app_setting = CustomSetting.objects.get(name=fdb_name, tethys_app__package='hydraulic_structures')
        custom_app_setting.value = fdb_id
        custom_app_setting.save()

        print_info(f'File Database with ID: {fdb_id} created successfully!')
    except (UnboundFileDatabaseError, FileDatabaseNotFoundError):
        fdb_errors_occurred = True
        print_error(f'No File Database with ID: {fdb_id} was found.')
    except StatementError:
        fdb_errors_occurred = True
        print_error('The file database ID must be a hexadecimal UUID string.')

    # Initialize workspace
    print_info('Initializing HYDRAULICSTRUCTURES GeoServer Workspace...')
    url = parse_url(arguments.gsurl)

    geoserver_engine = GeoServerSpatialDatasetEngine(
        endpoint=url.endpoint,
        username=url.username,
        password=url.password
    )

    spatial_manager = HydraulicStructuresSpatialManager(geoserver_engine)
    gs_api = spatial_manager.gs_api
    workspace_exists = geoserver_engine.get_workspace(HydraulicStructuresSpatialManager.WORKSPACE)['success']
    if workspace_exists:
        print_info(f'The "{HydraulicStructuresSpatialManager.WORKSPACE}" GeoServer workspace has already been initialized.')
    else:
        try:
            spatial_manager.create_workspace()
            print_success('Successfully initialized HYDRAULICSTRUCTURES GeoServer workspace.')
        except Exception as e:
            gs_errors_occurred = True
            print_error(f'An error occurred during workspace creation: {e}')

    # Initialize geoserver store from hydraulic_structures database
    db_url = app.get_persistent_store_database(app.DATABASE_NAME, as_url=True)
    available_gs_stores = spatial_manager.gs_engine.list_stores(HydraulicStructuresSpatialManager.WORKSPACE)['result']
    if db_url.database not in available_gs_stores:
        try:
            gs_api.create_postgis_store(
                workspace=HydraulicStructuresSpatialManager.WORKSPACE,
                name=db_url.database,
                db_host=db_url.host,
                db_port=db_url.port,
                db_name=db_url.database,
                db_username=db_url.username,
                db_password=db_url.password
            )
        except Exception as e:
            gs_errors_occurred = True
            print_error(f'An error occurred during postgis store creation: {e}')

    if not fdb_errors_occurred and not gs_errors_occurred:
        print_success('Successfully initialized HYDRAULICSTRUCTURES.')
