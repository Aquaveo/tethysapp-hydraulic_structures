from tethys_gizmos.gizmo_options.select_input import SelectInput
from tethys_gizmos.gizmo_options.text_input import TextInput
from tethysapp.hydraulic_structures.controllers.infrastructure_resource_types import HYDRAULIC_INFRASTRUCTURE_TYPE


def intake_create_context(
    intake_year_init,
):
    intake_year = TextInput(
        display_text="Anio",
        name="dams_and_resevoirs_year",
        placeholder="anio operacion",
        initial=intake_year_init,
    )

    intake_context = {
        "intake_year": intake_year,
    }
    return intake_context


def main_irrigation_channel_create_context(
    main_irrigation_channel_year_init,
):
    main_irrigation_channel_year = TextInput(
        display_text="Anio",
        name="main_irrigation_channel_year",
        placeholder="anio operacion",
        initial=main_irrigation_channel_year_init,
    )

    main_irrigation_channel_context = {
        "main_irrigation_channel_year": main_irrigation_channel_year,
    }
    return main_irrigation_channel_context


def secondary_and_lateral_irrigation_system_create_context(
    secondary_and_lateral_irrigation_system_init,
):
    secondary_and_lateral_irrigation_system_year = TextInput(
        display_text="Anio",
        name="secondary_and_lateral_irrigation_system_year",
        placeholder="anio operacion",
        initial=secondary_and_lateral_irrigation_system_init,
    )

    secondary_and_lateral_irrigation_system_context = {
        "secondary_and_lateral_irrigation_system_year": secondary_and_lateral_irrigation_system_year,
    }
    return secondary_and_lateral_irrigation_system_context


def drainage_channel_create_context(
    drainage_channel_year_init,
):
    drainage_channel_year = TextInput(
        display_text="Anio",
        name="drainage_channel_year",
        placeholder="anio operacion",
        initial=drainage_channel_year_init,
    )

    drainage_channel_context = {
        "drainage_channel_year": drainage_channel_year,
    }
    return drainage_channel_context


def intake_storage_pond_create_context(
    intake_storage_pond_year_init,
):
    intake_storage_pond_year = TextInput(
        display_text="Anio",
        name="intake_storage_pond_year",
        placeholder="anio operacion",
        initial=intake_storage_pond_year_init,
    )

    intake_storage_pond_context = {
        "intake_storage_pond_year": intake_storage_pond_year,
    }
    return intake_storage_pond_context
