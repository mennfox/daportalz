# modules/temp_panels.py

from test import (
    build_htu21d_panel,
    build_scd4x_panel,
    build_bme280_panel,
    build_ahtx0_panel,
    build_room_panel
)

def get_environment_panels():
    return [
        build_htu21d_panel(),
        build_scd4x_panel(),
        build_bme280_panel(),
        build_ahtx0_panel(),
        build_room_panel()
    ]

