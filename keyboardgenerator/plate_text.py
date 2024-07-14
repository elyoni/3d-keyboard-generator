from keyboardgenerator.base import Part, XY
from solid2.core.object_base import OpenSCADObject
from solid2 import debug
from keyboardgenerator.constants import BASIC_LAYER_THICKNESS
from solid2.extensions.bosl2 import cube, text3d, UP, union


class PlateTextPart(Part):
    name: str = "platetext"
    size = XY(1, 1)  # Size
    footprint_plate: XY | None = XY(0, 0)
    footprint_pcb: XY = size
    text = ""

    # Plate functions
    def _draw_plate_footprint(self) -> OpenSCADObject | None:
        return cube([self.footprint_plate.x, self.footprint_plate.y, 5], center=True)

    def _draw_text(self, text: str, y_offset: float = 0) -> OpenSCADObject:
        line_text = (
            text3d(
                text,
                size=7,
                height=1,
                direction=UP,
                atype="ycenter",
                font="Shantell Sans ExtraBold",
            )
            .rotate(180, [1, 0, 0])
            .translate(
                [
                    self.center_point.x,
                    self.center_point.y + y_offset,
                    0,
                ]
            )
            .color("black")
        )
        return line_text

    def draw_plate_part(self) -> OpenSCADObject | None:
        return None

    def draw_plate_part_addition_sub(self) -> OpenSCADObject | None:
        lines = self.text.split("\n")
        if len(lines) > 0:
            texts = union()
            for line_number, line_text in enumerate(lines):
                texts += self._draw_text(line_text, line_number * 10)

        return debug(texts)

    def draw_plate_part_addition_add(self) -> OpenSCADObject | None:
        return None

    # PCB functions
    # # Return the part on the PCB layer as a openscad object
    def _draw_pcb_part(self) -> OpenSCADObject | None:
        return None

    def draw_pcb_footprint(self) -> OpenSCADObject | None:
        return None

    def draw_pcb_part_addition_sub(self) -> OpenSCADObject | None:
        return None

    def draw_pcb_part_addition_add(self) -> OpenSCADObject | None:
        return None

    # Bottom functions
    def draw_bottom_part_addition_sub(self) -> OpenSCADObject | None:
        return None

    def draw_bottom_part_addition_add(self) -> OpenSCADObject | None:
        return None
