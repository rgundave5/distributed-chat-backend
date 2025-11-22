# client.py
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

    # ------------messages------------
    def messages(self, message):
        message_url =  f"http://{address}:{port}/chat"
        message_payload = {
            "email":  self.email,
            "password":  self.password,
            "message":  message
        }
        message_response = requests.post(message_url, json=message_payload)
        print(f"{self.name}'s message:", message_response.json())
        return message_response.json()

    # ------------get messages------------
    def get_messages(self):
        message_url =  f"http://{address}:{port}/messages"
        payload = {
            "email":  self.email,
            "password":  self.password,
        }
        response = requests.post(message_url, json=payload)
        print(f"{self.name} received message:", response.json())
        return response.json()

        try:
            data = response.json()
            print(f"{self.name} received messages:", data)
            return data
        except Exception as e:
            print(f"Error decoding JSON from server: {e}, raw response:", response.text)
            return None




# ------------main------------
if __name__=="__main__":
    print("Running")
    # test signup
    # multiple clients
    client1 = Client("JohnDoe", "johndoe12@gmail.com", "junk123")
    client2 = Client("JohnStar", "johndoe12@gmail.com", "junk123")
    client3 = Client("GeorgeFire", "george12@gmail.com", "pass")

    # Signup users
    client1.signup()
    client2.signup()
    client3.signup()

    # Login users
    client1.login()
    client2.login()
    client3.login()

    # Send messages
    client1.messages("Hello everyone! - JohnD")
    client3.messages("Hi John! - George")

    # Retrieve messages from server
    client1.get_messages()
    client3.get_messages()

    # test correct and incorrect login attempts
    #if client1_signup_response.get("message") == "Data stored successfully":
        #client1.login()  # correct
        #client1.password = "wrongpass"
        #client1.login()  # incorrect



# metavariable: describe python file/environment, cant write to them, js read their vals --> use to verify 
# that its entry point to program**

# hw: explore this, check socket examples
# FastAPI deals with this 

# chat:
# 1. authentication
#       email (--> later, profile id), password
#       later: tokens (token based auth: provide auth to server, returns an actual token, for future requests, provide that token, checks if token is correct)
# ack (in networking)
# relatonship (know what user is associated w a message)



# 107,102, 130 (hard programming), marco r (ece 30 chill)











