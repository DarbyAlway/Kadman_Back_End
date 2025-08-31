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

@patch("vendor_tools.send_line_multicast")
def test_full_vendor_workflow(mock_send):
    """
    Simulate full workflow:
    1. Read vendor attendance and days
    2. Calculate new attendance
    3. Update layout status
    4. Update attendance_days in vendor
    5. Send payment notification
    """
    # ----------------------------
    # Setup mock cursor and vendor data
    # ----------------------------
    mock_cursor = MagicMock()
    
    vendor_id = 123
    user_id = "U12345"
    current_attendance = 5
    days_checked = ["Mon", "Tue"]  # 2 days attended
    layout_data = {
        "A1": {"vendorID": vendor_id, "status": "waiting"},
        "A2": {"vendorID": 456, "status": "waiting"}
    }
    
    # Mock fetchone for layout
    mock_cursor.fetchone.return_value = (json.dumps(layout_data),)
    
    # ----------------------------
    # Step 1: Calculate new attendance
    # ----------------------------
    new_attendance = calculate_attendance(current_attendance, len(days_checked))
    assert new_attendance == 4  # current 5 - 1 (2 days checked)
    
    # ----------------------------
    # Step 2: Update layout
    # ----------------------------
    updated_layout, updated_flag = update_layout(mock_cursor, layout_id=1, vendor_id=vendor_id)
    assert updated_flag is True
    assert updated_layout["A1"]["status"] == "pending payment"
    
    # ----------------------------
    # Step 3: Update attendance_days in vendor
    # ----------------------------
    days_json = update_vendor_attendance_days(mock_cursor, vendor_id, days_checked)
    assert days_json == json.dumps(days_checked)
    
    # ----------------------------
    # Step 4: Generate PromptPay link and calculate amount
    # ----------------------------
    amount = calculate_promptpay_amount(days_checked)
    assert amount == 200  # 2 days * 100
    
    base_number = "0812345678"
    payment_url = generate_promptpay_link(base_number, amount)
    assert payment_url == "https://promptpay.io/0812345678/200"
    
    # ----------------------------
    # Step 5: Notify vendor
    # ----------------------------
    mock_send.return_value = "sent"
    notify_result = notify_vendor(user_id, payment_url)
    mock_send.assert_called_once_with([user_id], f"For payment confirmation use this link {payment_url}")
    assert notify_result == "sent"
    
    # ----------------------------
    # Verify cursor updates executed
    # ----------------------------
    # Layout update
    mock_cursor.execute.assert_any_call(
        "UPDATE layouts SET data = %s WHERE id = %s",
        (json.dumps(updated_layout), 1)
    )
    # Attendance_days update
    mock_cursor.execute.assert_any_call(
        "UPDATE vendors SET attendance_days = %s WHERE vendorID = %s",
        (json.dumps(days_checked), vendor_id)
    )
