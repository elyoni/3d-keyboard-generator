import os
from solid2.extensions.bosl2 import (
    cuboid,
    BOTTOM,
    RIGHT,
)

from solid2.core.object_base import OpenSCADObject

from solid2 import cube, import_stl, color, debug

from keyboardgenerator.constants import BASIC_LAYER_THICKNESS
from keyboardgenerator.base import XY, Part


class Key(Part):
    spacing: XY
    hole_size: XY
    openscad_file_path: str
    hole_wall_thickness: float = 3

    # Create the holes for the key socket
    def draw_pcb_footprint(self) -> OpenSCADObject | None:
        return (
            cube([self.size.x, self.size.y, 5], center=True)
            .rotate(self.angle_rotation)
            .translate([self.center_point.x, self.center_point.y, 0])
        )

    def _draw_plate_footprint(self) -> OpenSCADObject | None:
        return cuboid(
            [self.hole_size.x, self.hole_size.y, 5], anchor=BOTTOM
        ) + cuboid(  # Hole for the key
            [
                self.hole_size.x - self.hole_wall_thickness,
                self.hole_size.y - self.hole_wall_thickness,
                BASIC_LAYER_THICKNESS + 0.1,
            ],
            anchor=BOTTOM,
        ).up(
            BASIC_LAYER_THICKNESS / 2
        )

    def draw_plate_part_addition_add(self) -> OpenSCADObject | None:
        # Create square with a hole in the middle to add more strength to the plate
        return (
            (
                color("red")(
                    cuboid(
                        [
                            self.hole_size.x + self.hole_wall_thickness,
                            self.hole_size.y + self.hole_wall_thickness,
                            BASIC_LAYER_THICKNESS + 0.4,
                        ],
                        anchor=BOTTOM,
                    )
                )
                - (
                    cuboid(
                        [
                            self.hole_size.x + 2,
                            self.hole_size.y + 2,
                            BASIC_LAYER_THICKNESS + 3,
                        ],
                        anchor=BOTTOM,
                    )
                )
            )
            .rotate(self.angle_rotation)
            .translate(
                [self.center_point.x, self.center_point.y, BASIC_LAYER_THICKNESS]
            )
        )

    def _draw_plate_part_addition_sub(self) -> OpenSCADObject | None:
        return debug(
            cuboid(
                [self.hole_size.x, self.hole_size.y, BASIC_LAYER_THICKNESS],
                anchor=BOTTOM,
            ).down(0)
        )

    def _draw_pcb_part(self) -> OpenSCADObject | None:
        if os.path.isfile(self.openscad_file_path):
            stl_obj = import_stl("../" + self.openscad_file_path)
            return (
                stl_obj.mirror(RIGHT)
                if (self.mirror_affect and self.mirror_side)
                else stl_obj
            )
        else:
            raise FileNotFoundError(
                f"File {self.openscad_file_path} does not exist. Please check the file path."
            )


class CherryMxKey(Key):
    name: str = "cherry"
    mirror_affect: bool = True
    spacing = XY(19.05, 19.05)  # Size
    hole_size = XY(14.03, 14.03)  # Size

    footprint_plate: XY = spacing
    footprint_pcb: XY = hole_size

    openscad_file_path = "./stl/KeyHotswap.stl"

    def _draw_pcb_part(self) -> OpenSCADObject:
        key = (
            super()._draw_pcb_part().up(0.56)
        )  # The 0.12 is the height of the STL object in fusion
        return key


class KailhChocKey(Key):
    name: str = "kailhchoc"
    mirror_affect: bool = True
    spacing = XY(19.05, 19.05)  # Size
    hole_size = XY(14.03, 14.03)  # Size

    footprint_plate: XY = spacing
    footprint_pcb: XY = hole_size

    openscad_file_path = "keyboardgenerator/KeyHotswap.stl"
