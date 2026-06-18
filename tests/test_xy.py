import pytest
import numpy as np
from keyboardgenerator.base import XY


class TestXYArithmetic:
    def test_mul_xy_by_xy(self):
        a = XY(2.0, 3.0)
        b = XY(4.0, 5.0)
        result = a * b
        assert result.x == 8.0
        assert result.y == 15.0

    def test_mul_xy_by_scalar(self):
        a = XY(2.0, 3.0)
        result = a * 2
        assert result.x == 4.0
        assert result.y == 6.0

    def test_mul_xy_by_float(self):
        a = XY(1.0, 2.0)
        result = a * 0.5
        assert result.x == 0.5
        assert result.y == 1.0

    def test_mul_unsupported_type_raises(self):
        with pytest.raises(ValueError):
            XY(1, 2) * "bad"

    def test_add_xy_by_xy(self):
        result = XY(1.0, 2.0) + XY(3.0, 4.0)
        assert result.x == 4.0
        assert result.y == 6.0

    def test_add_xy_by_scalar(self):
        result = XY(1.0, 2.0) + 5
        assert result.x == 6.0
        assert result.y == 7.0

    def test_sub_xy_by_xy(self):
        result = XY(5.0, 7.0) - XY(2.0, 3.0)
        assert result.x == 3.0
        assert result.y == 4.0

    def test_sub_xy_by_scalar(self):
        result = XY(5.0, 7.0) - 2
        assert result.x == 3.0
        assert result.y == 5.0

    def test_sub_unsupported_type_raises(self):
        with pytest.raises(ValueError):
            XY(1, 2) - "bad"

    def test_div_xy_by_xy(self):
        result = XY(6.0, 8.0) / XY(2.0, 4.0)
        assert result.x == 3.0
        assert result.y == 2.0

    def test_div_xy_by_scalar(self):
        result = XY(6.0, 8.0) / 2
        assert result.x == 3.0
        assert result.y == 4.0

    def test_div_unsupported_type_raises(self):
        with pytest.raises(ValueError):
            XY(1, 2) / "bad"

    def test_get_tuple(self):
        assert XY(3.0, 4.0).get_tuple() == (3.0, 4.0)

    def test_str(self):
        assert str(XY(1.0, 2.0)) == "1.0, 2.0"

    def test_from_np(self):
        arr = np.array([1.5, 2.5])
        xy = XY.from_np(arr)
        assert xy.x == 1.5
        assert xy.y == 2.5

    def test_mul_preserves_subclass(self):
        """Ensure type(self) is used so subclasses work correctly."""
        result = XY(2.0, 3.0) * XY(1.0, 1.0)
        assert type(result) is XY


class TestXYRotate:
    def test_rotate_zero_degrees_returns_same_point(self):
        p = XY(5.0, 0.0)
        result = p.rotate(XY(0, 0), 0)
        assert result.x == pytest.approx(5.0)
        assert result.y == pytest.approx(0.0)

    def test_rotate_90_degrees_around_origin(self):
        p = XY(1.0, 0.0)
        result = p.rotate(XY(0, 0), 90)
        assert result.x == pytest.approx(0.0, abs=1e-9)
        assert result.y == pytest.approx(1.0)

    def test_rotate_180_degrees_around_origin(self):
        p = XY(1.0, 0.0)
        result = p.rotate(XY(0, 0), 180)
        assert result.x == pytest.approx(-1.0)
        assert result.y == pytest.approx(0.0, abs=1e-9)

    def test_rotate_around_non_origin_center(self):
        # Point (2,1) rotated 90° around (1,1) → (1,2)
        p = XY(2.0, 1.0)
        result = p.rotate(XY(1.0, 1.0), 90)
        assert result.x == pytest.approx(1.0)
        assert result.y == pytest.approx(2.0)

    def test_rotate_360_returns_original(self):
        p = XY(3.0, 4.0)
        result = p.rotate(XY(0, 0), 360)
        assert result.x == pytest.approx(3.0)
        assert result.y == pytest.approx(4.0)
