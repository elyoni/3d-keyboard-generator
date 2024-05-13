from keyboardgenerator.base import Part, XY
from solid2.core.object_base import OpenSCADObject
from solid2.extensions.bosl2 import cube


class TemplatePart(Part):
    name: str = "templatepart"
    size = XY(1, 1)  # Size
    footprint_plate: XY | None = XY(0, 0)
    footprint_pcb: XY = size

    # Plate functions
    def _draw_plate_footprint(self) -> OpenSCADObject | None:
        return cube([self.footprint_plate.x, self.footprint_plate.y, 5], center=True)

    def draw_plate_part(self) -> OpenSCADObject | None:
        return None

    def draw_plate_part_addition_sub(self) -> OpenSCADObject | None:
        return None

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
