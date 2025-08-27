import json
from layouts import send_line_multicast

def calculate_promptpay_amount(days_checked):
    # Assume each day is worth 100 units
    return len(days_checked) * 100

def generate_promptpay_link(base_number, amount):
    # base_number: the phone number associated with PromptPay (string)
    return f"https://promptpay.io/{base_number}/{amount}"


def get_vendor_by_lineid(cursor, user_id):
    cursor.execute("SELECT vendorID, attendance FROM vendors WHERE lineID = %s", (user_id,))
    return cursor.fetchone()

def update_vendor_attendance(cursor, vendor_id, new_attendance):
    cursor.execute(
        "UPDATE vendors SET attendance = %s WHERE vendorID = %s",
        (new_attendance, vendor_id)
    )

def calculate_attendance(current_attendance, days_count):
    if days_count == 3:
        return current_attendance
    elif days_count == 2:
        return max(0, current_attendance - 1)
    elif days_count == 1:
        return max(0, current_attendance - 2)
    else:
        return 0

def update_layout(cursor, layout_id, vendor_id): # update vendors status in layout for waiting for payment
    cursor.execute("SELECT data FROM layouts WHERE id = %s", (layout_id,))
    layout_row = cursor.fetchone()
    if not layout_row:
        return None, False

    layout_data = json.loads(layout_row[0])
    updated = False
    for slot, value in layout_data.items():
        if isinstance(value, dict) and value.get("vendorID") == vendor_id:
            value["status"] = "pending payment"
            updated = True
            break
    if updated:
        cursor.execute("UPDATE layouts SET data = %s WHERE id = %s",
                       (json.dumps(layout_data), layout_id))
    return layout_data, updated

def notify_vendor(user_id, payment_url):
    message_text = f"For payment confirmation use this link {payment_url}"
    return send_line_multicast([user_id], message_text)

def update_vendor_attendance_days(cursor, vendor_id, days):
    """
    Store the list of days into attendance_days column.
    Expects `days` as a Python list, stores as JSON string.
    """
    import json
    days_json = json.dumps(days) if isinstance(days, list) else "[]"
    cursor.execute(
        "UPDATE vendors SET attendance_days = %s WHERE vendorID = %s",
        (days_json, vendor_id)
    )
    return days_json
