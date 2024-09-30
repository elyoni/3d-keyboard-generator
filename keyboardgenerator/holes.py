from keyboardgenerator.constants import BASIC_LAYER_THICKNESS
from keyboardgenerator.base import Part, XY
from solid2.core.object_base import OpenSCADObject
from solid2.extensions.bosl2 import cuboid, BOTTOM

# from solid2 import debug


class Holes(Part):
    name: str = "hole"
    spacing = XY(14.03, 14.03)  # Size
    footprint_plate: XY | None = XY(0, 0)
    footprint_pcb: XY = XY(0, 0)

    # Plate functions
    def _draw_plate_part(self) -> OpenSCADObject | None:
        return None

    def _draw_plate_part_addition_sub(self) -> OpenSCADObject | None:
        return None

    def _draw_plate_part_addition_add(self) -> OpenSCADObject | None:
        return None

    # PCB functions
    def _draw_pcb_part(self) -> OpenSCADObject | None:
        return None

    def _draw_pcb_part_addition_sub(self) -> OpenSCADObject | None:
        height = BASIC_LAYER_THICKNESS + 2
        return cuboid([self.size, height], anchor=BOTTOM).translateZ(-1)

    def _draw_pcb_part_addition_add(self) -> OpenSCADObject | None:
        return None

    # Bottom functions
    def _draw_bottom_part_addition_sub(self) -> OpenSCADObject | None:
        return None

    def _draw_bottom_part_addition_add(self) -> OpenSCADObject | None:
        return None
