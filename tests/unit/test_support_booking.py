import json
import tempfile
from support_booking import write_json
import pytest


dt1 = {
                "id": "d3ddadf9-5ca0-411f-95b6-56e2e2662772",
                "club_id": "john@simplylift.co",
                "competition_id": "Fall Classic",
                "places": 2
            }
dt2 = {
                "id": "a1f4b2c3-7d8e-4f91-9a2b-3c5d6e7f8a90",
                "club_id": "john@simplylift.co",
                "competition_id": "Fall Classic",
                "places": 2
            }


def create_temp_file():
    """Create a temporary file and return its path."""
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        return tmp_file.name


@pytest.mark.parametrize("given_data", [(dt1), (dt2)])
def test_write_json(given_data,):
    """
    Testing the write_json support function
    """
    mock_path = create_temp_file()
    write_json(mock_path, given_data)

    with open(mock_path, "r") as f:
        data = json.load(f)

    assert "booking_places" in data
    saved_data = data["booking_places"]
    assert saved_data == given_data
