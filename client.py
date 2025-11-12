
import requests

address = "127.0.0.1"
port = 8000

class Client:
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password

    # ------------signup------------
    def signup(self):
        # create url to send data to
        signup_url = f"http://{address}:{port}/signup"
        # create payload - message sent w headers and payload (body of message - data)
        signup_payload = {
            "message":"hello!",
            "email": self.email,
            "password":  self.password
        }
        signup_response = requests.post(signup_url, json = signup_payload) # payload is json format, so must access the json format 
        print(f"{self.name} signup response: ", signup_response.json()) # for formatting
        return signup_response.json()
        
    # ------------login------------
    def login(self):
        login_url = f"http://{address}:{port}/login"
        login_payload = {
            "message":"hello!",
            "email":  self.email,
            "password":  self.password
        }
        login_response = requests.post(login_url, json=login_payload)
        print(f"{self.name} login response:", login_response.json())
        return login_response.json()

# ------------main------------
if __name__=="__main__":
    print("Running")
    # test signup
    # multiple clients
    client1 = Client("John", "johndoe10@gmail.com", "junk123")
    client2 = Client("Roshni", "roshni2@gmail.com", "pword")
    client3 = Client("George", "george1@gmail.com", "pass")

    client1_signup_response = client1.signup()
    client2_signup_response = client2.signup()
    client3_signup_response = client3.signup()

    # test correct and incorrect login attempts
    if client1_signup_response.get("message") == "Data stored successfully":
        client1.login()  # correct
        client1.password = "wrongpass"
        client1.login()  # incorrect

    if client2_signup_response.get("message") == "Data stored successfully":
        client2.login()  # correct
        client2.password = "wrongpass"
        client2.login()  # incorrect

    if client3_signup_response.get("message") == "Data stored successfully":
        client3.login()  # correct
        client3.password = "wrongpass"
        client3.login()  # incorrect


# metavariable: describe python file/environment, cant write to them, js read their vals --> use to verify 
# that its entry point to program**

# hw: explore this, check socket examples
# FastAPI deals with this 










