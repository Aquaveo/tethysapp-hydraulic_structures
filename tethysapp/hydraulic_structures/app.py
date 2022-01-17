import os
import sys
from pathlib import Path

from tethys_apps.models import SpatialDatasetServiceSetting
from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import PersistentStoreDatabaseSetting, CustomSetting


class HydraulicStructures(TethysAppBase):
    """
    Tethys app class for HydraulicStructures.
    """

    name = 'Hydraulic Structures'
    index = 'hydraulic_structures:home'
    icon = 'hydraulic_structures/images/icon.gif'
    package = 'hydraulic_structures'
    root_url = 'hydraulic-structures'
    color = '#d35400'
    description = 'Storing Hydraulic Structures Data'
    tags = '"Hydraulic Structures", "Hydraulic"'
    enable_feedback = False
    feedback_emails = []

    # services
    SCHEDULER_NAME = 'remote_cluster'
    GEOSERVER_NAME = 'primary_geoserver'
    DATABASE_NAME = 'primary_db'
    FILE_DATABASE_ID_NAME = 'file_database_id'
    LINUX_CONDOR_FDB_ROOT_NAME = 'linux_condor_fdb_root'
    WINDOWS_CONDOR_FDB_ROOT_NAME = 'windows_condor_fdb_root'
    FILE_DATABASE_ROOT = os.path.join(os.path.dirname(__file__), 'workspaces', 'app_workspace', 'file_databases')

    def custom_settings(self):
        """
        Example custom_settings method.
        """
        custom_settings = (
            CustomSetting(
                name=self.FILE_DATABASE_ID_NAME,
                type=CustomSetting.TYPE_STRING,
                description='File Database ID',
                required=True
            ),
            CustomSetting(
                name=self.LINUX_CONDOR_FDB_ROOT_NAME,
                type=CustomSetting.TYPE_STRING,
                description='The File Database root directory for the Linux condor worker.',
                required=False
            ),
            CustomSetting(
                name='cesium_api_token',
                type=CustomSetting.TYPE_STRING,
                description='Cesium API Token',
                required=True
            ),
        )
        return custom_settings

    def persistent_store_settings(self):
        """
        Define persistent store settings.
        """
        ps_settings = (
            PersistentStoreDatabaseSetting(
                name='primary_db',
                description='Primary database for HYDRAULICSTRUCTURES.',
                initializer='hydraulic_structures.models.init_primary_db',
                required=True,
                spatial=True,
            ),
        )

        return ps_settings

    def spatial_dataset_service_settings(self):
        """
        Define spatial dataset services settings.
        """
        sds_settings = (
            SpatialDatasetServiceSetting(
                name=self.GEOSERVER_NAME,
                description='GeoServer used to host spatial visualizations for the app.',
                engine=SpatialDatasetServiceSetting.GEOSERVER,
                required=True
            ),
        )
        return sds_settings

    def url_maps(self):
        """
        Add controllers
        """
        from tethysext.atcore.urls import app_users, spatial_reference, resource_workflows, resources
        from tethysapp.hydraulic_structures.services.spatial_managers.hydraulic_structures import\
            HydraulicStructuresSpatialManager
        from tethysapp.hydraulic_structures.models.resources.project_area_resource import\
            HydraulicStructuresProjectAreaResource
        from tethysapp.hydraulic_structures.models.resources.hydraulic_infrastructure_resource import HydraulicInfrastructureResource
        from tethysapp.hydraulic_structures.models.resources.health_infrastructure_resource import HealthInfrastructureResource
        from tethysapp.hydraulic_structures.models.app_users import HydraulicStructuresOrganization
        from tethysapp.hydraulic_structures.models.hydraulic_structures_workflows import HYDRAULICSTRUCTURES_WORKFLOWS

        from tethysapp.hydraulic_structures.controllers.project_areas import ModifyProjectArea,\
            ManageProjectAreas, ProjectAreaDetails
        from tethysapp.hydraulic_structures.controllers.map_view.hydraulic_structures_model_map_view import\
            HydraulicStructuresModelMapView
        from tethysapp.hydraulic_structures.controllers.hydraulic_infrastructures import ManageHydraulicInfrastructureResources,\
            ModifyHydraulicInfrastructureResource, HydraulicInfrastructureResourceDetails
        from tethysapp.hydraulic_structures.controllers.health_infrastructures import ManageHealthInfrastructureResources,\
            HealthInfrastructureResourceDetails, ModifyHealthInfrastructureResource
        from tethysapp.hydraulic_structures.controllers.workflows.hydraulic_structures_workflow_view import HydraulicStructuresWorkflowRouter
        from tethysapp.hydraulic_structures.services.map_manager import HydraulicStructuresMapManager

        UrlMap = url_map_maker(self.root_url)

        url_maps = []

        app_users_urls = app_users.urls(
            url_map_maker=UrlMap,
            app=self,
            persistent_store_name='primary_db',
            base_template='hydraulic_structures/base.html',
            custom_models=(
                HydraulicStructuresProjectAreaResource,
                HydraulicStructuresOrganization,
            ),
            custom_controllers=(
                ManageProjectAreas,
                ModifyProjectArea,
            )
        )
        url_maps.extend(app_users_urls)

        hydraulic_infrastructure_resources_urls = resources.urls(
            url_map_maker=UrlMap,
            app=self,
            persistent_store_name='primary_db',
            base_template='hydraulic_structures/base.html',
            custom_models=(
                HydraulicInfrastructureResource,
            ),
            custom_controllers=(
                ManageHydraulicInfrastructureResources,
                ModifyHydraulicInfrastructureResource,
            )
        )
        url_maps.extend(hydraulic_infrastructure_resources_urls)

        model_resources_urls = resources.urls(
            url_map_maker=UrlMap,
            app=self,
            persistent_store_name='primary_db',
            base_template='hydraulic_structures/base.html',
            custom_models=(
                HealthInfrastructureResource,
            ),
            custom_controllers=(
                ManageHealthInfrastructureResources,
                ModifyHealthInfrastructureResource,
            )
        )
        url_maps.extend(model_resources_urls)

        spatial_reference_urls = spatial_reference.urls(
            url_map_maker=UrlMap,
            app=self,
            persistent_store_name='primary_db'
        )
        url_maps.extend(spatial_reference_urls)

        url_maps.extend((
            UrlMap(
                name='project_area_details_tab',
                url='hydraulic_structures/project_areas/{resource_id}/details/{tab_slug}',
                controller=ProjectAreaDetails.as_controller(
                    _app=self,
                    _persistent_store_name='primary_db',
                    _Organization=HydraulicStructuresOrganization,
                    _Resource=HydraulicStructuresProjectAreaResource
                ),
                regex=['[0-9A-Za-z-_.]+', '[0-9A-Za-z-_.{}]+']
            ),
        ))

        url_maps.extend((
            UrlMap(
                name='hydraulic_infrastructure_details_tab',
                url='hydraulic_structures/hydraulic_infrastructures/{resource_id}/details/{tab_slug}',
                controller=HydraulicInfrastructureResourceDetails.as_controller(
                    _app=self,
                    _persistent_store_name='primary_db',
                    _Organization=HydraulicStructuresOrganization,
                    _Resource=HydraulicInfrastructureResource
                ),
                regex=['[0-9A-Za-z-_.]+', '[0-9A-Za-z-_.{}]+']
            ),
        ))

        url_maps.extend((
            UrlMap(
                name='model_details_tab',
                url='hydraulic_structures/health_infrastructures/{resource_id}/details/{tab_slug}',
                controller=HealthInfrastructureResourceDetails.as_controller(
                    _app=self,
                    _persistent_store_name='primary_db',
                    _Organization=HydraulicStructuresOrganization,
                    _Resource=HealthInfrastructureResource,
                ),
                regex=['[0-9A-Za-z-_.]+', '[0-9A-Za-z-_.{}]+']
            ),
        ))

        url_maps.extend(resource_workflows.urls(
            url_map_maker=UrlMap,
            app=self,
            persistent_store_name='primary_db',
            workflow_pairs=[(workflow, HydraulicStructuresWorkflowRouter) for _, workflow in HYDRAULICSTRUCTURES_WORKFLOWS.items()],
            custom_models=(
                HydraulicStructuresProjectAreaResource,
                HydraulicStructuresOrganization
            ),
        ))

        url_maps.extend((
            UrlMap(
                name='home',
                url='',
                controller=HydraulicStructuresModelMapView.as_controller(
                    _app=self,
                    _persistent_store_name=self.DATABASE_NAME,
                    geoserver_name=self.GEOSERVER_NAME,
                    _Organization=HydraulicStructuresOrganization,
                    _Resource=HydraulicStructuresProjectAreaResource,
                    _SpatialManager=HydraulicStructuresSpatialManager,
                    _MapManager=HydraulicStructuresMapManager,
                ),
                regex=['[0-9A-Za-z-_.', '[0-9A-Za-z-_.{}]+']
            ),
        ))

        return url_maps

    def permissions(self):
        from tethysext.atcore.services.app_users.permissions_manager import AppPermissionsManager
        from tethysext.atcore.permissions.app_users import PermissionsGenerator

        # Generate permissions for App Users
        pm = AppPermissionsManager(self.namespace)
        pg = PermissionsGenerator(pm)
        permissions = pg.generate()

        return permissions

    @classmethod
    def get_job_executable_dir(cls):
        """
        Return:
             str: the path to the directory containing the job executables.
        """
        return str(Path(sys.modules['tethysapp'].hydraulic_structures.__file__).parent / 'job_scripts')

    @classmethod
    def get_file_database_root(cls, relative_to='app'):
        """
        Resolve the FileDatabaseRoot relative to system given. The file database root location will vary depending on
         which system you are accessing it from.

        Args:
            relative_to (str): One of 'app', 'condor-linux', or 'condor-windows'.

        Returns:
            str: the path to the directory containing file databases.
        """  # noqa: E501
        if relative_to == 'app':
            return cls.FILE_DATABASE_ROOT

        if relative_to == 'condor-linux':
            # If the setting isn't defined, return the FDB root located in app_workspaces
            linux_fdb_root = cls.get_custom_setting(cls.LINUX_CONDOR_FDB_ROOT_NAME)
            return linux_fdb_root if linux_fdb_root else cls.FILE_DATABASE_ROOT

        elif relative_to == 'condor-windows':
            return cls.get_custom_setting(cls.WINDOWS_CONDOR_FDB_ROOT_NAME)

        return None
