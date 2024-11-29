from solid2.extensions.bosl2 import (
    sphere,
    round2d,
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

import logging


from keyboardgenerator.constants import BASIC_LAYER_THICKNESS, BORDER_RADIUS
from keyboardgenerator.base import XY, Part
from keyboardgenerator.arduino import Arduino
from keyboardgenerator.pins import Pin, PinPlate, PinPcb, PinFromBottomToPlate
from keyboardgenerator.keys import Key, KailhChocKey, CherryMxKey
from keyboardgenerator.plate_text import PlateTextPart
from keyboardgenerator.holes import Holes
from keyboardgenerator.split_keyboard_connectors import SplitKeyboardConnector, TRRSJack
from keyboardgenerator.constants import (
    PART_LABEL_INDEX,
    PROFILE_LABEL_INDEX,
    BASE_PLATE_WIDTH,
    KEY_LABEL_THINKNESS,
    PART_OLD_LABEL_INDEX,
    LABEL_TRANSLATE_LOCATION,
)

log = logging.getLogger(__name__)

ADD_LABEL = False


def get_part_obj(part_type: str):
    if part_type == Arduino.name:
        return Arduino
    elif part_type == Pin.name:
        # print("Part type is Pin")
        return Pin
    elif part_type == PinPlate.name:
        # print("Part type is PlatePin")
        return PinPlate
    elif part_type == PinPcb.name:
        # print("Part type is PcbPin")
        return PinPcb
    elif part_type == PinFromBottomToPlate.name:
        return PinFromBottomToPlate
    elif part_type == PlateTextPart.name:
        return PlateTextPart
    elif part_type == KailhChocKey.name:
        # print("Part type is kailh")
        return KailhChocKey
    elif part_type == SplitKeyboardConnector.name:
        return SplitKeyboardConnector
    elif part_type == TRRSJack.name:
        return TRRSJack
    elif part_type == CherryMxKey.name:
        # print("Part type is cherry")
        return CherryMxKey
    elif part_type == Holes.name:
        return Holes
    # ---> Add HEAR A NEW PART <---
    elif part_type == "":
        return CherryMxKey
    else:
        raise ValueError(
            "Don't know what type of spacing you are using,"
            "add the information in the json file"
            "Look at the readme file for more information. part_type:" + part_type
        )


class Keyboard:
    parts_list: list[Part | Key | Arduino]
    # profile_label_index: int = 10
    plate_border: int

    def __init__(
        self, part_list: list[Part | Key | Arduino], plate_border: int
    ) -> None:
        self.parts_list = part_list
        self.plate_border = plate_border

    @classmethod
    def _get_part_type(cls, part) -> str:
        log.debug(part.labels)
        if part.sm != "":
            return part.sm
        elif part.labels[PROFILE_LABEL_INDEX] is not None:
            return part.labels[PROFILE_LABEL_INDEX].lower()
        # elif part.labels[0] is not None:
        #     log.debug(f"Part type found, {part.labels[0].lower()}")
        #     return part.labels[0].lower()
        elif part.labels[PART_LABEL_INDEX] is not None:
            return part.labels[PART_LABEL_INDEX].lower()
        elif part.labels[PART_OLD_LABEL_INDEX] is not None:
            return part.labels[PART_OLD_LABEL_INDEX].lower()
        else:
            # log.debug(f"No part type found, {part.labels}")
            return ""

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
    def from_kle_obj(
        cls, kle_obj: kle_serial.Keyboard, mirror_side: bool = False
    ) -> "Keyboard":
        # Determine the keyboard spacing
        key_size_scale: XY = cls.get_keyboard_spacing(kle_obj.meta.switchType)
        if kle_obj.meta.notes == "":
            plate_border = 0
        else:
            plate_border = int(kle_obj.meta.notes)

        part_list = []
        for part in kle_obj.keys:
            part_obj = get_part_obj(cls._get_part_type(part))
            log.debug(f"Part type: {part_obj.name}")

            position = XY(part.x, part.y) * key_size_scale
            center_rotation = XY(part.rotation_x, part.rotation_y) * key_size_scale

            # If the object part_obj has a size attribute, use it else use the width and height
            if hasattr(part_obj, "spacing"):
                size = XY(part.width, part.height) * part_obj.spacing
            else:
                size = None

            # label = part.labels[PART_LABEL_INDEX]
            label = part.profile
            part_list.append(
                part_obj(
                    position,
                    part.rotation_angle,
                    center_rotation,
                    size,
                    label,
                    mirror_side=mirror_side,
                )
            )

        return cls(part_list, plate_border)

    # Define a function to create a sphere at a plate_borderiven point
    def create_point_sphere(self, point):
        return sphere(d=1).color("blue").translate(point.x, point.y, -2)

    def _draw_base_plate(self, border=1, add_label=ADD_LABEL) -> OpenSCADObject:
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
                            part.center_point.x + LABEL_TRANSLATE_LOCATION.x,
                            part.center_point.y + LABEL_TRANSLATE_LOCATION.y,
                            BASE_PLATE_WIDTH,
                        )
                        .color("black")
                        .linear_extrude(KEY_LABEL_THINKNESS)
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

        return polygonObj + round2d(r=BORDER_RADIUS, _fn=50)(
            polygon(points)
        ).linear_extrude(BASIC_LAYER_THICKNESS)

    def draw_plate(self) -> OpenSCADObject:
        footprint_objs = union()
        part_objs = union()
        part_addition_sub = union()
        part_addition_add = union()

        for part in self.parts_list:
            draw_plate_footprint = part.draw_plate_footprint()
            if draw_plate_footprint is not None:
                footprint_objs += draw_plate_footprint

            draw_plate_part = part.draw_plate_part()
            if draw_plate_part is not None:
                part_objs += draw_plate_part

            draw_plate_part_addition_sub = part.draw_plate_part_addition_sub()
            if draw_plate_part_addition_sub is not None:
                part_addition_sub += draw_plate_part_addition_sub

            draw_plate_part_addition_add = part.draw_plate_part_addition_add()
            if draw_plate_part_addition_add is not None:
                part_addition_add += draw_plate_part_addition_add
        return (
            self._draw_base_plate(add_label=ADD_LABEL)
            - footprint_objs
            + part_objs
            + part_addition_add
            - part_addition_sub
        )

    def draw_pcb(self) -> OpenSCADObject:
        footprint_objs = []
        part_objs = []
        part_addition_sub = []
        part_addition_add = []

        for part in self.parts_list:
            draw_pcb_footprint = part.draw_pcb_footprint()
            if draw_pcb_footprint is not None:
                footprint_objs += draw_pcb_footprint

            draw_pcb_part = part.draw_pcb_part()
            if draw_pcb_part is not None:
                part_objs += draw_pcb_part

            draw_pcb_part_addition_sub = part.draw_pcb_part_addition_sub()
            if draw_pcb_part_addition_sub is not None:
                part_addition_sub += draw_pcb_part_addition_sub

            draw_pcb_part_addition_add = part.draw_pcb_part_addition_add()
            if draw_pcb_part_addition_add is not None:
                part_addition_add += draw_pcb_part_addition_add

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
            draw_bottom_part_addition_sub = part.draw_bottom_part_addition_sub()
            if draw_bottom_part_addition_sub is not None:
                bottom_objs -= draw_bottom_part_addition_sub

            draw_bottom_part_addition_add = part.draw_bottom_part_addition_add()
            if draw_bottom_part_addition_add is not None:
                bottom_objs += draw_bottom_part_addition_add

        return bottom_objs
