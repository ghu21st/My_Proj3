# ---------------------------------------
# QA tech assignement for BrainBox AI - Aug 2025
# Gang Hu 
# --------------------------------
# modules
import pytest
import re
import logging
import requests
import os
import json
from pathlib import Path

LOGGER = logging.getLogger(__name__) # use config in pytest.ini
# -------------------------------------------------
@pytest.fixture(scope="session")
def upload_url():
    return "http://localhost:8000/upload/"

@pytest.fixture(scope="session")
def validate_url():
    return "http://localhost:8000/validate/"

@pytest.fixture(scope="session")
def query_url():
    return "http://localhost:8000/athena/query"

@pytest.fixture(scope="function")
def brainbox_api_client():
    # tear up - define requests default session with headers 
    session = requests.Session()
    #session.headers.update( {"Content-Type": "application/json"})
    #
    yield session
    # tear down
    session.close()

@pytest.fixture(scope="function")
def valid_upload_file():
    # 
    file_path = "./tests/data/valid_1.csv"
    #file_path = '.data/' + file_name
    #
    return file_path

@pytest.fixture(scope="function")
def invalid_upload_file():
    # 
    file_path = "./tests/data/invalid_1.csv"
    #
    return file_path

@pytest.fixture(scope="function")
def empty_upload_file():
    # 
    file_path = "./tests/data/empty_1.csv"  # csv file - column row ok, but data record rows empty
    #
    return file_path

def test_valid_csv_exist(valid_upload_file):
    LOGGER.info("test_valid_csv_exist()")
    #
    assert os.path.exists(valid_upload_file), f"File {valid_upload_file} does not exist"

def test_invalid_csv_exist(invalid_upload_file):
    LOGGER.info("test_invalid_csv_exist()")
    #
    assert os.path.exists(invalid_upload_file), f"File {invalid_upload_file} does not exist"

def test_empty_csv_exist(empty_upload_file):
    LOGGER.info("test_empty_csv_exist()")
    #
    assert os.path.exists(empty_upload_file), f"File {empty_upload_file} does not exist"

def test_brainbox_api_upload_ok_csv(brainbox_api_client, upload_url, valid_upload_file):
    LOGGER.info("test_brainbox_api_upload_ok_csv()")
    #
    with open(valid_upload_file, 'rb') as file_obj:
        # variables
        files = {'file': file_obj}
        data = {}
 
        # send POST to endpoint
        response = brainbox_api_client.post(upload_url, files = files, data = data)
 
    # assert check
    expected_pattern = ".+status.+ok.+stored.+local_state/uploads.+crawler_marker.+local_state/glue/bills_crawler_.*"
    actual_result = str(response.text)   #actual_result = json.dumps(response.text)
    LOGGER.info(actual_result + '\n' + expected_pattern)
    #
    assert response.status_code == 200 
    assert re.match(expected_pattern, actual_result), f"Does not match the test pattern '{expected_pattern}'"
    # {"status":"ok","stored":"local_state/uploads/valid_1.csv","crawler_marker":"local_state/glue/bills_crawler__1755641316__abdb60140b924dc492f3736f3b73a9f1.marker","rows_inserted":4}

def test_brainbox_api_upload_bad_csv(brainbox_api_client, upload_url, invalid_upload_file):
    LOGGER.info("test_brainbox_api_validate_bad_csv()")
    #
    with open(invalid_upload_file, 'rb') as file_obj:
        # variables
        files = {'file': file_obj}
        data = {}
 
        # send POST to endpoint
        response = brainbox_api_client.post(upload_url, files = files, data = data)
 
    # assert check
    #expected_pattern1 = ".+File validated failed.+"
    expected_pattern = ".+error.+InvalidSchema.+missing.+building_id.+"
    actual_result = str(response.text)   #actual_result = json.dumps(response.text)
    LOGGER.info(actual_result + '\n' + expected_pattern)
    #
    assert response.status_code == 422 
    assert re.match(expected_pattern, actual_result), f"Does not match the test pattern '{expected_pattern}'"
    # {"error":"InvalidSchema","missing":["building_id"],"extra":[]}

def test_brainbox_api_upload_empty_csv(brainbox_api_client, upload_url, empty_upload_file):
    LOGGER.info("test_brainbox_api_validate_empty_csv()")
    #
    with open(empty_upload_file, 'rb') as file_obj:
        # variables
        files = {'file': file_obj}
        data = {}
 
        # send POST to endpoint
        response = brainbox_api_client.post(upload_url, files = files, data = data)
 
    # assert check
    #expected_pattern1 = ".+File validated failed.+"
    expected_pattern = ".+error.+InvalidSchema.+missing.+building_id.+"
    actual_result = str(response.text)   #actual_result = json.dumps(response.text)
    LOGGER.info(actual_result + '\n' + expected_pattern)
    #
    assert response.status_code == 422 
    assert re.match(expected_pattern, actual_result), f"Does not match the test pattern '{expected_pattern}'"
    # {"error":"InvalidSchema","missing":["building_id"],"extra":[]}
