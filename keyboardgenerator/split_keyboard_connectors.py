from solid2.core.object_base import OpenSCADObject
from keyboardgenerator.base import Part, XY
from keyboardgenerator.constants import BASIC_LAYER_THICKNESS
from solid2.extensions.bosl2 import cube, cuboid, BOTTOM, cylinder, FWD

from solid2 import debug

# from solid2 import (
#     union,
# )


class SplitKeyboardConnector(Part):
    name: str = "split_keyboard_connector"
    size = XY(14.3, 6.5)  # Size
    footprint_plate = None  # XY(0, 0)
    footprint_pcb = size

    # Plate functions
    def _draw_plate_footprint(self) -> OpenSCADObject | None:
        if self.footprint_plate is None:
            return None
        return cube([self.footprint_plate.x, self.footprint_plate.y, 5], center=True)

    def _draw_plate_part(self) -> OpenSCADObject | None:
        return None

    def _draw_plate_part_addition_sub(self) -> OpenSCADObject | None:
        return None

    def _draw_plate_part_addition_add(self) -> OpenSCADObject | None:
        return None

    # Return the part on the PCB layer as a openscad object
    def _draw_pcb_part(self) -> OpenSCADObject | None:
        return cube([self.footprint_pcb.x, self.footprint_pcb.y, 5], center=True)

    def _draw_pcb_part_addition_add(self) -> OpenSCADObject | None:
        return None

    # Bottom functions
    def _draw_bottom_part_addition_sub(self) -> OpenSCADObject | None:
        return None

    def _draw_bottom_part_addition_add(self) -> OpenSCADObject | None:
        return None


class TRRSJack(SplitKeyboardConnector):
    socket_hold_size_diameter: float = 5.3
    socket_hole_size_height: float = 2.2

    socket_body_size: XY = XY(6.2, 12.4)
    name: str = "trrs"
    size: XY = XY(socket_body_size.x + 2, socket_body_size.y + socket_hole_size_height)
    footprint_plate: XY = XY(0, 0)
    footprint_pcb: XY = size

    def _draw_pcb_part_addition_sub(self) -> OpenSCADObject | None:
        socket_hole = (
            cylinder(
                d=self.socket_hold_size_diameter,
                h=self.socket_hole_size_height + 10,
                anchor=BOTTOM,
            )
            .rotateX(90)
            .translate(0, -self.socket_body_size.x, BASIC_LAYER_THICKNESS + 1 / 3)
        )
        return socket_hole

    def _draw_bottom_part_addition_sub(self) -> OpenSCADObject | None:
        return cuboid([self.socket_body_size * 2.5, BASIC_LAYER_THICKNESS])

    def _draw_pcb_part(self) -> OpenSCADObject:
        socket_hole = cylinder(
            d=self.socket_hold_size_diameter,
            h=self.socket_hole_size_height,
            anchor=BOTTOM,
        ).rotateX(90)

        socket_body = cube(
            [self.socket_body_size.x, self.socket_body_size.y, 5.2], anchor=FWD
        ).up(0.2)

        pj_320a_connector = socket_body + socket_hole
        pj_320a_connector = pj_320a_connector
        socket_pj_320a_connector = (
            cube(
                [self.size.x, self.size.y + self.socket_hole_size_height, 5], anchor=FWD
            ).translate([0, -self.socket_hole_size_height])
            - pj_320a_connector
        )
        # socket_pj_320a_connectorOrigin = socket_pj_320a_connector
        socket_pj_320a_connector = socket_pj_320a_connector.translate(
            [
                0,
                -self.socket_body_size.x,
                BASIC_LAYER_THICKNESS + 1 / 3,
            ]
        )

        return socket_pj_320a_connector
