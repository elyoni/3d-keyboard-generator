from solid2.extensions.bosl2 import (
    cuboid,
    cylinder,
    BOTTOM,
)

from solid2.core.object_base import OpenSCADObject
from solid2 import union, debug

from keyboardgenerator.constants import BASIC_LAYER_THICKNESS
from keyboardgenerator.base import (
    XY,
    Part,
)


class Pin(Part):
    name: str = "pin"
    draw_delta = 0.5
    hight: float = 10  # Original Value was 5
    inner_high: float = 5 + BASIC_LAYER_THICKNESS + draw_delta  # + 10
    diameter_inner: float = 2
    diameter_outter: float = 4
    scraws_outter_diameter = 2.5
    scraws_header_diameter = diameter_outter + 2.5

    size = XY(diameter_outter, diameter_outter)
    footprint_plate: XY = size
    footprint_pcb: XY = XY(0, 0)

    base_cube_fill: OpenSCADObject = cuboid(
        [size.x, size.y, BASIC_LAYER_THICKNESS], anchor=BOTTOM
    )

    cylihder_inner: OpenSCADObject = cylinder(
        d=diameter_inner, h=inner_high, _fn=50, anchor=BOTTOM
    )

    cylihder_outter: OpenSCADObject = cylinder(
        d=diameter_outter, h=hight, _fn=50, anchor=BOTTOM
    )

    scraws_chamfer: OpenSCADObject = cylinder(
        d=scraws_outter_diameter, h=BASIC_LAYER_THICKNESS, _fn=50, anchor=BOTTOM
    ) + cylinder(
        d1=scraws_outter_diameter,
        d2=scraws_header_diameter,
        h=BASIC_LAYER_THICKNESS / 3,
        _fn=50,
        anchor=BOTTOM,
    ).up(
        BASIC_LAYER_THICKNESS - BASIC_LAYER_THICKNESS / 3
    )

    def _draw_pcb_part(self) -> OpenSCADObject:
        return self.base_cube_fill + self.cylihder_outter - self.cylihder_inner

    def _draw_plate_part(self) -> OpenSCADObject:
        return (
            self.base_cube_fill
            + self.cylihder_outter
            - debug(
                self.cylihder_inner.translateZ(BASIC_LAYER_THICKNESS + self.draw_delta)
            )
        )

    def _draw_plate_footprint(self) -> OpenSCADObject:
        return self.cylihder_outter


class PinPlate(Pin):
    name: str = "pinplate"

    def draw_pcb_footprint(self) -> OpenSCADObject:
        return self.cylihder_inner.rotate(self.angle_rotation).translate(
            [self.center_point.x, self.center_point.y, 0]
        )

    def draw_pcb_part(self) -> OpenSCADObject:
        return union()

    def draw_plate_part(self) -> OpenSCADObject:
        return debug(
            self._draw_plate_part()
            .rotate(self.angle_rotation)
            .translate([self.center_point.x, self.center_point.y, 0])
        )

    def draw_pcb_part_addition_sub(self) -> OpenSCADObject:
        return debug(
            self.scraws_chamfer + self.cylihder_inner.translateZ(-3)
        ).translate([self.center_point.x, self.center_point.y, 0])


class PinPcb(Pin):
    name: str = "pinpcb"

    def draw_plate_footprint(self) -> OpenSCADObject:
        return None

    def draw_plate_part(self) -> OpenSCADObject:
        return None

    def draw_pcb_part(self) -> OpenSCADObject:
        return (
            self._draw_pcb_part()
            .rotate(self.angle_rotation)
            .translate([self.center_point.x, self.center_point.y, 0])
        )

    def draw_pcb_part_addition_sub(self) -> OpenSCADObject:
        return self.cylihder_inner.rotate(self.angle_rotation).translate(
            [self.center_point.x, self.center_point.y, 0]
        )

    def draw_bottom_part_addition_sub(self) -> OpenSCADObject:
        return (self.scraws_chamfer + self.cylihder_inner).translate(
            [self.center_point.x, self.center_point.y, 0]
        )
