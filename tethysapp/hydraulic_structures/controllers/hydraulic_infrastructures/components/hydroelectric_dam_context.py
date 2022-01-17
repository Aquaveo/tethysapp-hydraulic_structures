from tethys_gizmos.gizmo_options.select_input import SelectInput
from tethys_gizmos.gizmo_options.text_input import TextInput


def hydroelectric_dam_create_context(
    hydroelectric_dam_year_init,
):
    hydroelectric_dam_year = TextInput(
        display_text="Anio",
        name="dams_and_resevoirs_year",
        placeholder="anio operacion",
        initial=hydroelectric_dam_year_init,
    )

    hydroelectric_dam_context = {
        "hydroelectric_dam_year": hydroelectric_dam_year,
    }
    return hydroelectric_dam_context
