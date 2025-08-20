# modules
import requests
import os
import json

# url 
url_endpoint_upload = "http://localhost:8000/upload/"
url_endpoint_validate = "http://localhost:8000/validate/"
url_endpoint_query = "http://localhost:8000/athena/query/"

# CSV file
valid_csv_file = "./tests/data/valid_1.csv"
 
# post csv file to API endpoint - upload
def post_upload_csv(file):
    # test data files
    file_path = file
    if not os.path.exists(file_path):
        raise ValueError(f"The file '{file_path}' does not exist")
    response = None    

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
            print(str(response.text))
        else:
            print(response.status_code)
            print(response.text)
            raise ValueError("File upload failed")
        # 
    return response.json()

# post csv file to API endpoint - validate
def post_validate_csv(file):
    file_path = file
    if not os.path.exists(file_path):
        raise ValueError(f"The file '{file_path}' does not exist")
    response = None

    # POST - validate
    with open(file_path, 'rb') as file_obj: 
        files = {'file': file_obj}
        data = {}
        response = requests.post(url_endpoint_validate, files=files, data=data)

        if response.ok:
            print("File validate successfully")
            print(response.text)
        else:
            print(f"Status code: {response.status_code}")
            print(response.text)
            raise ValueError("File validate failed")
    #
    return response.json() 

# post csv file and check SQL query to API endpoint - query
def post_query_csv(file):
    file_path = file
    if not os.path.exists(file_path):
        raise ValueError(f"The file '{file_path}' does not exist")
    response = None

    # POST - query
    with open(file_path, 'rb') as file_obj:
        # variables
        files = {'file': file_obj}
        payload = {"sql": "SELECT * FROM custom_csv LIMIT 10"}
        headers = {"Content-Type": "application/json"} # optional 

        # send POST to endpoint
        #response = requests.post(url_endpoint_query, json = payload, timeout = 10)
        response = requests.post(url_endpoint_query, headers = headers, data = json.dumps(payload), timeout = 10)
        # check
        if response.ok:
            # upload ok
            print("Query successful")
            print(response.status_code)
            print(response.text)
        else:
            print(response.status_code)
            print(response.text)
            #print(response.json())
            raise ValueError("Query failed")
    #
    return response.json() 

#-------------------------------------
# Call the functions under main
if __name__ == '__main__':
    post_validate_csv(valid_csv_file)
    post_upload_csv(valid_csv_file)
    post_query_csv(valid_csv_file)

