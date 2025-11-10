
import requests

address = "127.0.0.1"
port = 8000

def main():
    print("Running")
    # create url to send data to
    url = f"http://{address}:{port}/signup"
    # create payload - message sent w headers and payload (body of message - data)
    payload = {
        "message":"hello!",
        "email":"johndoe1@gmail.com",
        "password":"junk123"
    }
    response = requests.post(url, json = payload) # payload is json format, so must access the json format 
    print("Server response: ", response.json()) # for formatting
    
    if (response.json()["message"] == "Data stored successfully"): 
        print("success")
    else:
        print("failure")
 

# good practice
if(__name__=="__main__"):
    main()

# metavariable: describe python file/environment, cant write to them, js read their vals --> use to verify 
# that its entry point to program**

# hw: explore this, check socket examples
# FastAPI deals with this 










