import requests
import os

url_endpoint_upload = "http://localhost:8000/upload/"
url_endpoint_validate = "http://localhost:8000/validate/"

file_path = "./data/valid_1.csv"
if not os.path.exists(file_path):
    print(f"The file '{file_path}' does not exist")
    exit()

with open(file_path, 'rb') as file_obj: 
    files = {'file': file_obj}
    data = {}
    response = requests.post(url_endpoint_validate, files=files, data=data)

    if response.ok:
        print("File validated successfully")
        print(response.text)
    else:
        print("File validated failed")
        print(f"Status code: {response.status_code}")
        print(response.text)
