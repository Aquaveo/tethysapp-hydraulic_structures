"""
********************************************************************************
* Name: project_area_workflows_tab.py
* Author: gagelarsen
* Created On: April 02, 2022
* Copyright: (c) Aquaveo 2022
********************************************************************************
"""
import logging
from django.shortcuts import redirect
from django.contrib import messages
from tethysext.atcore.controllers.resources import ResourceWorkflowsTab
from tethysapp.hydraulic_structures.models.hydraulic_structures_workflows import HYDRAULICSTRUCTURES_WORKFLOWS
from tethysapp.hydraulic_structures.services.spatial_managers.hydraulic_structures import HydraulicStructuresSpatialManager

from tethysapp.hydraulic_structures.services.map_manager import HydraulicStructuresMapManager

log = logging.getLogger('tethys.' + __name__)


class ProjectAreaWorkflowsTab(ResourceWorkflowsTab):
    template_name="hydraulic_structures/resources/tabs/workflows.html"
    modal_templates = [
        'hydraulic_structures/resources/tabs/delete_workflow_modal.html'
    ]

    @classmethod
    def get_workflow_types(cls):
        return HYDRAULICSTRUCTURES_WORKFLOWS

    def get_map_manager(self):
        return HydraulicStructuresMapManager

    def get_spatial_manager(self):
        return HydraulicStructuresSpatialManager

    def get_sds_setting_name(self):
        return self.get_app().GEOSERVER_NAME

    def post(self, request, resource_id, *args, **kwargs):
        """
        Handle the New Workflow form submissions for this tab.
        """
        params = request.POST
        all_workflow_types = self.get_workflow_types()

        if 'new-workflow' in params:
            # Create new workflow
            _AppUser = self.get_app_user_model()
            make_session = self.get_sessionmaker()
            session = make_session()
            request_app_user = _AppUser.get_app_user_from_request(request, session)

            try:
                WorkflowModel = all_workflow_types['prepare_query']
                workflow = WorkflowModel.new(
                    app=self._app,
                    name='consulta',
                    resource_id=resource_id,
                    creator_id=request_app_user.id,
                    geoserver_name=self.get_sds_setting_name(),
                    map_manager=self.get_map_manager(),
                    spatial_manager=self.get_spatial_manager(),
                )
                session.add(workflow)
                session.commit()

            except Exception:
                message = 'Un error inesperado ocurrió mientras se creaba la nueva consulta.'
                log.exception(message)
                messages.error(request, message)
                return redirect(request.path)
            finally:
                session.close()

            messages.success(
                request,
                f'Successfully created new {all_workflow_types["prepare_query"].DISPLAY_TYPE_SINGULAR}: {"prepare_query"}'
            )

            return redirect(request.path)

        # Redirect/render the normal GET page by default with warning message.
        messages.warning(request, 'Unable to perform requested action.')
        return redirect(request.path)