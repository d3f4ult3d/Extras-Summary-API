"""
extras_tests.py — Unit tests for ExtrasService._calc_extras.

All tests run without a database — _calc_extras is a pure function.

Run:
    pytest extras_tests.py -v
"""
import pytest
from Eservices import ExtrasService


def make_ball(extra_type=None, extras=0):
    return {"extra_type": extra_type, "extras": extras}


# ------------------------------------------------------------------
# Individual extra types
# ------------------------------------------------------------------
class TestEachExtraType:
    def test_wide(self):
        result = ExtrasService._calc_extras([make_ball("wide", 1)])
        assert result["wides"] == 1

    def test_no_ball(self):
        result = ExtrasService._calc_extras([make_ball("no_ball", 1)])
        assert result["no_balls"] == 1

    def test_bye(self):
        result = ExtrasService._calc_extras([make_ball("bye", 2)])
        assert result["byes"] == 2

    def test_leg_bye(self):
        result = ExtrasService._calc_extras([make_ball("leg_bye", 3)])
        assert result["leg_byes"] == 3

    def test_penalty(self):
        result = ExtrasService._calc_extras([make_ball("penalty", 5)])
        assert result["penalties"] == 5


# ------------------------------------------------------------------
# Total extras
# ------------------------------------------------------------------
class TestTotalExtras:
    def test_total_is_sum_of_all_types(self):
        balls = [
            make_ball("wide",    1),
            make_ball("no_ball", 1),
            make_ball("bye",     2),
            make_ball("leg_bye", 3),
            make_ball("penalty", 5),
        ]
        result = ExtrasService._calc_extras(balls)
        assert result["total_extras"] == 12

    def test_total_excludes_non_extras(self):
        balls = [
            make_ball(None, 0),   # clean delivery
            make_ball("wide", 1),
        ]
        result = ExtrasService._calc_extras(balls)
        assert result["total_extras"] == 1


# ------------------------------------------------------------------
# Edge cases
# ------------------------------------------------------------------
class TestEdgeCases:
    def test_empty_innings(self):
        result = ExtrasService._calc_extras([])
        assert result == {
            "wides": 0, "no_balls": 0, "byes": 0,
            "leg_byes": 0, "penalties": 0, "total_extras": 0,
        }

    def test_no_extras_in_innings(self):
        balls = [make_ball(None, 0)] * 6
        result = ExtrasService._calc_extras(balls)
        assert result["total_extras"] == 0

    def test_boundary_wide_adds_five(self):
        # A wide that reaches the boundary = 5 extra runs, not 1
        result = ExtrasService._calc_extras([make_ball("wide", 5)])
        assert result["wides"] == 5
        assert result["total_extras"] == 5

    def test_multiple_balls_same_type_accumulate(self):
        balls = [
            make_ball("wide", 1),
            make_ball("wide", 1),
            make_ball("wide", 5),  # boundary wide
        ]
        result = ExtrasService._calc_extras(balls)
        assert result["wides"] == 7

    def test_unknown_extra_type_ignored(self):
        # Unrecognised types should not corrupt totals
        balls = [make_ball("unknown_type", 3)]
        result = ExtrasService._calc_extras(balls)
        assert result["total_extras"] == 0

    def test_all_fields_present_in_result(self):
        result = ExtrasService._calc_extras([])
        assert set(result.keys()) == {
            "wides", "no_balls", "byes", "leg_byes", "penalties", "total_extras"
        }

    def test_categories_are_independent(self):
        balls = [
            make_ball("wide",    2),
            make_ball("bye",     1),
            make_ball("leg_bye", 2),
        ]
        result = ExtrasService._calc_extras(balls)
        assert result["wides"]    == 2
        assert result["byes"]     == 1
        assert result["leg_byes"] == 2
        assert result["no_balls"] == 0
        assert result["penalties"]== 0