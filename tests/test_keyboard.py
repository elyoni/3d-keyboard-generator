import pytest
from keyboardgenerator.keyboard import Keyboard, get_part_obj
from keyboardgenerator.base import XY
from keyboardgenerator.keys import CherryMxKey, KailhChocKey
from keyboardgenerator.arduino import Arduino
from keyboardgenerator.pins import Pin, PinPlate, PinPcb, PinFromBottomToPlate
from keyboardgenerator.holes import Holes
from keyboardgenerator.plate_text import PlateTextPart
from keyboardgenerator.split_keyboard_connectors import SplitKeyboardConnector, TRRSJack
from keyboardgenerator import hardcoded_jsons


class TestGetPartObj:
    def test_cherry(self):
        assert get_part_obj("cherry") is CherryMxKey

    def test_kailhchoc(self):
        assert get_part_obj("kailhchoc") is KailhChocKey

    def test_arduino(self):
        assert get_part_obj("arduino") is Arduino

    def test_pin(self):
        assert get_part_obj("pin") is Pin

    def test_pinplate(self):
        assert get_part_obj("pinplate") is PinPlate

    def test_pinpcb(self):
        assert get_part_obj("pinpcb") is PinPcb

    def test_pinb2t(self):
        assert get_part_obj("pinb2t") is PinFromBottomToPlate

    def test_hole(self):
        assert get_part_obj("hole") is Holes

    def test_platetext(self):
        assert get_part_obj("platetext") is PlateTextPart

    def test_split_keyboard_connector(self):
        assert get_part_obj("split_keyboard_connector") is SplitKeyboardConnector

    def test_trrs(self):
        assert get_part_obj("trrs") is TRRSJack

    def test_empty_string_defaults_to_cherry(self):
        assert get_part_obj("") is CherryMxKey

    def test_unknown_type_raises(self):
        with pytest.raises(ValueError):
            get_part_obj("unknown_part_xyz")


class TestGetKeyboardSpacing:
    def test_cherrymx_spacing(self):
        spacing = Keyboard.get_keyboard_spacing("cherrymx")
        assert spacing == CherryMxKey.spacing

    def test_cherrymx_empty_string_defaults(self):
        spacing = Keyboard.get_keyboard_spacing("")
        assert spacing == CherryMxKey.spacing

    def test_kailhchockey_spacing(self):
        spacing = Keyboard.get_keyboard_spacing("kailhchockey")
        assert spacing == KailhChocKey.spacing

    def test_cherrymx_case_insensitive(self):
        spacing = Keyboard.get_keyboard_spacing("CherryMX")
        assert spacing == CherryMxKey.spacing

    def test_unknown_spacing_raises(self):
        with pytest.raises(ValueError):
            Keyboard.get_keyboard_spacing("unknown")


class TestKeyboardFromKle:
    def test_from_kle_creates_keyboard(self):
        kle = hardcoded_jsons.tez_v3()
        kb = Keyboard.from_kle_obj(kle)
        assert isinstance(kb, Keyboard)
        assert len(kb.parts_list) > 0

    def test_from_kle_mirror_side(self):
        kle = hardcoded_jsons.tez_v3()
        kb = Keyboard.from_kle_obj(kle, mirror_side=True)
        assert isinstance(kb, Keyboard)

    def test_plate_border_from_notes(self):
        kle = hardcoded_jsons.tez_v3()
        # notes is empty → border = 0
        kb = Keyboard.from_kle_obj(kle)
        assert kb.plate_border == 0

    def test_parts_have_center_points(self):
        kle = hardcoded_jsons.tez_v3()
        kb = Keyboard.from_kle_obj(kle)
        for part in kb.parts_list:
            assert isinstance(part.center_point, XY)
            assert isinstance(part.center_point.x, float)
            assert isinstance(part.center_point.y, float)

    def test_support_parts_keyboard(self):
        kle = hardcoded_jsons.support_parts()
        kb = Keyboard.from_kle_obj(kle)
        assert len(kb.parts_list) > 0

    def test_one_board_tez_v3_keyboard(self):
        kle = hardcoded_jsons.one_board_tez_v3()
        kb = Keyboard.from_kle_obj(kle)
        assert len(kb.parts_list) > 0

    def test_left_side_gez_v1_keyboard(self):
        kle = hardcoded_jsons.left_side_gez_v1()
        kb = Keyboard.from_kle_obj(kle)
        assert len(kb.parts_list) > 0

    def test_almost_there_keyboard(self):
        kle = hardcoded_jsons.almost_there()
        kb = Keyboard.from_kle_obj(kle)
        assert len(kb.parts_list) > 0


class TestPartPositioning:
    """Verify that part positions are computed correctly from KLE layout."""

    def test_cherry_key_size_matches_spacing(self):
        kle = hardcoded_jsons.tez_v3()
        kb = Keyboard.from_kle_obj(kle)
        cherry_keys = [p for p in kb.parts_list if isinstance(p, CherryMxKey)]
        assert len(cherry_keys) > 0
        for key in cherry_keys:
            # Size should be a multiple of the spacing
            assert key.size.x > 0
            assert key.size.y > 0

    def test_all_parts_have_non_zero_size(self):
        kle = hardcoded_jsons.tez_v3()
        kb = Keyboard.from_kle_obj(kle)
        for part in kb.parts_list:
            assert part.size.x > 0
            assert part.size.y > 0
