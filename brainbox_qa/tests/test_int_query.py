# modules
import pytest
import re

from pathlib import Path

import requests
import os

@pytest.fixture(scope="session")
def upload_url():
    return "http://localhost:8000/upload/"

@pytest.fixture(scope="session")
def validate_url():
    return "http://localhost:8000/validate/"

@pytest.fixture(scope="session")
def query_url():
    return "http://localhost:8000/athena/query"

@pytest.fixture(scope="session")
def brainbox_api_client():
    # tear up - define requests default session with headers 
    session = requests.Session()
    session.header.update( {"Content-Type": "application/json"})
    #
    yield session
    # tear down
    session.close()

@pytest.fixture(scope="function")
def valid_upload_file():
    # 
    file_name = "valid_1.csv"
    file_path = '.data/' + file_name
    #
    return file_path

def test_valid_csv_exist(valid_upload_file):
    #
    assert os.path.exists(valid_upload_file), f"File {valid_upload_file} does not exist"
    assert os.path.isfile(valid_upload_file), f"Path {valid_upload_file} is not a file"

def test_brainbox_api_upload(brainbox_api_client, upload_url, valid_upload_file):
    with open(valid_upload_file, 'rb') as file_obj:
        # variables
        files = {'file': file_obj}
        data = {}
 
        # send POST to endpoint
        response = brainbox_api_client.post(upload_url, files = files, data = data)
 
    # assert check
    pattern = "\"status\":\"ok\".+\"stored\":\"local_state/uploads/valid_1.csv\".+\"crawler_marker\"\:\"local_state/glue/bills_crawler_"
    assert response.status_code == 200 
    assert re.match(pattern, response.text), f"Does not match the test pattern '{pattern}'"

'''
# POST - upload 
with open(file_path, 'rb') as file_obj:
    # variables
    files = {'file': file_obj}
    data = {}
    # send POST to endpoint
    response = requests.post(url_endpoint_upload, files = files, data = data)
    # check
    if response.ok:
        # upload ok
        print("File upload successful")
        print(response.status_code)
        print(response.text)
    else:
        print("File upload failed")
        print(response.status_code)
        print(response.text)

# POST - query
with open(file_path, 'rb') as file_obj:
    # variables
    files = {'file': file_obj}
    payload = {"sql": "SELECT * FROM custom_csv LIMIT 10"}
        #headers = {"Content-Type": "application/json"} # optional 

    # send POST to endpoint
    response = requests.post(url_endpoint_query, json = payload, timeout = 10)
        # response = requests.post(url_endpoint_query, headers = headers, data = json.dumps(payload), timeout = 10)
    # check
    if response.ok:
        # upload ok
        print("File upload successful")
        print(response.status_code)
        print(response.text)
    else:
        print("File upload failed")
        print(response.status_code)
        print(response.text)
        #print(response.json())
'''