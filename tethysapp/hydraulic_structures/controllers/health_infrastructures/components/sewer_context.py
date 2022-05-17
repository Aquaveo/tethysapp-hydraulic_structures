from tethys_gizmos.gizmo_options.select_input import SelectInput
from tethys_gizmos.gizmo_options.text_input import TextInput
from tethysapp.hydraulic_structures.controllers.infrastructure_resource_types import HYDRAULIC_INFRASTRUCTURE_TYPE


def sanitary_sewer_create_context(sanitary_sewer_year_init):
    sanitary_sewer_year = TextInput(
        display_text="Año",
        name="sanitary_sewer_year",
        placeholder="año operacion",
        initial=sanitary_sewer_year_init,
    )

    sanitary_sewer_context = {
        "sanitary_sewer_year": sanitary_sewer_year,
    }
    return sanitary_sewer_context


def storm_sewer_create_context(storm_sewer_year_init):
    storm_sewer_year = TextInput(
        display_text="Año",
        name="sanitary_sewer_year",
        placeholder="año operacion",
        initial=storm_sewer_year_init,
    )

    storm_sewer_context = {
        "storm_sewer_year": storm_sewer_year,
    }
    return storm_sewer_context
