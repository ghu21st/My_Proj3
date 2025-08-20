# ---------------------------------------
# QA tech assignement for BrainBox AI - Aug 2025
# Python Unit Test - upload 
# Gang Hu 
# --------------------------------
# modules
import pytest 
import tempfile
import re
import logging
import os

from main_brainbox_api import post_upload_csv

LOGGER = logging.getLogger(__name__) # use config in pytest.ini

# ----------------------------
def test_post_upload_csv_ok_one_datarow(mocker):
    LOGGER.info("test_post_upload_csv() under test_unit_upload.py")

    # create temp csv file by tempfile module for testing
    csv_content = "bill_id,meter_id,usage_type,building_id,start_date,end_date\
                    b0001,15,water,101,2025-02-01,2024-03-01"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name
    
    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set return values
    mock_post.return_value.ok = True
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "status":"ok",
        "stored":"local_state/uploads/valid_1.csv",
        "crawler_marker":"local_state/glue/bills_crawler__1755660638__9420aab4a5c44b82974c9a502e44a8d7.marker",
        "rows_inserted":2}
    mock_post.return_value.text = 'File upload successful'

    # call function
    result = post_upload_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+status.+ok+"
    expected_pattern2 = ".+stored.+local_state/uploads.+crawler_marker.+local_state/glue/bills_crawler_.*"
    actual_result = str(result)   #actual_result = json.dumps(response.text)
    #
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"
    mock_post.assert_called_once_with(
        "http://localhost:8000/upload/",
        files={'file': mocker.ANY},
        data={}
    )

# ------------------------------------------

