#!/opt/tethys-python
import time
import json
import os
from pprint import pprint

# DO NOT REMOVE, need to import all the subclasses of ResourceWorkflowStep for the polymorphism to work.
from tethysext.atcore.models.resource_workflow_results import *  # noqa: F401, F403
from tethysext.atcore.models.resource_workflow_steps import *  # noqa: F401, F403
from tethysext.atcore.services.resource_workflows.decorators import workflow_step_job
# END DO NOT REMOVE


@workflow_step_job
def main(resource_db_session, model_db_session, resource, workflow, step, gs_private_url, gs_public_url, resource_class,
         workflow_class, params_json, params_file, cmd_args):
    pprint('Running CropWat Model...')
    # Parse out parameters
    parameters = params_json['Update Model Input']['parameters']
    form_values = parameters['form-values']
    pprint('Model Input...')
    pprint(form_values)

    # Sleep for 5 seconds
    time.sleep(5)

    # Commit
    resource_db_session.commit()
    print(f'Successfully ran CropWat Model')