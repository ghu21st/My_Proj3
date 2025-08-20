# ---------------------------------------
# QA tech assignement for BrainBox AI - Aug 2025
# Python Unit Test - validate 
# Gang Hu 
# --------------------------------
# modules
import pytest
import tempfile
import re
import logging
import os

from main_brainbox_api import post_validate_csv

LOGGER = logging.getLogger(__name__) # use config in pytest.ini

# -----------------
def test_post_validate_csv_ok_one_datarow(mocker):
    LOGGER.info("test_post_validate_csv_ok_one_datarow() under test_unit_validate.py")

    # create temp csv file by tempfile module for testing
    csv_content = "bill_id,meter_id,usage_type,building_id,start_date,end_date\
                    b0001,15,water,101,2025-02-01,2024-03-01"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = True
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "message":"CSV file is valid.",
        "columns":["bill_id","meter_id","usage_type","building_id","start_date","end_date"],
        "rows_checked":1}
    mock_post.return_value.text = 'CSV file is valid'

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+CSV file is valid.+"
    expected_pattern2 = ".+columns.+bill_id.+meter_id.+usage_type.+building_id.+start_date.+end_date.+"
    expected_pattern3 = ".+rows_checked.+1"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"
    assert re.match(expected_pattern3, actual_result), f"Does not match the test pattern '{expected_pattern3}'"
    mock_post.assert_called_once_with(
        "http://localhost:8000/validate/",
        files={'file': mocker.ANY},
        data={}
    )

# -----------------
def test_post_validate_csv_ok_multiple_datarow(mocker):
    LOGGER.info("test_post_validate_csv_ok_multiple_datarow() under test_unit_validate.py")

    # create temp csv file by tempfile module for testing
    csv_content = "bill_id,meter_id,usage_type,building_id,start_date,end_date\
                    b0001,15,water,101,2025-02-01,2024-03-01\
                    b0002,21,electric,101,2024-02-01,2024-03-01\
                    b0003,33,water,105,2024-02-01,2024-03-01"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = True
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "message":"CSV file is valid.",
        "columns":["bill_id","meter_id","usage_type","building_id","start_date","end_date"],
        "rows_checked":3}
    mock_post.return_value.text = 'CSV file is valid'

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+message.+CSV file is valid.+"
    expected_pattern2 = ".+columns.+bill_id.+meter_id.+usage_type.+building_id.+start_date.+end_date.+"
    expected_pattern3 = ".+rows_checked.+3"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"
    assert re.match(expected_pattern3, actual_result), f"Does not match the test pattern '{expected_pattern3}'"
    mock_post.assert_called_once_with(
        "http://localhost:8000/validate/",
        files={'file': mocker.ANY},
        data={}
    )
# -----------------
def test_post_validate_csv_ok_zero_datarow(mocker):
    LOGGER.info("test_post_validate_csv_ok_zero_datarow() under test_unit_validate.py")

    # create temp csv file by tempfile module for testing
    csv_content = "bill_id,meter_id,usage_type,building_id,start_date,end_date"

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = True
    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "message":"CSV file is valid.",
        "columns":["bill_id","meter_id","usage_type","building_id","start_date","end_date"],
        "rows_checked":0}
    mock_post.return_value.text = 'CSV file is valid'

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+CSV file is valid.+"
    expected_pattern2 = ".+columns.+bill_id.+meter_id.+usage_type.+building_id.+start_date.+end_date.+"
    expected_pattern3 = ".+rows_checked.+0"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"
    assert re.match(expected_pattern3, actual_result), f"Does not match the test pattern '{expected_pattern3}'"
    mock_post.assert_called_once_with(
        "http://localhost:8000/validate/",
        files={'file': mocker.ANY},
        data={}
    )

# -----------------
def test_post_validate_csv_fail_empty_file(mocker):
    LOGGER.info("test_post_validate_csv_fail_empty_file() under test_unit_validate.py")

    # create temp csv file by tempfile module for testing
    csv_content = ""

    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 422
    mock_post.return_value.json.return_value = {
        "error":"InvalidSchema",
        "missing":["bill_id","meter_id","usage_type","building_id","start_date","end_date"],
        "extra":[]
        }
    mock_post.return_value.text = 'File validate failed'

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+error.+InvalidSchema.+"
    expected_pattern2 = ".+missing.+bill_id.+meter_id.+usage_type.+building_id.+start_date.+end_date.+"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"
    mock_post.assert_called_once_with(
        "http://localhost:8000/validate/",
        files={'file': mocker.ANY},
        data={}
    )

# -=----------------------
def test_post_validate_csv_fail_nonexist_file(mocker):
    LOGGER.info("test_post_validate_csv_fail_nonexist_file() under test_unit_validate.py")

    # create temp csv file by tempfile module for testing
    temp_file_path = 'xxxxx'

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = False
    mock_post.return_value.text = 'The CSV file does not exist'

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = "The CSV file does not exist"
    actual_result = str(result)   #actual_result = json.dumps(response.text)
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"

# -----------------
def test_post_validate_csv_fail_missing_col_bill_id(mocker):
    LOGGER.info("test_post_validate_csv_fail_missing_col_bill_id() under test_unit_validate.py")
    #  {"error":"InvalidSchema","missing":["bill_id"],"extra":[]}

    # create temp csv file by tempfile module for testing
    csv_content = "meter_id,usage_type,building_id,start_date,end_date"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 422
    mock_post.return_value.json.return_value = {    
        "error":"InvalidSchema",
        "missing":["bill_id"],
        "extra":[]
        }

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+error.+InvalidSchema.+"
    expected_pattern2 = ".+missing.+bill_id.+"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"

# -----------------
def test_post_validate_csv_fail_missing_col_meter_id(mocker):
    LOGGER.info("test_post_validate_csv_fail_missing_col_meter_id() under test_unit_validate.py")
    #  {"error":"InvalidSchema","missing":["bill_id"],"extra":[]}

    # create temp csv file by tempfile module for testing
    csv_content = "bill_id, usage_type,building_id,start_date,end_date"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 422
    mock_post.return_value.json.return_value = {    
        "error":"InvalidSchema",
        "missing":["meter_id"],
        "extra":[]
        }

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+error.+InvalidSchema.+"
    expected_pattern2 = ".+missing.+meter_id.+"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"

# -----------------
def test_post_validate_csv_fail_missing_col_usage_type(mocker):
    LOGGER.info("test_post_validate_csv_fail_missing_col_usage_type() under test_unit_validate.py")
    #  {"error":"InvalidSchema","missing":["bill_id"],"extra":[]}

    # create temp csv file by tempfile module for testing
    csv_content = "bill_id,meter_id,building_id,start_date,end_date"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 422
    mock_post.return_value.json.return_value = {    
        "error":"InvalidSchema",
        "missing":["usage_type"],
        "extra":[]
        }

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+error.+InvalidSchema.+"
    expected_pattern2 = ".+missing.+usage_type.+"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"

# -----------------
def test_post_validate_csv_fail_missing_col_building_id(mocker):
    LOGGER.info("test_post_validate_csv_fail_missing_col_building_id() under test_unit_validate.py")
    #  {"error":"InvalidSchema","missing":["bill_id"],"extra":[]}

    # create temp csv file by tempfile module for testing
    csv_content = "bill_id,meter_id,usage_type,start_date,end_date"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 422
    mock_post.return_value.json.return_value = {    
        "error":"InvalidSchema",
        "missing":["building_id"],
        "extra":[]
        }

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+error.+InvalidSchema.+"
    expected_pattern2 = ".+missing.+building_id.+"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"

# -----------------
def test_post_validate_csv_fail_missing_col_start_date(mocker):
    LOGGER.info("test_post_validate_csv_fail_missing_col_start_date() under test_unit_validate.py")
    #  {"error":"InvalidSchema","missing":["bill_id"],"extra":[]}

    # create temp csv file by tempfile module for testing
    csv_content = "bill_id,meter_id,usage_type,building_id,end_date"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 422
    mock_post.return_value.json.return_value = {    
        "error":"InvalidSchema",
        "missing":["start_date"],
        "extra":[]
        }

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+error.+InvalidSchema.+"
    expected_pattern2 = ".+missing.+start_date.+"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"

# -----------------
def test_post_validate_csv_fail_missing_col_end_date(mocker):
    LOGGER.info("test_post_validate_csv_fail_missing_col_end_date() under test_unit_validate.py")
    #  {"error":"InvalidSchema","missing":["bill_id"],"extra":[]}

    # create temp csv file by tempfile module for testing
    csv_content = "bill_id,meter_id,usage_type,building_id,start_date"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 422
    mock_post.return_value.json.return_value = {    
        "error":"InvalidSchema",
        "missing":["end_date"],
        "extra":[]
        }

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+error.+InvalidSchema.+"
    expected_pattern2 = ".+missing.+end_date.+"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"

# -----------------
def test_post_validate_csv_fail_wrongtype_col_bill_id(mocker):
    LOGGER.info("test_post_validate_csv_fail_wrongtype_col_bill_id() under test_unit_validate.py")
    # '{"error":"InvalidType","row":1,"field":"bill_id","expected":"string"}'

    # create temp csv file by tempfile module for testing
    csv_content = "bill_id,meter_id,usage_type,building_id,start_date,end_date\
                    20.0,15,water,101,2025-02-01,2024-03-01"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 422
    mock_post.return_value.json.return_value = {    
        "error":"InvalidType",
        "row":1,
        "field":"bill_id",
        "expected":"string"
        }

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+error.+InvalidType.+"
    expected_pattern2 = ".+field.+bill_id.+expected.+string"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"

# -----------------
def test_post_validate_csv_fail_wrongtype_col_meter_id(mocker):
    LOGGER.info("test_post_validate_csv_fail_wrongtype_col_meter_id() under test_unit_validate.py")
    # '{"error":"InvalidType","row":1,"field":"meter_id","expected":"integer"}'

    # create temp csv file by tempfile module for testing
    csv_content = "bill_id,meter_id,usage_type,building_id,start_date,end_date\
                    b0001,xxx,water,101,2025-02-01,2024-03-01"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 422
    mock_post.return_value.json.return_value = {    
        "error":"InvalidType",
        "row":1,
        "field":"meter_id",
        "expected":"integer"
        }

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+error.+InvalidType.+"
    expected_pattern2 = ".+field.+meter_id.+expected.+integer"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"

# -----------------
def test_post_validate_csv_fail_wrongtype_col_usage_type(mocker):
    LOGGER.info("test_post_validate_csv_fail_wrongtype_col_usage_type() under test_unit_validate.py")
    # '{"error":"InvalidType","row":1,"field":"usage_type","expected":"string"}'

    # create temp csv file by tempfile module for testing
    csv_content = "bill_id,meter_id,usage_type,building_id,start_date,end_date\
                    b0001,15,9999,101,2025-02-01,2024-03-01"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 422
    mock_post.return_value.json.return_value = {    
        "error":"InvalidType",
        "row":1,
        "field":"usage_type",
        "expected":"string"
        }

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+error.+InvalidType.+"
    expected_pattern2 = ".+field.+usage_type.+expected.+string"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"

# -----------------
def test_post_validate_csv_fail_wrongtype_col_building_id(mocker):
    LOGGER.info("test_post_validate_csv_fail_wrongtype_col_building_id() under test_unit_validate.py")
    # '{"error":"InvalidType","row":1,"field":"usage_type","expected":"string"}'

    # create temp csv file by tempfile module for testing
    csv_content = "bill_id,meter_id,usage_type,building_id,start_date,end_date\
                    b0001,15,water,xyz,2025-02-01,2024-03-01"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 422
    mock_post.return_value.json.return_value = {    
        "error":"InvalidType",
        "row":1,
        "field":"building_id",
        "expected":"integer"
        }

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+error.+InvalidType.+"
    expected_pattern2 = ".+field.+building_id.+expected.+integer"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"

# -----------------
def test_post_validate_csv_fail_wrongtype_col_start_date(mocker):
    LOGGER.info("test_post_validate_csv_fail_wrongtype_col_start_date()) under test_unit_validate.py")
    # '{"error":"InvalidType","row":1,"field":"start_date","expected":"ISO date"}

    # create temp csv file by tempfile module for testing
    csv_content = "bill_id,meter_id,usage_type,building_id,start_date,end_date\
                    b0001,15,water,101,1234567,2024-03-01"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 422
    mock_post.return_value.json.return_value = {    
        "error":"InvalidType",
        "row":1,
        "field":"start_date",
        "expected":"ISO date"
        }

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+error.+InvalidType.+"
    expected_pattern2 = ".+field.+start_date.+expected.+ISO date.+"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"

# -----------------
def test_post_validate_csv_fail_wrongtype_col_end_date(mocker):
    LOGGER.info("test_post_validate_csv_fail_wrongtype_col_end_date()) under test_unit_validate.py")
    # '{"error":"InvalidType","row":1,"field":"end_date","expected":"ISO date"}

    # create temp csv file by tempfile module for testing
    csv_content = "bill_id,meter_id,usage_type,building_id,start_date,end_date\
                    b0001,15,water,101,2024-03-01,1234567"
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as tmp_file:
        tmp_file.write(csv_content)
        temp_file_path = tmp_file.name

    # Mock request.post
    mock_post = mocker.patch("main_brainbox_api.requests.post")

    # Set mock return values
    mock_post.return_value.ok = False
    mock_post.return_value.status_code = 422
    mock_post.return_value.json.return_value = {    
        "error":"InvalidType",
        "row":1,
        "field":"end_date",
        "expected":"ISO date"
        }

    # call the real function
    result = post_validate_csv(temp_file_path)
    # optional - for debug logging
    LOGGER.info(result)

    # Assertions
    expected_pattern1 = ".+error.+InvalidType.+"
    expected_pattern2 = ".+field.+end_date.+expected.+ISO date.+"
    actual_result = str(result)   
    assert re.match(expected_pattern1, actual_result), f"Does not match the test pattern '{expected_pattern1}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"