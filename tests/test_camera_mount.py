import pytest
from keyboardgenerator.base import XY
from keyboardgenerator.keyboard import Keyboard
from keyboardgenerator.keys import CherryMxKey
from keyboardgenerator.camera_mount import (
    CameraMount,
    CameraMountSelfTap,
    CameraMountHeatSet,
    TiltLeg,
    SELF_TAP_HOLE_DIAMETER,
    HEAT_SET_HOLE_DIAMETER,
    BOSS_OUTER_DIAMETER,
)


def _make_part(cls, center_x, center_y, **kwargs):
    """Create a part with a given center position."""
    upper_left = XY(center_x - cls.size.x / 2, center_y - cls.size.y / 2)
    part = cls(upper_left, 0, XY(0, 0), None, "", mirror_side=False)
    for k, v in kwargs.items():
        setattr(part, k, v)
    return part


def _make_keys(n=5, start_x=0.0):
    """Create n CherryMx keys in a row so the keyboard has a well-defined hull."""
    spacing = CherryMxKey.spacing.x
    keys = []
    for i in range(n):
        ul = XY(start_x + i * spacing, 0)
        keys.append(
            CherryMxKey(ul, 0, XY(0, 0), CherryMxKey.spacing, "", mirror_side=False)
        )
    return keys


# ── right_edge_x for 5 Cherry keys ──────────────────────────────────────────
# 5 keys × 19.05mm each = 95.25mm right edge
RIGHT_EDGE = 5 * CherryMxKey.spacing.x  # 95.25


class TestCameraMountVariants:
    def test_selftap_hole_diameter(self):
        assert CameraMountSelfTap.hole_diameter == SELF_TAP_HOLE_DIAMETER

    def test_heatset_hole_diameter(self):
        assert CameraMountHeatSet.hole_diameter == HEAT_SET_HOLE_DIAMETER

    def test_heatset_hole_larger_than_selftap(self):
        assert HEAT_SET_HOLE_DIAMETER > SELF_TAP_HOLE_DIAMETER

    def test_boss_outer_diameter_greater_than_heatset_hole(self):
        assert BOSS_OUTER_DIAMETER > HEAT_SET_HOLE_DIAMETER

    def test_names_registered(self):
        from keyboardgenerator.keyboard import get_part_obj
        assert get_part_obj("cameramount_selftap") is CameraMountSelfTap
        assert get_part_obj("cameramount_heatset") is CameraMountHeatSet
        assert get_part_obj("tiltleg") is TiltLeg

    def test_center_point_correct(self):
        mount = _make_part(CameraMountSelfTap, 60.0, 30.0)
        assert mount.center_point.x == pytest.approx(60.0)
        assert mount.center_point.y == pytest.approx(30.0)


class TestLegHeightCalculation:
    def _keyboard(self, boss_center_x, leg_center_xs, boss_height=10.0):
        keys = _make_keys(5)
        mount = _make_part(CameraMountSelfTap, boss_center_x, 10.0, boss_height=boss_height)
        legs = [_make_part(TiltLeg, lx, 10.0) for lx in leg_center_xs]
        return Keyboard(keys + [mount] + legs, plate_border=0)

    def test_leg_height_set_after_validation(self):
        kb = self._keyboard(boss_center_x=60.0, leg_center_xs=[10.0], boss_height=10.0)
        kb._validate_and_set_leg_heights()
        leg = [p for p in kb.parts_list if isinstance(p, TiltLeg)][0]
        # required = 10 * (95.25 - 10) / (95.25 - 60) = 10 * 85.25 / 35.25
        expected = 10.0 * (RIGHT_EDGE - 10.0) / (RIGHT_EDGE - 60.0)
        assert leg.height == pytest.approx(expected, rel=1e-4)

    def test_leg_at_far_inner_edge_is_taller(self):
        kb = self._keyboard(boss_center_x=60.0, leg_center_xs=[5.0, 30.0], boss_height=10.0)
        kb._validate_and_set_leg_heights()
        legs = sorted(
            [p for p in kb.parts_list if isinstance(p, TiltLeg)],
            key=lambda p: p.center_point.x,
        )
        assert legs[0].height > legs[1].height  # further left → taller

    def test_taller_boss_produces_taller_legs(self):
        kb_low = self._keyboard(boss_center_x=60.0, leg_center_xs=[10.0], boss_height=8.0)
        kb_high = self._keyboard(boss_center_x=60.0, leg_center_xs=[10.0], boss_height=15.0)
        kb_low._validate_and_set_leg_heights()
        kb_high._validate_and_set_leg_heights()
        leg_low = [p for p in kb_low.parts_list if isinstance(p, TiltLeg)][0]
        leg_high = [p for p in kb_high.parts_list if isinstance(p, TiltLeg)][0]
        assert leg_high.height > leg_low.height

    def test_leg_at_boss_position_would_have_same_height_as_boss(self):
        # At x == boss_x, required_height == boss_height (on the plane)
        boss_x = 60.0
        boss_height = 10.0
        # Put a leg just epsilon to the left to avoid the equality check failing
        kb = self._keyboard(boss_center_x=boss_x, leg_center_xs=[boss_x - 0.001], boss_height=boss_height)
        kb._validate_and_set_leg_heights()
        leg = [p for p in kb.parts_list if isinstance(p, TiltLeg)][0]
        assert leg.height == pytest.approx(boss_height, rel=1e-3)

    def test_no_legs_skips_validation(self):
        keys = _make_keys(5)
        mount = _make_part(CameraMountSelfTap, 60.0, 10.0)
        kb = Keyboard(keys + [mount], plate_border=0)
        kb._validate_and_set_leg_heights()  # should not raise

    def test_no_legs_no_mount_is_fine(self):
        keys = _make_keys(5)
        kb = Keyboard(keys, plate_border=0)
        kb._validate_and_set_leg_heights()  # should not raise


class TestLegValidationErrors:
    def test_legs_without_mount_raises(self):
        keys = _make_keys(5)
        leg = _make_part(TiltLeg, 10.0, 10.0)
        kb = Keyboard(keys + [leg], plate_border=0)
        with pytest.raises(ValueError, match="CameraMount"):
            kb._validate_and_set_leg_heights()

    def test_leg_to_right_of_boss_raises(self):
        keys = _make_keys(5)
        mount = _make_part(CameraMountSelfTap, 40.0, 10.0)
        leg = _make_part(TiltLeg, 70.0, 10.0)  # right of boss
        kb = Keyboard(keys + [mount, leg], plate_border=0)
        with pytest.raises(ValueError, match="left of"):
            kb._validate_and_set_leg_heights()

    def test_leg_at_same_x_as_boss_raises(self):
        keys = _make_keys(5)
        mount = _make_part(CameraMountSelfTap, 40.0, 10.0)
        leg = _make_part(TiltLeg, 40.0, 10.0)
        kb = Keyboard(keys + [mount, leg], plate_border=0)
        with pytest.raises(ValueError, match="left of"):
            kb._validate_and_set_leg_heights()

    def test_boss_to_right_of_keyboard_raises(self):
        keys = _make_keys(5)
        mount = _make_part(CameraMountSelfTap, RIGHT_EDGE + 10.0, 10.0)
        leg = _make_part(TiltLeg, 10.0, 10.0)
        kb = Keyboard(keys + [mount, leg], plate_border=0)
        with pytest.raises(ValueError, match="right edge"):
            kb._validate_and_set_leg_heights()

    def test_multiple_mounts_raises(self):
        keys = _make_keys(5)
        mount1 = _make_part(CameraMountSelfTap, 40.0, 10.0)
        mount2 = _make_part(CameraMountSelfTap, 60.0, 10.0)
        leg = _make_part(TiltLeg, 10.0, 10.0)
        kb = Keyboard(keys + [mount1, mount2, leg], plate_border=0)
        with pytest.raises(ValueError, match="Only one"):
            kb._validate_and_set_leg_heights()
