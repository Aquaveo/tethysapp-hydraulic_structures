from tethys_gizmos.gizmo_options.select_input import SelectInput
from tethys_gizmos.gizmo_options.text_input import TextInput


def river_protection_wall_create_context(
    river_protection_wall_year_init,
):
    river_protection_wall_year = TextInput(
        display_text="Año",
        name="river_protection_wall_year",
        placeholder="año operacion",
        initial=river_protection_wall_year_init,
    )

    river_protection_wall_context = {
        "river_protection_wall_year": river_protection_wall_year,
    }
    return river_protection_wall_context
