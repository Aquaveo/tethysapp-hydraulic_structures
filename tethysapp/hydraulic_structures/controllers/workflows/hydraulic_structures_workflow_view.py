"""
********************************************************************************
* Name: hydraulic_structures_workflow_view.py
* Author: glarsen
* Created On: Oct 09, 2019
* Copyright: (c) Aquaveo 2019
********************************************************************************
"""
from django.shortcuts import reverse
from tethysext.atcore.controllers.resource_workflows import ResourceWorkflowRouter


class HydraulicStructuresWorkflowRouter(ResourceWorkflowRouter):

    def default_back_url(self, request, resource_id, *args, **kwargs):
        """
        Get the url of the view to go back to.
        Args:
            request(HttpRequest): The request.
            resource_id(str): ID of the resource this workflow applies to.
            workflow_id(str): ID of the workflow.
            step_id(str): ID of the step to render.
            args, kwargs: Additional arguments passed to the controller.

        Returns:
            str: back url
        """
        return reverse(
            'hydraulic_structures:project_area_details_tab',
            kwargs={
               'resource_id': resource_id,
               'tab_slug': 'workflows'
            }
        )
