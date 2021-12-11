#!/opt/tethys-python
import datetime
import json
import os
from pprint import pprint
import pandas as pd
import plotly.express as px

from tethysext.atcore.services.file_database import FileCollectionClient, FileDatabaseClient


# DO NOT REMOVE, need to import all the subclasses of ResourceWorkflowStep for the polymorphism to work.
from tethysapp.hydraulic_structures.models.resources.model_resource import HydraulicStructuresModelResource
from tethysapp.hydraulic_structures.models.resources.dataset_resource import HydraulicStructuresDatasetResource
from tethysext.atcore.models.resource_workflow_results import *  # noqa: F401, F403
from tethysext.atcore.models.resource_workflow_steps import *  # noqa: F401, F403
from tethysext.atcore.services.resource_workflows.decorators import workflow_step_job
# END DO NOT REMOVE


def generate_geojson_setting(resource, properties={}):
    geojson_model_boundary = {
        'type': 'FeatureCollection',
        'name': resource.name,
        'properties': {},
        'crs': {'type': 'name', 'properties': {'name': 'urn:ogc:def:crs:OGC:1.3:CRS84'}},
        'features': [{
            'type': 'Feature',
            'properties': properties,
            'geometry': resource.get_extent(),
        }]
    }

    extent_lat = []
    extent_lng = []
    for coordinate in resource.get_extent()['coordinates'][0]:
        extent_lng.append(coordinate[0])
        extent_lat.append(coordinate[1])

    extents = [min(extent_lng), min(extent_lat), max(extent_lng), max(extent_lat)]

    return geojson_model_boundary, extents


def parse_value(value):
    if pd.isna(value):
        return 0
    else:
        return round(value, 2)

@workflow_step_job
def main(resource_db_session, model_db_session, resource, workflow, step, gs_private_url, gs_public_url, resource_class,
         workflow_class, params_json, params_file, cmd_args):
    pprint('Getting Flow Data...')
    # Parse out parameters
    parameters = params_json['Update Model Input']['parameters']
    form_values = parameters['form-values']
    existing_model_id = form_values['select_existing_cropwat_model']

    # Get base ModelResource from selected base model
    existing_model = resource_db_session.query(HydraulicStructuresModelResource).get(existing_model_id)

    file_database_id = workflow.get_attribute('file_database_id')
    root_directory = workflow.get_attribute('linux_fdb_root')
    database_client = FileDatabaseClient(resource_db_session, root_directory, file_database_id)

    # Find file_collection with adh model files
    print('Retrieving cropwat data files...')
    for file_collection in existing_model.file_collections:
        collection_client = FileCollectionClient(resource_db_session, database_client, file_collection.id)
        for file in collection_client.files:
            if file.endswith('.csv'):
                cropwat_csv = os.path.join(collection_client.path, file)

    cropwat_table = pd.read_csv(cropwat_csv, engine='python', encoding='utf-8', error_bad_lines=False)

    # building data
    # Create list of rows with crop name
    crop_name_rows = cropwat_table.iloc[:, 0].values.tolist()
    net_demand_jan_rows = cropwat_table.iloc[:, 7].values.tolist()
    net_demand_feb_rows = cropwat_table.iloc[:, 8].values.tolist()
    net_demand_mar_rows = cropwat_table.iloc[:, 9].values.tolist()
    net_demand_apr_rows = cropwat_table.iloc[:, 10].values.tolist()
    net_demand_may_rows = cropwat_table.iloc[:, 11].values.tolist()
    net_demand_jun_rows = cropwat_table.iloc[:, 12].values.tolist()
    net_demand_jul_rows = cropwat_table.iloc[:, 13].values.tolist()
    net_demand_aug_rows = cropwat_table.iloc[:, 14].values.tolist()
    net_demand_sep_rows = cropwat_table.iloc[:, 15].values.tolist()
    net_demand_oct_rows = cropwat_table.iloc[:, 16].values.tolist()
    net_demand_nov_rows = cropwat_table.iloc[:, 17].values.tolist()
    net_demand_dec_rows = cropwat_table.iloc[:, 18].values.tolist()

    area_tas_rows = list()
    area_has_rows = list()
    percent_rows = list()
    area_crop_rows = list()
    demand_jan_rows = list()
    demand_feb_rows = list()
    demand_mar_rows = list()
    demand_apr_rows = list()
    demand_may_rows = list()
    demand_jun_rows = list()
    demand_jul_rows = list()
    demand_aug_rows = list()
    demand_sep_rows = list()
    demand_oct_rows = list()
    demand_nov_rows = list()
    demand_dec_rows = list()
    irrigation_efficiency_rows = list()
    gross_demand_jan_rows = list()
    gross_demand_feb_rows = list()
    gross_demand_mar_rows = list()
    gross_demand_apr_rows = list()
    gross_demand_may_rows = list()
    gross_demand_jun_rows = list()
    gross_demand_jul_rows = list()
    gross_demand_aug_rows = list()
    gross_demand_sep_rows = list()
    gross_demand_oct_rows = list()
    gross_demand_nov_rows = list()
    gross_demand_dec_rows = list()

    row_index = 0
    crop_name_index = 1
    prev_crop_name = ''
    multiple_cycles = False
    for crop_name_row in crop_name_rows:
        if crop_name_row != prev_crop_name:
            prev_crop_name = crop_name_row
            crop_name_index = 1
        # Set area value
        area_param_name = crop_name_row.lower().replace(" ", "_") + "_area"
        area_tas = form_values[area_param_name]
        area_has = round(area_tas/16, 2)
        area_tas_rows.append(area_tas)
        area_has_rows.append(area_has)

        # Set percent value
        percent_param_name = crop_name_row.lower().replace(" ", "_") + "_percent"
        if percent_param_name not in form_values:
            multiple_cycles = True
        if multiple_cycles:
            if crop_name_index == 1:
                percent_param_name = crop_name_row.lower().replace(" ", "_") + "_percent_first_cycle"
            elif crop_name_index == 2:
                percent_param_name = crop_name_row.lower().replace(" ", "_") + "_percent_second_cycle"
            elif crop_name_index == 3:
                percent_param_name = crop_name_row.lower().replace(" ", "_") + "_percent_third_cycle"
            elif crop_name_index == 4:
                percent_param_name = crop_name_row.lower().replace(" ", "_") + "_percent_fourth_cycle"

        percent = form_values[percent_param_name]
        percent_rows.append(percent)

        area_crop = round(area_has * percent / 100, 2)
        area_crop_rows.append(area_crop)

        demand_jan = parse_value(net_demand_jan_rows[row_index] * 10 * area_crop)
        demand_feb = parse_value(net_demand_feb_rows[row_index] * 10 * area_crop)
        demand_mar = parse_value(net_demand_mar_rows[row_index] * 10 * area_crop)
        demand_apr = parse_value(net_demand_apr_rows[row_index] * 10 * area_crop)
        demand_may = parse_value(net_demand_may_rows[row_index] * 10 * area_crop)
        demand_jun = parse_value(net_demand_jun_rows[row_index] * 10 * area_crop)
        demand_jul = parse_value(net_demand_jul_rows[row_index] * 10 * area_crop)
        demand_aug = parse_value(net_demand_aug_rows[row_index] * 10 * area_crop)
        demand_sep = parse_value(net_demand_sep_rows[row_index] * 10 * area_crop)
        demand_oct = parse_value(net_demand_oct_rows[row_index] * 10 * area_crop)
        demand_nov = parse_value(net_demand_nov_rows[row_index] * 10 * area_crop)
        demand_dec = parse_value(net_demand_dec_rows[row_index] * 10 * area_crop)

        demand_jan_rows.append(demand_jan)
        demand_feb_rows.append(demand_feb)
        demand_mar_rows.append(demand_mar)
        demand_apr_rows.append(demand_apr)
        demand_may_rows.append(demand_may)
        demand_jun_rows.append(demand_jun)
        demand_jul_rows.append(demand_jul)
        demand_aug_rows.append(demand_aug)
        demand_sep_rows.append(demand_sep)
        demand_oct_rows.append(demand_oct)
        demand_nov_rows.append(demand_nov)
        demand_dec_rows.append(demand_dec)

        efficiency_param_name = crop_name_row.lower().replace(" ", "_") + "_efficiency"
        efficiency = form_values[efficiency_param_name]

        irrigation_efficiency_rows.append(efficiency)

        gross_demand_jan = parse_value(demand_jan / efficiency)
        gross_demand_feb = parse_value(demand_feb / efficiency)
        gross_demand_mar = parse_value(demand_mar / efficiency)
        gross_demand_apr = parse_value(demand_apr / efficiency)
        gross_demand_may = parse_value(demand_may / efficiency)
        gross_demand_jun = parse_value(demand_jun / efficiency)
        gross_demand_jul = parse_value(demand_jul / efficiency)
        gross_demand_aug = parse_value(demand_aug / efficiency)
        gross_demand_sep = parse_value(demand_sep / efficiency)
        gross_demand_oct = parse_value(demand_oct / efficiency)
        gross_demand_nov = parse_value(demand_nov / efficiency)
        gross_demand_dec = parse_value(demand_dec / efficiency)

        gross_demand_jan_rows.append(gross_demand_jan)
        gross_demand_feb_rows.append(gross_demand_feb)
        gross_demand_mar_rows.append(gross_demand_mar)
        gross_demand_apr_rows.append(gross_demand_apr)
        gross_demand_may_rows.append(gross_demand_may)
        gross_demand_jun_rows.append(gross_demand_jun)
        gross_demand_jul_rows.append(gross_demand_jul)
        gross_demand_aug_rows.append(gross_demand_aug)
        gross_demand_sep_rows.append(gross_demand_sep)
        gross_demand_oct_rows.append(gross_demand_oct)
        gross_demand_nov_rows.append(gross_demand_nov)
        gross_demand_dec_rows.append(gross_demand_dec)

        row_index += 1
        crop_name_index += 1
        multiple_cycles = False

    cropwat_new_data = {
        'Crops': crop_name_rows,
        'Cycles': cropwat_table.iloc[:, 1].values.tolist(),
        'No Days': cropwat_table.iloc[:, 2].values.tolist(),
        'Cultivated Areas (tas)': area_tas_rows,
        'Cultivated Areas (has)': area_has_rows,
        'Cultivated Area Percentage': percent_rows,
        'Cultivated Area per Cycles': area_crop_rows,
        'Net Demand for Irrigation - Jan': cropwat_table.iloc[:, 7].values.tolist(),
        'Net Demand for Irrigation - Feb': cropwat_table.iloc[:, 8].values.tolist(),
        'Net Demand for Irrigation - Mar': cropwat_table.iloc[:, 9].values.tolist(),
        'Net Demand for Irrigation - Apr': cropwat_table.iloc[:, 10].values.tolist(),
        'Net Demand for Irrigation - May': cropwat_table.iloc[:, 11].values.tolist(),
        'Net Demand for Irrigation - Jun': cropwat_table.iloc[:, 12].values.tolist(),
        'Net Demand for Irrigation - Jul': cropwat_table.iloc[:, 13].values.tolist(),
        'Net Demand for Irrigation - Aug': cropwat_table.iloc[:, 14].values.tolist(),
        'Net Demand for Irrigation - Sep': cropwat_table.iloc[:, 15].values.tolist(),
        'Net Demand for Irrigation - Oct': cropwat_table.iloc[:, 16].values.tolist(),
        'Net Demand for Irrigation - Nov': cropwat_table.iloc[:, 17].values.tolist(),
        'Net Demand for Irrigation - Dec': cropwat_table.iloc[:, 18].values.tolist(),
        'Water Demand for Irrigation (m3) - Jan': demand_jan_rows,
        'Water Demand for Irrigation (m3) - Feb': demand_feb_rows,
        'Water Demand for Irrigation (m3) - Mar': demand_mar_rows,
        'Water Demand for Irrigation (m3) - Apr': demand_apr_rows,
        'Water Demand for Irrigation (m3) - May': demand_may_rows,
        'Water Demand for Irrigation (m3) - Jun': demand_jun_rows,
        'Water Demand for Irrigation (m3) - Jul': demand_jul_rows,
        'Water Demand for Irrigation (m3) - Aug': demand_aug_rows,
        'Water Demand for Irrigation (m3) - Sep': demand_sep_rows,
        'Water Demand for Irrigation (m3) - Oct': demand_oct_rows,
        'Water Demand for Irrigation (m3) - Nov': demand_nov_rows,
        'Water Demand for Irrigation (m3) - Dec': demand_dec_rows,
        'Gross Water Demand for Irrigation (m3) - Jan': demand_jan_rows,
        'Gross Water Demand for Irrigation (m3) - Feb': demand_feb_rows,
        'Gross Water Demand for Irrigation (m3) - Mar': demand_mar_rows,
        'Gross Water Demand for Irrigation (m3) - Apr': demand_apr_rows,
        'Gross Water Demand for Irrigation (m3) - May': demand_may_rows,
        'Gross Water Demand for Irrigation (m3) - Jun': demand_jun_rows,
        'Gross Water Demand for Irrigation (m3) - Jul': demand_jul_rows,
        'Gross Water Demand for Irrigation (m3) - Aug': demand_aug_rows,
        'Gross Water Demand for Irrigation (m3) - Sep': demand_sep_rows,
        'Gross Water Demand for Irrigation (m3) - Oct': demand_oct_rows,
        'Gross Water Demand for Irrigation (m3) - Nov': demand_nov_rows,
        'Gross Water Demand for Irrigation (m3) - Dec': demand_dec_rows,
    }

    cropwat_new_table = pd.DataFrame(data=cropwat_new_data)
    cropwat_new_table.fillna("", inplace=True)

    report_result = step.result.get_result_by_codename('cropwat_table')
    report_result.reset()

    report_result.add_pandas_dataframe('CropWat Result', cropwat_new_table.round(2), show_export_button=True)

    # Graph
    crop_name_list = sorted(set(crop_name_rows))
    chart_month_list = list()
    chart_crop_list = list()
    chart_value_list = list()
    month_list = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    for crop_name in crop_name_list:
        month_start_index = 19
        for month in month_list:
            chart_month_list.append(month)
            chart_crop_list.append(crop_name)
            chart_value = \
                cropwat_new_table.loc[cropwat_new_table['Crops'] == crop_name].iloc[:, month_start_index].sum()
            chart_value_list.append(chart_value)
            month_start_index += 1

    chart_data = {
        'Month': chart_month_list,
        'Crop': chart_crop_list,
        'Gross Demand': chart_value_list,
    }

    chart_dataframe = pd.DataFrame(data=chart_data)

    fig = px.bar(chart_dataframe, x="Crop", color="Month",
                 y='Gross Demand',
                 title="Gross Demand Monthly (m3)",
                 barmode='relative',
                 height=1000,
                 log_y=True,
                 category_orders={'Month': month_list}
                 )

    plot_result = step.result.get_result_by_codename('gross_demand')
    plot_result.reset()

    plot_result.add_plot(plot=fig)

    # Map
    map_result = step.result.get_result_by_codename('map_demand')
    map_result.reset()

    datasets = resource_db_session.query(HydraulicStructuresDatasetResource).\
        filter(HydraulicStructuresDatasetResource.extent.ST_Intersects(existing_model.extent)).all()

    for dataset in datasets:
        geojson_model_boundary, extents = generate_geojson_setting(dataset)

        map_result.add_geojson_layer(geojson=geojson_model_boundary, layer_name=dataset.name.lower().replace(" ", "_"),
                                     layer_title=dataset.name, layer_variable=str(dataset.id),
                                     layer_id=f'dataset_{str(dataset.id)}', extent=extents)

    # Add existing model too
    geojson_model_boundary, extents = generate_geojson_setting(existing_model, properties=chart_data)
    map_result.add_geojson_layer(geojson=geojson_model_boundary, layer_name=existing_model.name.lower().replace(" ", "_"),
                                 layer_title=existing_model.name, layer_variable=str(existing_model.id),
                                 layer_id=f'model_{str(dataset.id)}', extent=extents)
    # Commit
    resource_db_session.commit()
    print(f'Successfully retrieved data and saved to file_database_id {file_database_id} ')
