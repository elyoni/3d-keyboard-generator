from solid2.extensions.bosl2 import (
    cuboid,
    cylinder,
    BOTTOM,
)

from solid2.core.object_base import OpenSCADObject

# from solid2 import debug

# from solid2 import union

from keyboardgenerator.constants import BASIC_LAYER_THICKNESS, CHERRY_MX_PCB_HEIGHT
from keyboardgenerator.base import (
    XY,
    Part,
)


class Pin(Part):
    name: str = "pin"
    draw_delta = 0.5
    height: float = CHERRY_MX_PCB_HEIGHT  # 10  # Original Value was 5
    inner_high: float = 5 + BASIC_LAYER_THICKNESS + draw_delta  # + 10
    diameter_inner: float = 2
    diameter_outer: float = 4
    scraws_outer_diameter = 2.5
    scraws_header_diameter = diameter_outer + 2.5

    size = XY(diameter_outer, diameter_outer)
    footprint_plate: XY = XY(0, 0)  # = size
    footprint_pcb: XY = XY(0, 0)

    base_cube_fill: OpenSCADObject = cuboid(
        [size.x, size.y, BASIC_LAYER_THICKNESS], anchor=BOTTOM
    )

    cylihder_inner: OpenSCADObject = cylinder(
        d=diameter_inner, h=inner_high, _fn=50, anchor=BOTTOM
    )

    cylihder_outer: OpenSCADObject = cylinder(
        d=diameter_outer, h=height, _fn=50, anchor=BOTTOM
    )

    scraws_chamfer: OpenSCADObject = cylinder(
        d=scraws_outer_diameter, h=BASIC_LAYER_THICKNESS, _fn=50, anchor=BOTTOM
    ) + cylinder(
        d=diameter_outer,
        h=BASIC_LAYER_THICKNESS,
        _fn=50,
        anchor=BOTTOM,
    ).up(
        1
    )

    def _draw_pcb_part(self) -> OpenSCADObject | None:
        return None

    def _draw_plate_footprint(self) -> OpenSCADObject:
        return None


# Pin between the plate and the pcb layers
class PinPlate(Pin):
    name: str = "pinplate"

    def _draw_plate_part(self) -> OpenSCADObject:
        return (
            self.base_cube_fill
            + self.cylihder_outer
            - self.cylihder_inner.translateZ(self.draw_delta)
        )

    def _draw_plate_footprint(self) -> OpenSCADObject:
        return self.base_cube_fill

    def _draw_pcb_footprint(self) -> OpenSCADObject:
        return self.cylihder_inner

    def _draw_pcb_part_addition_sub(self) -> OpenSCADObject:
        return self.scraws_chamfer + self.cylihder_inner.translateZ(-3)

    def _draw_plate_part_addition_sub(self) -> OpenSCADObject | None:
        return self.cylihder_inner.translateZ(0.2)


class PinPcb(Pin):
    name: str = "pinpcb"

    def _draw_pcb_part(self) -> OpenSCADObject:
        return self.base_cube_fill + self.cylihder_outer - self.cylihder_inner

    def _draw_pcb_part_addition_sub(self) -> OpenSCADObject:
        return self.cylihder_inner.rotate(self.angle_rotation)

    def _draw_bottom_part_addition_sub(self) -> OpenSCADObject:
        return self.scraws_chamfer + self.cylihder_inner


class PinFromBottomToPlate(PinPlate, PinPcb):
    name: str = "pinb2t"

    def _draw_pcb_part_addition_sub(self) -> OpenSCADObject:
        return self.cylihder_inner.translateZ(-1)
