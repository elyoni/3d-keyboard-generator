from solid2.extensions.bosl2 import cylinder, sphere, TOP, BOTTOM
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
# Width of the conical chamfer at the base of boss and legs.
# Adds a flare where the feature meets the plate for better adhesion and strength.
CHAMFER_SIZE = 2.0


class CameraMount(Part):
    """
    Cylindrical boss on the outer (desk-facing) side of the bottom layer for
    a 1/4"-20 camera arm screw.  The boss protrudes upward from the plate's
    top face (z = BASIC_LAYER_THICKNESS) so it prints without supports and
    points toward the desk when the keyboard is assembled.

    Print orientation: lay the flat PCB-facing face (z = 0) on the print bed;
    the boss will stick upward during printing.  After printing, assemble the
    keyboard with the boss/legs facing down.

    The screw hole is a blind hole: it starts at the boss tip and ends at the
    plate surface — it does NOT pass through the plate.
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
        chamfer = min(CHAMFER_SIZE, self.boss_height * 0.4)

        # Conical chamfer flare at the plate surface for structural support.
        base_cone = (
            cylinder(
                h=chamfer,
                d1=self.boss_outer_diameter + 2 * chamfer,
                d2=self.boss_outer_diameter,
                anchor=BOTTOM,
                _fn=50,
            )
            .up(BASIC_LAYER_THICKNESS)
        )
        # Main boss cylinder above the chamfer.
        main_boss = (
            cylinder(
                d=self.boss_outer_diameter,
                h=self.boss_height - chamfer,
                anchor=BOTTOM,
                _fn=50,
            )
            .up(BASIC_LAYER_THICKNESS + chamfer)
        )
        # Blind screw hole: opens at the boss tip, stops at the plate surface.
        # Extra 0.5 mm above the tip prevents z-fighting at the open end.
        hole = (
            cylinder(d=self.hole_diameter, h=self.boss_height + 0.5, anchor=TOP, _fn=50)
            .up(BASIC_LAYER_THICKNESS + self.boss_height + 0.5)
        )
        return (base_cone + main_boss) - hole

    def _draw_bottom_part_addition_sub(self) -> OpenSCADObject | None:
        # No through-hole in the plate — the screw stops inside the boss.
        return None


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
    Cylindrical leg with a hemispherical tip and a conical chamfer base.
    Protrudes upward from the plate's outer face (z = BASIC_LAYER_THICKNESS)
    so it prints without supports and points toward the desk when assembled.
    Height is auto-calculated by Keyboard.draw_bottom() so the leg tip lies
    on the tilt plane defined by the CameraMount boss and the outer edge.
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
        r = self.diameter / 2
        chamfer = min(CHAMFER_SIZE, (self.height - r) * 0.4)

        # Conical chamfer flare at the plate surface for structural support.
        base_cone = (
            cylinder(
                h=chamfer,
                d1=self.diameter + 2 * chamfer,
                d2=self.diameter,
                anchor=BOTTOM,
                _fn=50,
            )
            .up(BASIC_LAYER_THICKNESS)
        )
        # Straight shaft from the top of the chamfer to the start of the hemisphere.
        shaft = (
            cylinder(d=self.diameter, h=self.height - r - chamfer, anchor=BOTTOM, _fn=50)
            .up(BASIC_LAYER_THICKNESS + chamfer)
        )
        # Hemispherical tip — its lowest point is the desk contact point.
        rounded_tip = sphere(d=self.diameter, _fn=50).up(BASIC_LAYER_THICKNESS + self.height - r)
        return base_cone + shaft + rounded_tip
