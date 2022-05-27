"""
********************************************************************************
* Name: hs_spatial_input_mwv.py
* Author: msouffront
* Created On: May 21, 2022
* Copyright: (c) Aquaveo 2022
********************************************************************************
"""
import json
import os
import zipfile
import uuid
import shutil
import shapefile as shp
import geojson
import logging
from django.shortcuts import redirect
from django.http import JsonResponse
from tethys_sdk.gizmos import MVDraw
from tethysext.atcore.forms.widgets.param_widgets import generate_django_form
from tethysext.atcore.controllers.resource_workflows.map_workflows import SpatialInputMWV
from tethysext.atcore.models.resource_workflow_steps import SpatialInputRWS


log = logging.getLogger(f'tethys.{__name__}')


class HydraulicStructuresSpatialInputMWV(SpatialInputMWV):
    """
    Controller for a map workflow view requiring spatial input.
    """
    previous_title = 'Regresar'
    next_title = 'Siguiente'
    finish_title = 'Terminar'
    # template_name = 'atcore/resource_workflows/spatial_input_mwv.html'
    # valid_step_classes = [SpatialInputRWS]

    def get_step_specific_context(self, request, session, context, current_step, previous_step, next_step):
        """
        Hook for extending the view context.

        Args:
           request(HttpRequest): The request.
           session(sqlalchemy.orm.Session): Session bound to the steps.
           context(dict): Context object for the map view template.
           current_step(ResourceWorkflowStep): The current step to be rendered.
           previous_step(ResourceWorkflowStep): The previous step.
           next_step(ResourceWorkflowStep): The next step.

        Returns:
            dict: key-value pairs to add to context.
        """
        # Determine if user has an active role
        is_read_only = self.is_read_only(request, current_step)

        if is_read_only:
            allow_shapefile_uploads = False
            allow_edit_attributes = False
        else:
            allow_shapefile_uploads = current_step.options.get('allow_shapefile')
            allow_edit_attributes = True

        return {'allow_shapefile': allow_shapefile_uploads,
                'allow_edit_attributes': allow_edit_attributes}

    def process_step_options(self, request, session, context, resource, current_step, previous_step, next_step):
        """
        Hook for processing step options (i.e.: modify map or context based on step options).

        Args:
            request(HttpRequest): The request.
            session(sqlalchemy.orm.Session): Session bound to the steps.
            context(dict): Context object for the map view template.
            resource(Resource): the resource for this request.
            current_step(ResourceWorkflowStep): The current step to be rendered.
            previous_step(ResourceWorkflowStep): The previous step.
            next_step(ResourceWorkflowStep): The next step.
        """
        # Prepare attributes form
        attributes = current_step.options.get('attributes', None)

        if attributes is not None:
            attributes_form = generate_django_form(attributes)
            context.update({'attributes_form': attributes_form})

        # Get Map View
        map_view = context['map_view']

        # Determine if user has an active role
        is_read_only = self.is_read_only(request, current_step)

        # Turn off feature selection
        self.set_feature_selection(map_view=map_view, enabled=False)

        if not is_read_only:
            enabled_controls = ['Modify', 'Delete', 'Move', 'Pan']

            # Add layer for current geometry
            if current_step.options['allow_drawing']:
                for elem in current_step.options['shapes']:
                    if elem == 'points':
                        enabled_controls.append('Point')
                    elif elem == 'lines':
                        enabled_controls.append('LineString')
                    elif elem == 'polygons':
                        enabled_controls.append('Polygon')
                    elif elem == 'extents':
                        enabled_controls.append('Box')
                    else:
                        raise RuntimeError('Invalid shapes defined: {}.'.format(elem))
        else:
            enabled_controls = ['Pan']

        # Load the currently saved geometry, if any.
        current_geometry = current_step.get_parameter('geometry')

        # Configure drawing
        draw_options = MVDraw(
            controls=enabled_controls,
            initial='Pan',
            initial_features=current_geometry,
            output_format='GeoJSON',
            snapping_enabled=current_step.options.get('snapping_enabled'),
            snapping_layer=current_step.options.get('snapping_layer'),
            snapping_options=current_step.options.get('snapping_options'),
            feature_selection=attributes is not None,
            legend_title=current_step.options.get('plural_name'),
            data={
                'layer_id': 'drawing_layer',
                'layer_name': 'drawing_layer',
                'popup_title': current_step.options.get('singular_name'),
                'excluded_properties': ['id', 'type'],
            }
        )

        if draw_options is not None and 'map_view' in context:
            map_view.draw = draw_options

        # Save changes to map view
        context.update({'map_view': map_view})

        # Note: new layer created by super().process_step_options will have feature selection enabled by default
        super().process_step_options(
            request=request,
            session=session,
            context=context,
            resource=resource,
            current_step=current_step,
            previous_step=previous_step,
            next_step=next_step
        )
