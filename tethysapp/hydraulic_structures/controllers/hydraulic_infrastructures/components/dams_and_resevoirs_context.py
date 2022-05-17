from tethys_gizmos.gizmo_options.select_input import SelectInput
from tethys_gizmos.gizmo_options.text_input import TextInput


def dams_and_resevoirs_create_context(
    dams_and_resevoirs_purposes_init,
    dams_and_resevoirs_year_init,
    dams_and_resevoirs_height_init,
    dams_and_resevoirs_volume_init,
):
    dams_and_resevoirs_purposes = SelectInput(
        display_text="Principal Propósito",
        name="dams_and_resevoirs_purposes",
        multiple=True,
        options=[
            ("Hidroelectrica", "hidroelectrica"),
            ("Riego", "riego"),
            ("Agua Potable", "agua_potable"),
            ("Control Inondaciones", "control_inondaciones"),
        ],
        initial=dams_and_resevoirs_purposes_init,
    )
    dams_and_resevoirs_year = TextInput(
        display_text="Año",
        name="dams_and_resevoirs_year",
        placeholder="año operación",
        initial=dams_and_resevoirs_year_init,
    )
    dams_and_resevoirs_height = TextInput(
        display_text="Altura",
        name="dams_and_resevoirs_height",
        placeholder="Altura",
        initial=dams_and_resevoirs_height_init,
    )
    dams_and_resevoirs_volume = TextInput(
        display_text="Volumen de Almacenamiento",
        name="dams_and_resevoirs_volume",
        placeholder="volumen de almacenamiento",
        initial=dams_and_resevoirs_volume_init,
    )

    dams_and_resevoirs_context = {
        "dams_and_resevoirs_purposes": dams_and_resevoirs_purposes,
        "dams_and_resevoirs_year": dams_and_resevoirs_year,
        "dams_and_resevoirs_height": dams_and_resevoirs_height,
        "dams_and_resevoirs_volume": dams_and_resevoirs_volume,
    }
    return dams_and_resevoirs_context
