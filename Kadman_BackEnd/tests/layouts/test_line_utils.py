import pytest
from unittest.mock import patch, MagicMock
from layouts import send_line_multicast  # or your actual file name

@patch("layouts.requests.post")
def test_send_line_multicast_success(mock_post):
    # 1. Prepare mock response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "OK"
    mock_post.return_value = mock_response

    # 2. Call the function with test data
    test_user_ids = ["U123456", "U789012"]
    test_message = "Hello from test!"
    status, response_text = send_line_multicast(test_user_ids, test_message)

    # 3. Assertions
    assert status == 200
    assert response_text == "OK"

    # 4. Ensure post was called with correct arguments
    expected_url = "https://api.line.me/v2/bot/message/multicast"
    mock_post.assert_called_once()
    called_url, = mock_post.call_args[0]
    called_kwargs = mock_post.call_args[1]

    assert called_url == expected_url
    assert called_kwargs["headers"]["Content-Type"] == "application/json"
    assert "Authorization" in called_kwargs["headers"]
    assert called_kwargs["json"]["to"] == test_user_ids
    assert called_kwargs["json"]["messages"][0]["text"] == test_message
