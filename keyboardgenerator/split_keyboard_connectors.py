from solid2.core.object_base import OpenSCADObject
from keyboardgenerator.base import Part, XY
from solid2.extensions.bosl2 import cube, BOTTOM, cylinder


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

    def draw_plate_part(self) -> OpenSCADObject | None:
        return None

    def draw_plate_part_addition_sub(self) -> OpenSCADObject | None:
        return None

    def draw_plate_part_addition_add(self) -> OpenSCADObject | None:
        return None

    # PCB functions
    def draw_pcb_footprint(self) -> OpenSCADObject | None:
        return None

    # Return the part on the PCB layer as a openscad object
    def _draw_pcb_part(self) -> OpenSCADObject | None:
        return cube([self.footprint_pcb.x, self.footprint_pcb.y, 5], center=True)

    def draw_pcb_part_addition_sub(self) -> OpenSCADObject | None:
        return None

    def draw_pcb_part_addition_add(self) -> OpenSCADObject | None:
        return None

    # Bottom functions
    def draw_bottom_part_addition_sub(self) -> OpenSCADObject | None:
        return None

    def draw_bottom_part_addition_add(self) -> OpenSCADObject | None:
        return None


class TRRSJack(SplitKeyboardConnector):
    name: str = "trrs"
    size: XY = XY(8, 14.2)

    socket_size: XY = XY(6, 12.2)
    footprint_plate: XY = XY(0, 0)
    footprint_pcb: XY = size

    def _draw_pcb_part(self) -> OpenSCADObject:
        pj_320a_connector = cube(
            [self.socket_size.x, self.socket_size.y, 5], anchor=BOTTOM
        ).up(2) + cylinder(d=5, h=2.2, anchor=BOTTOM).rotateX(90).translate(
            [0, -self.socket_size.x / 2 / 2, 2 + self.socket_size.y / 2]
        )
        return (
            cube([self.size.x, self.size.y, 6], anchor=BOTTOM)
            - pj_320a_connector.debug()
        )
