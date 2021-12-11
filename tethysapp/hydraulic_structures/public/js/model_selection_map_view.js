/*****************************************************************************
 * FILE:    model_selection_map_view.js
 * DATE:    August 27th, 2021
 * AUTHOR:  Hoang Tran, Nathan Swain
 * COPYRIGHT: (c) Aquaveo 2021
 * LICENSE:
 *****************************************************************************/

/*****************************************************************************
 *                      LIBRARY WRAPPER
 *****************************************************************************/

var MODEL_SELECTION_MAP_VIEW = (function() {
	// Wrap the library in a package function
	"use strict"; // And enable strict mode for this library

	/************************************************************************
 	*                      MODULE LEVEL / GLOBAL VARIABLES
 	*************************************************************************/
 	// Constants

 	// Module variables
 	var m_public_interface;				// Object returned by the module

 	var m_map,                          // OpenLayers map object
        m_layers;                       // OpenLayers layer objects mapped to by layer by layer_name

    // help modal
    var bind_help_modal_check, init_help_modal;

	/************************************************************************
 	*                    PRIVATE FUNCTION DECLARATIONS
 	*************************************************************************/
 	// Config
 	var setup_model_select, set_layer_styles;

 	/************************************************************************
 	*                    PRIVATE FUNCTION IMPLEMENTATIONS
 	*************************************************************************/
    // Config

    setup_model_select = function() {
        // Get handle on map
	    m_map = TETHYS_MAP_VIEW.getMap();

	    // Setup layer map
	    m_layers = {};

	    // Get id from tethys_data attribute
	    m_map.getLayers().forEach(function(item, index, array) {
	        if ('tethys_data' in item && 'layer_id' in item.tethys_data) {
	           if (item.tethys_data.layer_id in m_layers) {
	               console.log('Warning: layer_id already in layers map: "' + item.tethys_data.layer_id + '".');
	           }
	           m_layers[item.tethys_data.layer_id] = item;
	        }
	    });
    };

    init_help_modal = function() {
        let show_helper = $('#show_helper_status').data('value')
        if (show_helper == 'True') {
            $('#help-modal').modal('show');
        }
    }

    bind_help_modal_check = function () {
        $('#modal-show-again').change(function() {
            // Update django session.
            var csrf_token = get_csrf_token();
            $.ajax({
                type: 'get',
                url: '/apps/hydraulic_structures/update-help-modal-status/',
                data: {'status': !this.checked,
                       'page_name': 'model_selection'},
                beforeSend: xhr => {
                    xhr.setRequestHeader('X-CSRFToken', csrf_token);
                },
            }).done(function (json) {
                if(json.success) {
                }


            })
        })
    }

    set_layer_styles = function() {
        for (const [layer_id, layer] of Object.entries(m_layers)) {
            if (layer.tethys_data.layer_variable === 'irrigation_zone') {
                // Set style for irrigation zones
                layer.setStyle(new ol.style.Style({
                    stroke: new ol.style.Stroke({color: 'blue', width: 2}),
                    fill: new ol.style.Fill({color: 'rgba(0,0,255,0.3)'}),
                }));
            } else if (layer.tethys_data.layer_variable === 'model_resource') {
                // Set style for model_resources
                layer.setStyle(new ol.style.Style({
                    stroke: new ol.style.Stroke({color: 'red', width: 1}),
                    fill: new ol.style.Fill({color: 'rgba(255,0,0,0.1)'}),
                }));
            } else if (layer.tethys_data.layer_variable === 'dataset_resource') {
                // Set style for model_resources
                layer.setStyle(new ol.style.Style({
                    stroke: new ol.style.Stroke({color: 'green', width: 1}),
                    fill: new ol.style.Fill({color: 'rgba(0,255,0,0.1)'}),
                }));
            }
        }
    }

    ATCORE_MAP_VIEW.action_button_generator(function(feature) {
        let layer_name = ATCORE_MAP_VIEW.get_layer_name_from_feature(feature);
        let fid = ATCORE_MAP_VIEW.get_feature_id_from_feature(feature);

        // Check if layer is plottable
        let layer = m_layers[layer_name];
        let resource_id = m_layers[layer_name]['tethys_data']['layer_id'];
        if (!layer || !layer.tethys_data.has_action) {
            return;
        }

        // Build Action Button Markup
        let action_button =
            '<div class="action-btn-wrapper">' +
                '<a class="btn btn-primary btn-popup" ' +
                    'href="/apps/hydraulic_structures/irrigation-zones/' + resource_id + '/details/summary/"' +
                    'role="button"' +
                    'data-feature-id="' + fid +'"' +
                    'data-layer-id="' + layer_name + '"' +
                    'id="map-view-plot-button"' +
                '>Load Irrigation Zone</a>' +
            '</div>';

        return action_button;
    })

    ATCORE_MAP_VIEW.plot_button_generator(function(feature) {
    })

    ATCORE_MAP_VIEW.properties_table_generator(function(feature) {
    })

	/************************************************************************
 	*                        DEFINE PUBLIC INTERFACE
 	*************************************************************************/
	/*
	 * Library object that contains public facing functions of the package.
	 * This is the object that is returned by the library wrapper function.
	 * See below.
	 * NOTE: The functions in the public interface have access to the private
	 * functions of the library because of JavaScript function scope.
	 */
	m_public_interface = {
	};

	/************************************************************************
 	*                  INITIALIZATION / CONSTRUCTOR
 	*************************************************************************/

	// Initialization: jQuery function that gets called when
	// the DOM tree finishes loading
	$(function() {
	    setup_model_select();
	    init_help_modal();
	    bind_help_modal_check();
	    set_layer_styles();
	});

	return m_public_interface;

}()); // End of package wrapper
// NOTE: that the call operator (open-closed parenthesis) is used to invoke the library wrapper
// function immediately after being parsed.
