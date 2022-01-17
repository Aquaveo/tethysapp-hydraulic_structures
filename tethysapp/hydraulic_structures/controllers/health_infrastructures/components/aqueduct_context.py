from tethys_gizmos.gizmo_options.select_input import SelectInput
from tethys_gizmos.gizmo_options.text_input import TextInput


def hydraulic_dam_create_context(
    hydraulic_dam_purposes_init,
    hydraulic_dam_year_init,
    hydraulic_dam_height_init,
    hydraulic_dam_volume_init,
):
    hydraulic_dam_purposes = SelectInput(
        display_text="Proposito",
        name="hydraulic_dam_purposes",
        multiple=True,
        options=[
            ("Hidroelectrica", "hidroelectrica"),
            ("Riego", "riego"),
            ("Agua Potable", "agua_potable"),
            ("Control Inondaciones", "control_inondaciones"),
        ],
        initial=hydraulic_dam_purposes_init,
    )
    hydraulic_dam_year = TextInput(
        display_text="Anio",
        name="hydraulic_dam_year",
        placeholder="anio operacion",
        initial=hydraulic_dam_year_init,
    )
    hydraulic_dam_height = TextInput(
        display_text="Altura",
        name="hydraulic_dam_height",
        placeholder="Altura",
        initial=hydraulic_dam_height_init,
    )
    hydraulic_dam_volume = TextInput(
        display_text="Volumen Almacenado",
        name="hydraulic_dam_volume",
        placeholder="volumen almacenado",
        initial=hydraulic_dam_volume_init,
    )

    hydraulic_dam_context = {
        "hydraulic_dam_purposes": hydraulic_dam_purposes,
        "hydraulic_dam_year": hydraulic_dam_year,
        "hydraulic_dam_height": hydraulic_dam_height,
        "hydraulic_dam_volume": hydraulic_dam_volume,
    }
    return hydraulic_dam_context


def well_create_context(well_year_init):
    well_year = TextInput(
        display_text="Anio",
        name="well_year",
        placeholder="anio operacion",
        initial=well_year_init,
    )

    well_context = {
        "well_year": well_year,
    }
    return well_context


def pipe_line_create_context(pipe_line_year_init):
    pipe_line_year = TextInput(
        display_text="Anio",
        name="pipe_line_year",
        placeholder="anio operacion",
        initial=pipe_line_year_init,
    )

    pipe_line_context = {
        "pipe_line_year": pipe_line_year,
    }
    return pipe_line_context


def storage_tank_create_context(storage_tank_year_init):
    storage_tank_year = TextInput(
        display_text="Anio",
        name="storage_tank_year",
        placeholder="anio operacion",
        initial=storage_tank_year_init,
    )

    storage_tank_context = {
        "storage_tank_year": storage_tank_year,
    }
    return storage_tank_context


def gravity_pipe_line_create_context(gravity_pipe_line_year_init):
    gravity_pipe_line_year = TextInput(
        display_text="Anio",
        name="gravity_pipe_line_year",
        placeholder="anio operacion",
        initial=gravity_pipe_line_year_init,
    )

    gravity_pipe_line_context = {
        "gravity_pipe_line_year": gravity_pipe_line_year,
    }
    return gravity_pipe_line_context


def distribution_network_create_context(distribution_network_year_init):
    distribution_network_year = TextInput(
        display_text="Anio",
        name="distribution_network_year",
        placeholder="anio operacion",
        initial=distribution_network_year_init,
    )

    distribution_network_context = {
        "distribution_network_year": distribution_network_year,
    }
    return distribution_network_context
