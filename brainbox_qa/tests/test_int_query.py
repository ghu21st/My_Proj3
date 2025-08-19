# modules
import requests
import os
import json

# url 
url_endpoint_upload = "http://localhost:8000/upload/"
url_endpoint_validate = "http://localhost:8000/validate/"
url_endpoint_query = "http://localhost:8000/athena/query/"

# test data files
file_path = "./data/valid_1.csv"
if not os.path.exists(file_path):
    print(f"The file '{file_path}' does not exist")
    exit()

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
        print(response.json())