#!/usr/bin/env python3

import numpy as np

from solid2.extensions.bosl2 import cube

from solid2.core.object_base import OpenSCADObject
from solid2 import union

X = 0
Y = 1
Z = 2

LAYER_THICKNESS = 2.16


class XY:
    x: float
    y: float

    def __init__(self, x: float, y: float) -> None:
        self.x = x
        self.y = y

    def get_tuple(self) -> tuple[float, float]:
        return (self.x, self.y)

    @classmethod
    def from_np(cls, np: np.ndarray):
        return cls(float(np[0]), float(np[1]))

    def __str__(self):
        return f"{self.x}, {self.y}"

    def __truediv__(self, other):
        if isinstance(other, XY):
            result_x = self.x / other.x
            result_y = self.y / other.y
            return type(self)(result_x, result_y)
        elif isinstance(other, int | float):
            result_x = self.x / other
            result_y = self.y / other
            return type(self)(result_x, result_y)
        else:
            # Raise an exception if the other object is not a XY
            raise ValueError("Dividing is only supported between two XY instances")

    def __mul__(self, other):
        # Check if the other object is also a XY
        if isinstance(other, XY):
            # Perform element-wise multiplication
            result_x = self.x * other.x
            result_y = self.y * other.y
            return type(self)(result_x, result_y)
        elif isinstance(other, int | float):
            result_x = self.x * other
            result_y = self.y * other
            return type(self)(result_x, result_y)
        else:
            # Raise an exception if the other object is not a XY
            raise ValueError(
                "Multiplication is only supported between two XY instances"
            )

    def __add__(self, other):
        # Check if the other object is also a XY
        if isinstance(other, XY):
            # Perform element-wise addition
            result_x = self.x + other.x
            result_y = self.y + other.y
            return type(self)(result_x, result_y)
        if isinstance(other, int | float):
            result_x = self.x + other
            result_y = self.y + other
            return type(self)(result_x, result_y)
        else:
            # Raise an exception if the other object is not a XY
            raise ValueError("Addition is only supported between two XY instances")

    def __sub__(self, other):
        # Check if the other object is also a XY
        if isinstance(other, XY):
            # Perform element-wise addition
            result_x = self.x - other.x
            result_y = self.y - other.y
            return type(self)(result_x, result_y)
        elif isinstance(other, int | float):
            result_x = self.x - other
            result_y = self.y - other
            return type(self)(result_x, result_y)
        else:
            # Raise an exception if the other object is not a XY
            raise ValueError("Addition is only supported between two XY instances")

    def rotate(self, center_point: "XY", rotation_degree: float) -> "XY":
        if rotation_degree == 0:
            "easy case"
            return self
        angle = np.deg2rad(rotation_degree)
        R = np.array([[np.cos(angle), -np.sin(angle)], [np.sin(angle), np.cos(angle)]])
        np_center = np.atleast_2d((center_point.x, center_point.y))
        np_point = np.atleast_2d((self.x, self.y))
        np_point = np.squeeze((R @ (np_point.T - np_center.T) + np_center.T).T)
        return self.from_np(np_point)


class Corners:
    top_left: XY
    top_right: XY
    bottom_left: XY
    bottom_right: XY

    def __init__(
        self,
        top_left: XY,
        size: XY,
    ) -> None:
        self.top_left = top_left + size * XY(0, 1)
        self.top_right = top_left + size * XY(1, 1)
        self.bottom_left = top_left + size * XY(0, 0)
        self.bottom_right = top_left + size * XY(1, 0)

    def rotate(self, center_rotation_point: XY, angle_rotate: float) -> "Corners":
        if angle_rotate != 0:
            self.top_left = self.top_left.rotate(center_rotation_point, angle_rotate)
            self.top_right = self.top_right.rotate(center_rotation_point, angle_rotate)
            self.bottom_left = self.bottom_left.rotate(
                center_rotation_point, angle_rotate
            )
            self.bottom_right = self.bottom_right.rotate(
                center_rotation_point, angle_rotate
            )
        return self

    def __add__(self, other: int) -> "Corners":
        self.top_left += XY(-other, other)
        self.top_right += XY(other, other)
        self.bottom_left += XY(-other, -other)
        self.bottom_right += XY(other, -other)
        return self

    def __str__(self) -> str:
        # return f"top_left: {self.top_left}, top_right: {self.top_right}, bottom_left: {self.bottom_left}, bottom_right: {self.bottom_right}"
        return f"{self.top_left}, {self.top_right}, {self.bottom_left}, {self.bottom_right}"

    def get_coruners(self) -> tuple[XY, XY, XY, XY]:
        return (self.top_left, self.top_right, self.bottom_left, self.bottom_right)


# General Keyboard part, can be a key, mcu, etc.
class Part:
    # Calculate in the init function
    corners: Corners
    center_point: XY  # Center XY of the part in mm NOT u.
    center_rotation: XY
    angle_rotation: float
    text: str

    # Provide by the component class
    size: XY
    footprint_pcb: XY
    footprint_plate: XY

    # border_pcb: XY  # Add additional border to the part
    def __init__(
        self,
        upper_left_corner: XY,
        angle_rotation: float,
        center_rotation: XY,
        size: XY | None,
        text: str,
    ):
        self.text = text
        if size is not None:
            self.size = size
        # print("upper_left_corner", upper_left_corner, text)
        self.center_point = (upper_left_corner + self.size / 2).rotate(
            center_rotation, angle_rotation
        )
        # print("after upper_left_corner", self.center_point, text)
        self.center_rotation = center_rotation
        self.angle_rotation = angle_rotation
        self.corners = Corners(upper_left_corner, self.size).rotate(
            center_rotation, angle_rotation
        )

    def get_openscad_obj(self) -> OpenSCADObject:
        raise NotImplementedError(
            "This function must be implemented, for the part ", type(self)
        )

    # Add border add constant length to every size of the part and rotate it if needed
    # The center of rotation is the center of the part, not the original rotation point
    def add_border(self, border: int) -> "Part":
        if self.angle_rotation != 0:
            self.corners.rotate(self.center_point, -self.angle_rotation)
        self.corners += border
        if self.angle_rotation != 0:
            self.corners.rotate(self.center_point, self.angle_rotation)
        return self

    def draw_pcb_footprint(self) -> OpenSCADObject:
        if self.footprint_pcb == XY(0, 0):
            # No footprint
            return union()

        return (
            cube([self.footprint_pcb.x, self.footprint_pcb.y, 5], center=True)
            .rotate(self.angle_rotation)
            .translate(self.center_point.x, self.center_point.y, 0)
        )

    # # Return the part on the PCB layer as a openscad object
    def draw_pcb_part(self) -> OpenSCADObject:
        return (
            self.get_openscad_obj()
            .rotate(self.angle_rotation)
            .translate(self.center_point.x, self.center_point.y, 0)
        )

    def draw_pcb_part_addition_sub(self) -> OpenSCADObject:
        return union()

    def draw_pcb_part_addition_add(self) -> OpenSCADObject:
        return union()

    def draw_bottom_part_addition_sub(self) -> OpenSCADObject:
        return union()

    def draw_bottom_part_addition_add(self) -> OpenSCADObject:
        return union()

    def draw_plate_footprint(self) -> OpenSCADObject:
        if self.footprint_plate == XY(0, 0):
            return union()
        return (
            cube([self.footprint_plate.x, self.footprint_plate.y, 5], center=True)
            .rotate(self.angle_rotation)
            .translate(self.center_point.x, self.center_point.y, 0)
        )

    def draw_plate_part(self) -> OpenSCADObject:
        return union()

    def draw_plate_part_addition_sub(self) -> OpenSCADObject:
        return union()

    def draw_plate_part_addition_add(self) -> OpenSCADObject:
        return union()
