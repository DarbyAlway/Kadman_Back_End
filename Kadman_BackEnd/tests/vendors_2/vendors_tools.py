# test_attendance.py
import pytest
from vendor_tools import calculate_attendance

@pytest.mark.parametrize("current_attendance, days_count, expected", [
    # days_count = 3 → unchanged
    (0, 3, 0),
    (1, 3, 1),
    (2, 3, 2),
    (3, 3, 3),

    # days_count = 2 → decrease by 1, min 0
    (0, 2, 0),
    (1, 2, 0),
    (2, 2, 1),
    (3, 2, 2),

    # days_count = 1 → decrease by 2, min 0
    (0, 1, 0),
    (1, 1, 0),
    (2, 1, 0),
    (3, 1, 1),

    # days_count = 0 → always 0
    (0, 0, 0),
    (1, 0, 0),
    (2, 0, 0),
    (3, 0, 0),
])

def test_calculate_attendance(current_attendance, days_count, expected):
    assert calculate_attendance(current_attendance, days_count) == expected
