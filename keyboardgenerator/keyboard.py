from solid2.extensions.bosl2 import (
    sphere,
)

from solid2.core.object_base import OpenSCADObject
from solid2 import (
    union,
    polygon,
    text,
)

import pykle_serial as kle_serial
import numpy as np
from scipy.spatial import ConvexHull

from keyboardgenerator.base import XY, Part, LAYER_THICKNESS
from keyboardgenerator.arduino import Arduino
from keyboardgenerator.pins import Pin, PinPlate, PinPcb
from keyboardgenerator.keys import Key, KailhChocKey, CherryMxKey


ADD_LABEL = False


def get_part_obj(part_type: str, part_profile: str | None = None):
    if part_profile == "arduino":
        # print("Part type is arduino")
        return Arduino
    elif part_profile == "pin":
        print("Part type is Pin")
        return Pin
    elif part_profile == "pinplate":
        # print("Part type is PlatePin")
        return PinPlate
    elif part_profile == "pinpcb":
        # print("Part type is PcbPin")
        return PinPcb
    elif part_type == "kailh":
        # print("Part type is kailh")
        return KailhChocKey
    elif part_type == "cherry" or part_type == "":
        # print("Part type is cherry")
        return CherryMxKey
    else:
        raise ValueError(
            "Don't know what type of spacing you are using,"
            "add the information in the json file"
            "Look at the readme file for more information"
        )


class Keyboard:
    parts_list: list[Part | Key | Arduino]
    # profile_label_index: int = 10
    profile_label_index: int = 4
    plate_border: int
    part_label_index: int = 1

    def __init__(
        self, part_list: list[Part | Key | Arduino], plate_border: int
    ) -> None:
        self.parts_list = part_list
        self.plate_border = plate_border

    # @classmethod
    # def from_kle_file(cls, kle_json_file: Path) -> "Keyboard":
    # part_list = []
    # with open(kle_json_file) as json_file:
    # data = json.load(json_file)
    # for part in data["keys"]:
    # part_list.append(from_kle(part))
    # return cls(part_list)

    @classmethod
    def get_keyboard_spacing(cls, switch_type: str) -> XY:
        switch_type = switch_type.lower()
        if switch_type == "cherrymx" or switch_type == "":
            return CherryMxKey.spacing
        elif switch_type == "kailhchockey":
            return KailhChocKey.spacing
        else:
            raise ValueError(
                "Don't know what type of spacing you are using,"
                "add the information in the json file"
                "Look at the readme file for more information    " + switch_type
            )

    @classmethod
    def from_kle_obj(cls, kle_obj: kle_serial.Keyboard) -> "Keyboard":
        # Determine the keyboard spacing
        key_size_scale: XY = cls.get_keyboard_spacing(kle_obj.meta.switchType)
        if kle_obj.meta.notes == "":
            plate_border = 0
        else:
            plate_border = int(kle_obj.meta.notes)

        part_list = []
        for part in kle_obj.keys:
            lable = (
                None
                if part.labels[cls.profile_label_index] is None
                else part.labels[cls.profile_label_index].lower()
            )
            # print("labeels", part.labels, "lable", lable)

            part_obj = get_part_obj(part.sm, lable)

            position = XY(part.x, part.y) * key_size_scale
            center_rotation = XY(part.rotation_x, part.rotation_y) * key_size_scale

            # If the object part_obj has a size attribute, use it else use the width and height
            if hasattr(part_obj, "spacing"):
                size = XY(part.width, part.height) * part_obj.spacing
            else:
                size = None

            label = part.labels[cls.part_label_index]
            part_list.append(
                part_obj(
                    position,
                    part.rotation_angle,
                    center_rotation,
                    size,
                    label,
                )
            )

        return cls(part_list, plate_border)

    # Define a function to create a sphere at a plate_borderiven point
    def create_point_sphere(self, point):
        return sphere(d=1).color("blue").translate(point.x, point.y, -2)

    def _draw_base_plate(self, border=0, add_label=ADD_LABEL) -> OpenSCADObject:
        if add_label:
            move_label = XY(5, 3)
            label_thinkness = 3
        polygonObj = []

        points_list = []
        for part in self.parts_list:
            corner = part.add_border(border).corners
            for corner in corner.get_coruners():
                if add_label:
                    polygonObj += (
                        text(part.text, size=4)
                        # .rotate(180)
                        .translate(
                            part.center_point.x + move_label.x,
                            part.center_point.y + move_label.y,
                            3,
                        )
                        .color("black")
                        .linear_extrude(label_thinkness)
                    )
                points_list.append(corner.get_tuple())

        # Convert the points_raw to a NumPy array for compatibility with ConvexHull
        points_array = np.array(points_list)
        # Calculate the convex hull
        hull = ConvexHull(points_array)
        # Extract the vertices of the convex hull
        hull_points = points_array[hull.vertices]

        # Close the shape by adding the first point at the end
        hull_points = np.append(hull_points, [hull_points[0]], axis=0)
        # Extract x and y coordinates from the hull points
        points = []
        x, y = zip(*hull_points)
        for _x, _y in zip(x, y):
            points.append((_x, _y))

        return polygonObj + polygon(points).linear_extrude(LAYER_THICKNESS)

    def draw_plate(self) -> OpenSCADObject:
        footprint_objs = union()
        part_objs = union()
        part_addition_sub = union()
        part_addition_add = union()

        for part in self.parts_list:
            footprint_objs += part.draw_plate_footprint()
            part_objs += part.draw_plate_part()
            part_addition_sub += part.draw_plate_part_addition_sub()
            part_addition_add += part.draw_plate_part_addition_add()
        return (
            self._draw_base_plate(add_label=ADD_LABEL)
            - footprint_objs
            + part_objs
            - part_addition_sub
            + part_addition_add
        )

    def draw_pcb(self) -> OpenSCADObject:
        # footprint_objs = union()
        # part_objs = union()
        # part_addition_sub = union()
        # part_addition_add = union()

        footprint_objs = []
        part_objs = []
        part_addition_sub = []
        part_addition_add = []

        for part in self.parts_list:
            footprint_objs += part.draw_pcb_footprint()
            part_objs += part.draw_pcb_part()
            part_addition_sub += part.draw_pcb_part_addition_sub()
            part_addition_add += part.draw_pcb_part_addition_add()

        # return part_objs
        return (
            self._draw_base_plate(add_label=ADD_LABEL)
            - footprint_objs
            + part_objs
            - part_addition_sub
            + part_addition_add
        )

    def draw_bottom(self) -> OpenSCADObject:
        bottom_objs = self._draw_base_plate(add_label=ADD_LABEL)

        for part in self.parts_list:
            bottom_objs -= part.draw_bottom_part_addition_sub()
            bottom_objs += part.draw_bottom_part_addition_add()

        return bottom_objs


# Create Plate: _base_plate - part.footprint + part.plate_openscad_obj + part.plate_additional_add - part.plate_additional_sub

# self._draw_base_plate(border=)
#    - sum(part.draw_plate_footprint)
#    + sum(part.plate_openscad_obj)
#    - sum(part.plate_additional_sub)


# draw_base_plate_xxx - will affect the base plate of the keyboard
# part.draw_base_plate_sub()
# part.draw_base_plate_add()
# draw_plate - Will affect the plate it self
# part.draw_plate_add()
# part.draw_plate_sub()
# part.draw_sub_add()
# part.draw_sub_sub()
