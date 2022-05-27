"""
********************************************************************************
* Name: flood simulation_workflow
* Author: msouffront, mlebaron
* Created On: April 17, 2022
* Copyright: (c) Aquaveo 2022
********************************************************************************
"""
import param
import panel as pn
from geoalchemy2 import func

from tethysext.atcore.models.app_users import ResourceWorkflow
from tethysext.atcore.models.resource_workflow_steps import FormInputRWS, SpatialInputRWS,\
    ResultsResourceWorkflowStep
from tethysext.atcore.models.resource_workflow_results import SpatialWorkflowResult, DatasetWorkflowResult, \
    PlotWorkflowResult, ReportWorkflowResult

from tethysapp.hydraulic_structures.models.resources.project_area_resource import HydraulicStructuresProjectAreaResource


class SelectStructureTypeParam(param.Parameterized):
    def __init__(self, *args, **kwargs):
        kwargs.pop('request', None)
        kwargs.pop('session', None)
        super().__init__(*args, **kwargs)
        self.update_param_data()

    select_structure_type = param.ObjectSelector(
        default='default_string', precedence=1, objects=['default_string'], label="Tipo de Estructura"
    )

    def update_param_data(self):
        select_structure_types = {'hydraulic_infrastructure': 'Estructuras Hidráulicas',
                                  'health_infrastructure': 'Estructuras Sanitarias'}

        param_update_list = ['select_structure_type']
        for each_param in param_update_list:
            self.param[each_param].default = list(select_structure_types.values())[0]
            self.param[each_param].names = select_structure_types
            self.param[each_param].objects = list(select_structure_types.values())


class PrepareQueryWorkflow(ResourceWorkflow):
    """
    Data model for storing information about detention basin workflows.
    """
    TYPE = 'prepare_query'
    DISPLAY_TYPE_SINGULAR = 'Consulta'
    DISPLAY_TYPE_PLURAL = 'Consultas'

    __mapper_args__ = {
        'polymorphic_identity': TYPE
    }

    def get_url_name(self):
        return 'hydraulic_structures:prepare_query_workflow'

    @classmethod
    def new(cls, app, name, resource_id, creator_id, geoserver_name, map_manager, spatial_manager, **kwargs):
        """
        Factor class method that creates a new workflow with steps
        Args:
            app:
            name:
            resource_id:
            creator_id:
            kwargs: additional arguments to use when configuring workflows.

        Returns:
            ResourceWorkflow: the new workflow.
        """
        # Create new workflow instance
        workflow = cls(name=name, resource_id=resource_id, creator_id=creator_id)

        # Set workflow attributes
        workflow.set_attribute('file_database_id', app.get_custom_setting(app.FILE_DATABASE_ID_NAME))

        # Setup Create Detention Basins Step
        step1 = FormInputRWS(
            name='Tipo de Estructura',
            order=10,
            help='',
            options={
                'param_class': 'tethysapp.hydraulic_structures.models.hydraulic_structures_workflows.'
                               'prepare_query.SelectStructureTypeParam',
                'form_title': 'Seleccione el Tipo de Estructura',
                'renderer': 'django'
            }
        )
        workflow.steps.append(step1)

        # # Verify Results
        # step2 = ResultsResourceWorkflowStep(
        #     name='Preview Results',
        #     order=40,
        #     help='Use the tabs near the bottom on the screen to view each result',
        # )
        # workflow.steps.append(step2)
        # step1.result = step2

        # review_results_1 = DatasetWorkflowResult(
        #     name='Result',
        #     codename='cropwat_table',
        #     order=30,
        #     options={
        #         'no_hydraulic_infrastructure_message': 'No data to view...',
        #     },
        # )

        # review_results_2 = SpatialWorkflowResult(
        #     name='Map Demand',
        #     codename='map_demand',
        #     order=20,
        #     options={
        #         'layer_group_title': 'Map Demand',
        #     },
        #     geoserver_name=geoserver_name,
        #     map_manager=map_manager,
        #     spatial_manager=spatial_manager,
        # )
        # step2.results.extend([review_results_1, review_results_2])

        return workflow
