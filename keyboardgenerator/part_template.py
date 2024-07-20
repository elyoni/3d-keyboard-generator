from keyboardgenerator.base import Part, XY
from solid2.core.object_base import OpenSCADObject


class TemplatePart(Part):
    name: str = "templatepart"
    size = XY(1, 1)  # Size
    footprint_plate: XY | None = XY(0, 0)
    footprint_pcb: XY = size

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
        return None

    def _draw_pcb_part_addition_add(self) -> OpenSCADObject | None:
        return None

    # Bottom functions
    def _draw_bottom_part_addition_sub(self) -> OpenSCADObject | None:
        return None

    def _draw_bottom_part_addition_add(self) -> OpenSCADObject | None:
        return None
