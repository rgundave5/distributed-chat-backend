
import requests

address = "127.0.0.1"
port = 8000

# ------------signup------------
def signup(email, password):
    # create url to send data to
    signup_url = f"http://{address}:{port}/signup"
    # create payload - message sent w headers and payload (body of message - data)
    signup_payload = {
        "message":"hello!",
        "email": email,
        "password": password
    }
    signup_response = requests.post(signup_url, json = signup_payload) # payload is json format, so must access the json format 
    print("Signup response: ", signup_response.json()) # for formatting
    return signup_response.json()
    
# ------------login------------
def login(email, password):
    login_url = f"http://{address}:{port}/login"
    login_payload = {
        "message":"hello!",
        "email": email,
        "password": password
    }
    login_response = requests.post(login_url, json=login_payload)
    print("Login response:", login_response.json())
    return login_response.json()

# ------------main------------
def main():
    print("Running")
    # test signup
    # multiple clients
    client1_signup_response = signup("johndoe9@gmail.com", "junk123")
    client2_signup_response = signup("roshni1@gmail.com", "pword")

    # test correct and incorrect login attempts
    if client1_signup_response.get("message") == "Data stored successfully":
        login("janedoe9@gmail.com", "junk123")  # correct
        login("janedoe9@gmail.com", "wrongpass")  # incorrect
    
    if client2_signup_response.get("message") == "Data stored successfully":
        login("roshni_g1@gmail.com", "pword")  # correct
        login("roshni_g1@gmail.com", "wrongpass")  # incorrect


# good practice
if(__name__=="__main__"):
    main()


# metavariable: describe python file/environment, cant write to them, js read their vals --> use to verify 
# that its entry point to program**

# hw: explore this, check socket examples
# FastAPI deals with this 










