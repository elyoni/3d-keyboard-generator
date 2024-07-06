from solid2.extensions.bosl2 import cube, cuboid, cylinder, union, BOTTOM
from solid2.core.object_base import OpenSCADObject

from keyboardgenerator.constants import BASIC_LAYER_THICKNESS
from keyboardgenerator.base import (
    Y,
    Z,
    XY,
    Part,
)


class Arduino(Part):
    name: str = "arduino"
    size = XY(19, 37)  # Size
    footprint_plate: XY | None = None  # XY(0, 0)
    footprint_pcb: XY = size

    pcb_size: tuple[float, float, float] = (size.x, size.y, 1)  # [mm,mm,mm]
    # pins_socket: tuple[float, float, float] = (3, 31.5, 4)  # [mm,mm,mm]
    pins_diameter: float = 1.5
    pins_row_space: int = 15  # mm
    pins_number: int = 12  # Each side
    pins_space: float = 2.54  # mm

    arduino_header: tuple[float, float, float] = (11, 10, 4)  # [mm,mm,mm]

    holder_pole_size: tuple[float, float, float] = (3, 3, 4)  # [mm,mm,mm]
    holder_tooth_size: tuple[float, float, float] = (3, 3.5, 1)  # [mm,mm,mm]

    # Draw the pins for the arduino header
    def _draw_pings(self) -> OpenSCADObject:
        pins_socket_obj: OpenSCADObject = union()
        for i in range(self.pins_number):
            pins_socket_obj += cylinder(
                d=self.pins_diameter, h=8, _fn=30, center=True
            ).translateY(i * self.pins_space)
        pins_socket_obj = pins_socket_obj.translateY(-12.7)  # TODO, need to reduce it
        return pins_socket_obj

    def draw_bottom_part_addition_sub(self) -> OpenSCADObject | None:
        print("draw_bottom_part_addition_sub")
        return cuboid(self.arduino_header, anchor=BOTTOM).translate(
            self.center_point.x,
            self.center_point.y - self.size.y / 2 + self.arduino_header[Y] / 2,
            -self.arduino_header[Z] + BASIC_LAYER_THICKNESS / 2,
        )

    def _draw_pcb_part(self) -> OpenSCADObject | None:
        baseLayer: OpenSCADObject = cube(self.pcb_size, anchor=BOTTOM)
        pins_socket_obj: OpenSCADObject = self._draw_pings()

        return (
            baseLayer
            - pins_socket_obj.translateX(-self.pins_row_space / 2)
            - pins_socket_obj.translateX(self.pins_row_space / 2)
        )

    def _draw_plate_footprint(self) -> OpenSCADObject | None:
        return None
