from keyboardgenerator.base import Part, XY
from solid2.core.object_base import OpenSCADObject
from solid2.extensions.bosl2 import cube, text3d, UP, union, RIGHT

# from solid2 import debug


class PlateTextPart(Part):
    name: str = "platetext"
    mirror_affect: bool = True  # Affect the mirror of the part, disable mirror for text
    size = XY(1, 1)  # Size
    footprint_plate: XY | None = XY(0, 0)
    footprint_pcb: XY = size
    text = ""

    # Plate functions
    def _draw_plate_footprint(self) -> OpenSCADObject | None:
        return cube([self.footprint_plate.x, self.footprint_plate.y, 5], center=True)

    def _draw_text(
        self, text: str, mirror_text: bool, max_char_offset: int, y_offset: float = 0
    ) -> OpenSCADObject:
        translate_x = (
            -(self.center_point.x + max_char_offset * 5)
            if mirror_text
            else self.center_point.x
        )
        line_text = (
            text3d(
                text,
                size=7,
                height=1,
                direction=UP,
                atype="ycenter",
                font="Shantell Sans ExtraBold",
            )
            .rotate(180, RIGHT)
            .translate(
                [
                    translate_x,
                    self.center_point.y + y_offset,
                    0,
                ]
            )
            .color("black")
        )

        return (
            line_text.mirror(RIGHT)
            if (self.mirror_affect and self.mirror_side)
            else line_text
        )

    def draw_plate_part(self) -> OpenSCADObject | None:
        return None

    def draw_plate_part_addition_sub(self) -> OpenSCADObject | None:
        lines = self.text.split("\n")
        if len(lines) > 0:
            max_char = 0
            for line in lines:
                max_char = len(line) if len(line) > max_char else max_char
            texts = union()
            for line_number, line_text in enumerate(lines):
                texts += self._draw_text(
                    line_text, self.mirror_side, max_char, line_number * 10
                )

        return texts if (self.mirror_affect and self.mirror_side) else texts

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
