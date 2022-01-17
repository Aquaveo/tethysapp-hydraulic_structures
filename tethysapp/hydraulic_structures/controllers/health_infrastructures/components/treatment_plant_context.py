from tethys_gizmos.gizmo_options.select_input import SelectInput
from tethys_gizmos.gizmo_options.text_input import TextInput


def water_treatment_plant_create_context(water_treatment_plant_year_init):
    water_treatment_plant_year = TextInput(
        display_text="Anio",
        name="water_treatment_plant_year",
        placeholder="anio operacion",
        initial=water_treatment_plant_year_init,
    )

    water_treatment_plant_context = {
        "water_treatment_plant_year": water_treatment_plant_year,
    }
    return water_treatment_plant_context


def sewer_treatment_plant_create_context(sewer_treatment_plant_year_init):
    sewer_treatment_plant_year = TextInput(
        display_text="Anio",
        name="sewer_treatment_plant_year",
        placeholder="anio operacion",
        initial=sewer_treatment_plant_year_init,
    )

    sewer_treatment_plant_context = {
        "sewer_treatment_plant_year": sewer_treatment_plant_year,
    }
    return sewer_treatment_plant_context
