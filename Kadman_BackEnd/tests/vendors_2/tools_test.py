import pytest
import json
from unittest.mock import MagicMock, patch
from vendor_tools import (
    calculate_attendance,
    update_layout,
    update_vendor_attendance_days,
    notify_vendor,
    calculate_promptpay_amount,
    generate_promptpay_link
)


def test_calculate_promptpay_amount():
    assert calculate_promptpay_amount(["Mon"]) == 100
    assert calculate_promptpay_amount(["Mon", "Tue"]) == 200
    assert calculate_promptpay_amount([]) == 0


def test_generate_promptpay_link():
    link = generate_promptpay_link("0812345678", 500)
    assert link == "https://promptpay.io/0812345678/500"


@pytest.mark.parametrize("days_count,current,expected", [
    (3, 5, 5),   # unchanged
    (2, 5, 4),   # minus 1
    (2, 0, 0),   # not below 0
    (1, 5, 3),   # minus 2
    (1, 1, 0),   # min 0
    (0, 10, 0),  # reset
])
def test_calculate_attendance(days_count, current, expected):
    assert calculate_attendance(current, days_count) == expected


def test_update_layout_success():
    mock_cursor = MagicMock()
    layout_data = {"A1": {"vendorID": 1, "status": "old"}}
    mock_cursor.fetchone.return_value = (json.dumps(layout_data),)

    updated_layout, updated = update_layout(mock_cursor, 10, 1)

    assert updated is True
    assert updated_layout["A1"]["status"] == "pending payment"

    mock_cursor.execute.assert_any_call(
        "UPDATE layouts SET data = %s WHERE id = %s",
        (json.dumps(updated_layout), 10)
    )


def test_update_layout_not_found():
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None

    layout_data, updated = update_layout(mock_cursor, 99, 1)
    assert layout_data is None
    assert updated is False


def test_update_layout_vendor_not_in_layout():
    mock_cursor = MagicMock()
    layout_data = {"A1": {"vendorID": 2, "status": "ok"}}
    mock_cursor.fetchone.return_value = (json.dumps(layout_data),)

    updated_layout, updated = update_layout(mock_cursor, 10, 1)

    assert updated is False
    assert updated_layout == layout_data


def test_notify_vendor():
    with patch("vendor_tools.send_line_multicast", return_value=(200, "OK")) as mock_send:
        result = notify_vendor("line123", "http://pay.me")
        assert result == (200, "OK")
        mock_send.assert_called_once_with(
            ["line123"], "For payment confirmation use this link http://pay.me"
        )


def test_update_vendor_attendance_days():
    mock_cursor = MagicMock()
    days = ["Mon", "Tue"]

    result = update_vendor_attendance_days(mock_cursor, 1, days)

    assert json.loads(result) == days
    mock_cursor.execute.assert_called_once_with(
        "UPDATE vendors SET attendance_days = %s WHERE vendorID = %s",
        (json.dumps(days), 1)
    )
