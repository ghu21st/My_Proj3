# ---------------------------------------
# QA tech assignement for BrainBox AI - Aug 2025
# Python Integration API Test - query 
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
def empty_upload_file():
    # 
    file_path = "./tests/data/empty_1.csv"  # csv file - column row ok, but data record rows empty
    #
    return file_path

def test_valid_csv_exist(valid_upload_file):
    LOGGER.info("test_valid_csv_exist()")
    #
    assert os.path.exists(valid_upload_file), f"File {valid_upload_file} does not exist"

def test_empty_csv_exist(empty_upload_file):
    LOGGER.info("test_empty_csv_exist()")
    #
    assert os.path.exists(empty_upload_file), f"File {empty_upload_file} does not exist"

def test_brainbox_api_query_ok_csv(brainbox_api_client, upload_url, query_url, valid_upload_file):
    # Verify API upload CSV file, populate to DB table and then run SQL query to check (row count = 10)
    LOGGER.info("test_brainbox_api_query_ok_csv()")
    # Upload --------------
    with open(valid_upload_file, 'rb') as file_obj:
        # variables
        files = {'file': file_obj}
        data = {}
         # send POST to endpoint upload
        response1 = brainbox_api_client.post(upload_url, files = files, data = data)

    # SQL Query ------------
    payload = {"sql": "SELECT * FROM custom_csv LIMIT 10"}
        # send POST to endpoint query
    response = brainbox_api_client.post(query_url, json = payload, timeout = 10)
 
    # assert check
    expected_pattern = ".+columns.+bill_id.+meter_id.+usage_type.+building_id.+start_date.+end_date.+"
    expected_pattern2 = ".+b0001.+15.+water.+101.+2025-02-01.+2024-03-01.+b0002.+21.+electric.+101.+2024-02-01.+2024-03-01.+rowcount.+10"
    actual_result = str(response.text)   #actual_result = json.dumps(response.text)
    LOGGER.info('For checkinging: ' + actual_result + '\n' + expected_pattern + '\n' + expected_pattern2)
    #
    assert response.status_code == 200 
    assert re.match(expected_pattern, actual_result), f"Does not match the test pattern '{expected_pattern}'"
    assert re.match(expected_pattern2, actual_result), f"Does not match the test pattern '{expected_pattern2}'"
    # {"columns":["bill_id","meter_id","usage_type","building_id","start_date","end_date"],"rows":[["b1",100,"kwh",1,"2024-01-01","2024-01-31"],["b0001",15,"water",101,"2025-02-01","2024-03-01"],["b0002",21,"electric",101,"2024-02-01","2024-03-01"],["b0003",103,"water",202,"2025-02-01","2025-03-01"],["b0003",105,"electric",202,"2025-02-01","2025-03-01"],["b0001",15,"water",101,"2025-02-01","2024-03-01"],["b0002",21,"electric",101,"2024-02-01","2024-03-01"],["b0003",103,"water",202,"2025-02-01","2025-03-01"],["b0003",105,"electric",202,"2025-02-01","2025-03-01"],["b0001",15,"water",101,"2025-02-01","2024-03-01"]],"rowcount":10}


def test_brainbox_api_query_empty_csv(brainbox_api_client, upload_url, query_url, empty_upload_file):
    # Verify API upload empty CSV file, failed, no populate to DB table, but SQL query still can check for old records
    LOGGER.info("test_brainbox_api_query_bad_csv()")
    # Upload --------------
    with open(empty_upload_file, 'rb') as file_obj:
        # variables
        files = {'file': file_obj}
        data = {}
         # send POST to endpoint upload
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

    # Query ------------
    payload = {"sql": "SELECT * FROM custom_csv LIMIT 10"}
        # send POST to endpoint query
    response = brainbox_api_client.post(query_url, json = payload, timeout = 10)
 
    # assert check
    #expected_pattern1 = ".+File validated failed.+"
    expected_pattern = ".+columns.+bill_id.+meter_id.+usage_type.+building_id.+start_date.+end_date.+"
    actual_result = str(response.text)   #actual_result = json.dumps(response.text)
    LOGGER.info(actual_result + '\n' + expected_pattern)
    LOGGER.info(response.status_code)
    #
    assert response.status_code == 200 
    assert re.match(expected_pattern, actual_result), f"Does not match the test pattern '{expected_pattern}'"
    # {"error":"InvalidSchema","missing":["building_id"],"extra":[]}
