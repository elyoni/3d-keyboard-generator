import pytest
from keyboardgenerator.base import XY, Corners


class TestCornersConstruction:
    def test_corners_no_rotation(self):
        top_left = XY(0.0, 0.0)
        size = XY(10.0, 20.0)
        c = Corners(top_left, size)
        assert c.bottom_left.x == pytest.approx(0.0)
        assert c.bottom_left.y == pytest.approx(0.0)
        assert c.bottom_right.x == pytest.approx(10.0)
        assert c.bottom_right.y == pytest.approx(0.0)
        assert c.top_left.x == pytest.approx(0.0)
        assert c.top_left.y == pytest.approx(20.0)
        assert c.top_right.x == pytest.approx(10.0)
        assert c.top_right.y == pytest.approx(20.0)

    def test_get_corners_returns_four_points(self):
        c = Corners(XY(0, 0), XY(5, 5))
        corners = c.get_coruners()
        assert len(corners) == 4

    def test_str_returns_string(self):
        c = Corners(XY(0, 0), XY(5, 5))
        assert isinstance(str(c), str)


class TestCornersRotation:
    def test_rotate_zero_angle_no_change(self):
        c = Corners(XY(0, 0), XY(10, 10))
        before_tl = (c.top_left.x, c.top_left.y)
        c.rotate(XY(5, 5), 0)
        assert (c.top_left.x, c.top_left.y) == before_tl

    def test_rotate_90_around_center(self):
        # A 10x10 square at origin, rotated 90° around its center (5,5)
        # top_left (0,10) → rotated 90° around (5,5) → (0,0)? Let's check:
        # (x',y') = R*(p - c) + c  for 90° CCW
        # (0-5, 10-5) = (-5, 5) → rotated 90° → (-5, -5) → + center → (0,0)
        c = Corners(XY(0, 0), XY(10, 10))
        c.rotate(XY(5, 5), 90)
        all_corners = c.get_coruners()
        xs = [p.x for p in all_corners]
        ys = [p.y for p in all_corners]
        # After rotating a square 90° around its center, corners map to corners
        assert min(xs) == pytest.approx(0.0, abs=1e-9)
        assert max(xs) == pytest.approx(10.0, abs=1e-9)


class TestCornersAddBorder:
    def test_add_border_expands_box(self):
        c = Corners(XY(0, 0), XY(10, 10))
        c += 2
        assert c.top_left.x == pytest.approx(-2.0)
        assert c.top_left.y == pytest.approx(12.0)
        assert c.bottom_right.x == pytest.approx(12.0)
        assert c.bottom_right.y == pytest.approx(-2.0)
