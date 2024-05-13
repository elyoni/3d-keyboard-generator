import os
from solid2.extensions.bosl2 import (
    cuboid,
    BOTTOM,
)

from solid2.core.object_base import OpenSCADObject

from solid2 import cube, import_stl
from keyboardgenerator.base import XY, Part, LAYER_THICKNESS


class Key(Part):
    spacing: XY
    hole_size: XY
    openscad_file_path: str

    # Create the holes for the key socket
    def draw_pcb_footprint(self) -> OpenSCADObject | None:
        return (
            cube([self.size.x, self.size.y, 5], center=True)
            .rotate(self.angle_rotation)
            .translate([self.center_point.x, self.center_point.y, 0])
        )

    def _draw_plate_footprint(self) -> OpenSCADObject | None:
        return cuboid(
            [self.footprint_pcb.x, self.footprint_pcb.y, 5], anchor=BOTTOM
        ) + cuboid(  # Hole for the key
            [
                self.footprint_pcb.x + 3,
                self.footprint_pcb.y + 3,
                LAYER_THICKNESS + 0.1,
            ],
            anchor=BOTTOM,
        ).up(
            LAYER_THICKNESS / 2
        )  #

    def draw_plate_part_addition_add(self) -> OpenSCADObject | None:
        # Create square with a hole in the middle to add more strength to the plate
        return (
            cuboid(
                [self.hole_size.x + 3, self.hole_size.y + 3, LAYER_THICKNESS],
                anchor=BOTTOM,
            )
            - cuboid(
                [self.hole_size.x + 2, self.hole_size.y + 2, LAYER_THICKNESS + 0.5],
                anchor=BOTTOM,
            )
        ).translate([self.center_point.x, self.center_point.y, LAYER_THICKNESS])

    def _draw_base_pcb(self) -> OpenSCADObject | None:
        if os.path.isfile(self.openscad_file_path):
            return import_stl("../" + self.openscad_file_path)
        else:
            raise FileNotFoundError(
                f"File {self.openscad_file_path} does not exist. Please check the file path."
            )


class CherryMxKey(Key):
    spacing = XY(19.05, 19.05)  # Size
    hole_size = XY(14.03, 14.03)  # Size

    footprint_plate: XY = spacing
    footprint_pcb: XY = hole_size

    openscad_file_path = "./stl/KeyHotswap.stl"

    def _draw_base_pcb(self) -> OpenSCADObject:
        key = (
            super()._draw_base_pcb().up(0.56)
        )  # The 0.12 is the height of the STL object in fusion
        return key


class KailhChocKey(Key):
    spacing = XY(19.05, 19.05)  # Size
    hole_size = XY(14.03, 14.03)  # Size

    footprint_plate: XY = spacing
    footprint_pcb: XY = hole_size

    openscad_file_path = "keyboardgenerator/KeyHotswap.stl"
