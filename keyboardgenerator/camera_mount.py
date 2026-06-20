from solid2.extensions.bosl2 import cylinder, TOP
from solid2.core.object_base import OpenSCADObject

from keyboardgenerator.base import Part, XY
from keyboardgenerator.constants import BASIC_LAYER_THICKNESS

# 1/4"-20 UNC: self-tap pilot hole into PLA/ABS
SELF_TAP_HOLE_DIAMETER = 5.5
# 1/4"-20 UNC: hole for a heat-set brass insert (verify with your insert brand)
HEAT_SET_HOLE_DIAMETER = 7.0

BOSS_OUTER_DIAMETER = 14.0
BOSS_DEFAULT_HEIGHT = 10.0
LEG_DIAMETER = 10.0


class CameraMount(Part):
    """
    Cylindrical boss on the bottom layer for a 1/4"-20 camera arm screw.
    Protrudes downward; hole_diameter is set by subclasses.
    """

    boss_outer_diameter: float = BOSS_OUTER_DIAMETER
    boss_height: float = BOSS_DEFAULT_HEIGHT
    hole_diameter: float = SELF_TAP_HOLE_DIAMETER  # overridden in subclasses

    size = XY(BOSS_OUTER_DIAMETER, BOSS_OUTER_DIAMETER)
    footprint_plate: XY | None = None
    footprint_pcb: XY = XY(0, 0)

    def _draw_pcb_part(self) -> OpenSCADObject | None:
        return None

    def _draw_bottom_part_addition_add(self) -> OpenSCADObject | None:
        # Boss protrudes downward from z=0 (the bottom face of the keyboard)
        return cylinder(
            d=self.boss_outer_diameter,
            h=self.boss_height,
            anchor=TOP,
            _fn=50,
        )

    def _draw_bottom_part_addition_sub(self) -> OpenSCADObject | None:
        # Hole runs from above the bottom layer down through the full boss
        total_height = self.boss_height + BASIC_LAYER_THICKNESS + 1.0
        return (
            cylinder(d=self.hole_diameter, h=total_height, anchor=TOP, _fn=50)
            .up(BASIC_LAYER_THICKNESS + 0.5)
        )


class CameraMountSelfTap(CameraMount):
    """Boss with a 5.5 mm pilot hole — the arm screw taps directly into plastic."""

    name: str = "cameramount_selftap"
    hole_diameter: float = SELF_TAP_HOLE_DIAMETER


class CameraMountHeatSet(CameraMount):
    """Boss with a 7.0 mm hole sized for a 1/4\"-20 heat-set brass insert."""

    name: str = "cameramount_heatset"
    hole_diameter: float = HEAT_SET_HOLE_DIAMETER


class TiltLeg(Part):
    """
    Cylindrical leg on the bottom layer that tilts the keyboard.
    Height is auto-calculated by Keyboard.draw_bottom() so the leg tip
    lies exactly on the tilt plane defined by the CameraMount boss and
    the keyboard's right (outer) edge.
    """

    name: str = "tiltleg"
    diameter: float = LEG_DIAMETER
    height: float = 0.0  # set by Keyboard._validate_and_set_leg_heights()

    size = XY(LEG_DIAMETER, LEG_DIAMETER)
    footprint_plate: XY | None = None
    footprint_pcb: XY = XY(0, 0)

    def _draw_pcb_part(self) -> OpenSCADObject | None:
        return None

    def _draw_bottom_part_addition_add(self) -> OpenSCADObject | None:
        if self.height <= 0:
            return None
        return cylinder(d=self.diameter, h=self.height, anchor=TOP, _fn=50)
