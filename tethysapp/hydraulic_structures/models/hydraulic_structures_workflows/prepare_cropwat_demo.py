"""
********************************************************************************
* Name: flood simulation_workflow
* Author: glarsen, mlebaron
* Created On: October 17, 2019
* Copyright: (c) Aquaveo 2019
********************************************************************************
"""
import param
import os
import panel as pn

from tethysext.atcore.models.app_users import ResourceWorkflow
from tethysext.atcore.models.resource_workflow_steps import FormInputRWS, SpatialInputRWS, SpatialCondorJobRWS,\
    ResultsResourceWorkflowStep
from tethysext.atcore.models.resource_workflow_results import SpatialWorkflowResult, DatasetWorkflowResult, \
    PlotWorkflowResult, ReportWorkflowResult

from tethysapp.hydraulic_structures.models.resources.project_area_resource import HydraulicStructuresProjectAreaResource


class SelectCropWatModelParam(param.Parameterized):
    DEFAULT_SETTINGS_ZONES = {
        'Santiago': {
            'Arroz Area': 114044, 'Arroz Percent First Cycle': 20, 'Arroz Percent Second Cycle': 30,
            'Arroz Percent Third Cycle': 20, 'Arroz Percent Fourth Cycle': 30, 'Arroz Efficiency': 0.2,
        },
    }

    def __init__(self, *args, **kwargs):
        super(SelectCropWatModelParam, self).__init__(*args, **kwargs)
        if 'request' in kwargs:
            self.update_param_data(**kwargs)

    select_existing_cropwat_model = param.ObjectSelector(default='default_string', precedence=1, objects=['default_string'],
                                                  label="Select Existing CropWat Model")
    
    arroz_area = param.Parameter(default=-10000, pickle_default_value=False, precedence=2, label='Arroz Area')
    arroz_percent_first_cycle = param.Parameter(default=-20, precedence=3, label='Arroz Percent First Cycle')
    arroz_percent_second_cycle = param.Parameter(default=-20, precedence=4, label='Arroz Percent Second Cycle')
    arroz_percent_third_cycle = param.Parameter(default=-20, precedence=5, label='Arroz Percent Third Cycle')
    arroz_percent_fourth_cycle = param.Parameter(default=-20, precedence=6, label='Arroz Percent Fourth Cycle')
    arroz_efficiency = param.Parameter(default=-0.2, precedence=7, label='Arroz Efficiency')


    def update_param_data(self, **kwargs):
        """
            This method will update the base_scenario and existing scenario using the existing model intersecting with
            the irrigation zone.
        """
        if kwargs:
            workflow_id = None
            if kwargs['request'].resolver_match:
                resource_id = kwargs['request'].resolver_match.kwargs['resource_id']
            else:
                resource_id = kwargs['request'].url_route['kwargs']['resource_id']
                workflow_id = kwargs['request'].url_route['kwargs']['workflow_id']
            session = kwargs['session']
            resource = session.query(HydraulicStructuresProjectAreaResource).get(resource_id)
            workflow = session.query(ResourceWorkflow).get(workflow_id)
            select_existing_cropwat_models = dict()
            model_name_duplicate_count = 0
            for model in resource.models:
                model_name = str(model.name)
                if str(model.name) in select_existing_cropwat_models.keys():
                    model_name_duplicate_count += 1
                    model_name = f'{model_name} {model_name_duplicate_count}'
                select_existing_cropwat_models[model_name] = str(model.id)

            param_update_list = ['select_existing_cropwat_model']
            for each_param in param_update_list:
                self.param[each_param].default = list(select_existing_cropwat_models.values())[0]
                self.param[each_param].names = select_existing_cropwat_models
                self.param[each_param].objects = list(select_existing_cropwat_models.values())

            zone_param_update_list = \
                ['Arroz Area', 'Arroz Percent First Cycle', 'Arroz Percent Second Cycle', 'Arroz Percent Third Cycle',
                 'Arroz Percent Fourth Cycle', 'Arroz Efficiency']

            resource_name = resource.name
            zone_name = 'Santiago'
            for each_zone_param in zone_param_update_list:
                zone_param_name = each_zone_param.replace(" ", "_").lower()
                # This is how you set default value
                if each_zone_param in self.DEFAULT_SETTINGS_ZONES[zone_name]:
                    setattr(self, zone_param_name, self.DEFAULT_SETTINGS_ZONES[zone_name][each_zone_param])
                else:
                    self.param[zone_param_name].precedence = -1


ops = SelectCropWatModelParam()
op = pn.panel(ops.param)
pn.Param(SelectCropWatModelParam, default_layout=pn.Row, width=900, show_name=False)

CropWatParamView = pn.Param(
    SelectCropWatModelParam,
    parameters=['select_existing_cropwat_model', 'arroz_area', 'arroz_percent_first_cycle',
                'arroz_percent_second_cycle'],
    show_name=False,
    default_layout=pn.Row,
    width=600,
)

class PrepareCropWatWorkflow(ResourceWorkflow):
    """
    Data model for storing information about detention basin workflows.
    """
    TYPE = 'prepare_cropwat_demo'
    DISPLAY_TYPE_SINGULAR = 'Prepare Cropwat Workflow'
    DISPLAY_TYPE_PLURAL = 'Prepare Cropwat Workflow'

    __mapper_args__ = {
        'polymorphic_identity': TYPE
    }

    def get_url_name(self):
        return 'hydraulic_structures:prepare_cropwat_demo_workflow'

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
        workflow.set_attribute('linux_fdb_root', app.get_file_database_root(relative_to='condor-linux'))

        # Setup Create Detention Basins Step
        step1 = FormInputRWS(
            name='Update Model Input',
            order=10,
            help='Select CropWat Model and Update Model Input',
            options={
                'param_class': 'tethysapp.hydraulic_structures.models.hydraulic_structures_workflows.'
                               'prepare_cropwat_demo.SelectCropWatModelParam',
                'form_title': 'Update Model Input',
                'renderer': 'bokeh'
            }
        )
        workflow.steps.append(step1)

        job_executable_dir = app.get_job_executable_dir()

        run_cropwat_model = {
            'name': 'run_cropwat_model',
            'condorpy_template_name': 'vanilla_transfer_files',
            'remote_input_files': [
                os.path.join(job_executable_dir, 'workflows', 'prepare_cropwat_demo',
                             'run_cropwat_model.py'),
            ],
            'attributes': {
                'executable': 'run_cropwat_model.py',
            }
        }

        prepare_results = {
            'name': 'prepare_results',
            'condorpy_template_name': 'vanilla_transfer_files',
            'remote_input_files': [
                os.path.join(job_executable_dir, 'workflows', 'prepare_cropwat_demo',
                             'prepare_results.py'),
            ],
            'attributes': {
                'executable': 'prepare_results.py',
            },
            'parents': [run_cropwat_model['name']],
        }

        step2 = SpatialCondorJobRWS(
            name='Review CropWat Input',
            order=30,
            help='Review selected CropWat model and press the Run button to run the simulation. Press the Next button'
                 ' after execution as finished',
            options={
                'scheduler': app.SCHEDULER_NAME,
                'jobs': [run_cropwat_model, prepare_results],
                'working_message': 'Model is running.',
                'error_message': 'Job failed.',
                'pending_message': 'Run model to continue.',
                'geocode_enabled': False,
            },
            geoserver_name=geoserver_name,
            map_manager=map_manager,
            spatial_manager=spatial_manager,
        )
        workflow.steps.append(step2)

        # Verify Results
        step3 = ResultsResourceWorkflowStep(
            name='Preview Results',
            order=40,
            help='Use the tabs near the bottom on the screen to view each result',
        )
        workflow.steps.append(step3)
        step2.result = step3

        review_results_1 = HydraulicInfrastructureWorkflowResult(
            name='CropWat Result',
            codename='cropwat_table',
            order=30,
            options={
                'no_hydraulic_infrastructure_message': 'No data to view...',
            },
        )

        review_results_2 = PlotWorkflowResult(
            name='Gross Irrigation Demand',
            codename='gross_demand',
            order=30,
            options={
                'no_hydraulic_infrastructure_message': 'No data to view...',
                'renderer': 'plotly',
                'plot_type': 'lines',
                'line_shape': 'spline',
                'axis_labels': ['Time', 'Depth (ft)'],
            },
        )

        review_results_3 = SpatialWorkflowResult(
            name='Map Demand',
            codename='map_demand',
            order=20,
            options={
                'layer_group_title': 'Map Demand',
            },
            geoserver_name=geoserver_name,
            map_manager=map_manager,
            spatial_manager=spatial_manager,
        )
        step3.results.extend([review_results_1, review_results_2, review_results_3])

        return workflow
