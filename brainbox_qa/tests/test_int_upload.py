import os
import requests

url_endpoint_upload = "http://localhost:8000/upload/"
url_endpoint_validation = ""

file_path = "./data/valid_1.csv"
if not os.path.exists(file_path):
    print(f"The file '{file_path}' does not exist")
    exit()
    
with open(file_path, 'rb') as file_obj: 
    files = {'file': file_obj}
    data = {}
    response = requests.post(url_endpoint_upload, files=files, data=data)

    if response.ok:
        print("File uploaded successfully")
        print(response.text)
    else:
        print("File upload failed")
        print(f"Status code: {response.status_code}")
        print(response.text)


