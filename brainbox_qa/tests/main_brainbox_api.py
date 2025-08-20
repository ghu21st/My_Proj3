# modules
import requests
import os
import json

#--------------------------------------------
# url 
url_endpoint_upload = "http://localhost:8000/upload/"
url_endpoint_validate = "http://localhost:8000/validate/"
url_endpoint_query = "http://localhost:8000/athena/query/"

# CSV file
valid_csv_file = "./tests/data/valid_1.csv"
invalid_csv_file = './tests/data/invalid_1.csv'
empty_csv_file = './tests/data/empty_1.csv'
nonexist_csv_file = './tests/data/xxxxx.csv'
  
# -------------------------------------------
# post csv file to API endpoint - upload
def post_upload_csv(file):
    # test data files
    file_path = file
    if not os.path.exists(file_path):
        #raise ValueError(f"The file '{file_path}' does not exist")
        ret = f"The CSV file does not exist"
        print(ret)
        return ret

    # POST - upload 
    response = None    
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
            print("File upload failed")
            #raise ValueError("File upload failed")
        # 
    return response.json()

# post csv file to API endpoint - validate
def post_validate_csv(file):
    file_path = file
    if not os.path.exists(file_path):
        #raise ValueError(f"The file '{file_path}' does not exist")
        ret = f"The CSV file does not exist"
        print(ret)
        return ret

    # POST - validate
    response = None
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
            print("File validate failed")
            #raise ValueError("File validate failed")
    #
    return response.json() 

# post csv file and check SQL query to API endpoint - query
def post_query_csv(file):
    file_path = file
    if not os.path.exists(file_path):
        #raise ValueError(f"The file '{file_path}' does not exist")
        ret = f"The CSV file does not exist"
        print(ret)
        return ret

    # POST - query
    response = None
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
            print("Query failed")
            #raise ValueError("Query failed")
    #
    return response.json() 

#-------------------------------------
# Call the functions under main
if __name__ == '__main__':
    # Valid CSV
    print("-------- Valid CSV ------------")
    post_validate_csv(valid_csv_file)
    post_upload_csv(valid_csv_file)
    post_query_csv(valid_csv_file)

    # Empty CSV
    print("-------- Empty CSV ------------")
    post_validate_csv(empty_csv_file)
    post_upload_csv(empty_csv_file)
    post_query_csv(empty_csv_file)

    # Invalid CSV (missing column)
    print("-------- Inalid CSV ------------")
    post_validate_csv(invalid_csv_file)
    post_upload_csv(invalid_csv_file)
    post_query_csv(invalid_csv_file)

    # Non-exist CSV 
    print("-------- Non-exist CSV ------------")
    post_validate_csv(nonexist_csv_file)
    post_upload_csv(nonexist_csv_file)
    post_query_csv(nonexist_csv_file)
