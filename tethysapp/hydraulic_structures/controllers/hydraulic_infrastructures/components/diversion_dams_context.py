from tethys_gizmos.gizmo_options.select_input import SelectInput
from tethys_gizmos.gizmo_options.text_input import TextInput


def diversion_dam_create_context(
    diversion_dam_year_init,
):
    diversion_dam_year = TextInput(
        display_text="Año",
        name="diversion_dam_year",
        placeholder="año operacion",
        initial=diversion_dam_year_init,
    )

    diversion_dam_context = {
        "diversion_dam_year": diversion_dam_year,
    }
    return diversion_dam_context
