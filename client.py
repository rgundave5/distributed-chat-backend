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
    #def messages(self, message):
        # tells us where to send 
        # mailbox ex: we want to send to client's mailbox
        # specifies where message ends up
        #message_url =  f"http://{address}:{port}/chat"
        # chat endpoint: this tells me this person wants to chat (functionality)
        # 
       # message_payload = {
           # "email":  self.email,
            #"password":  self.password,
            #"message":  message
       # }
        # requests makes it easier (python lib)
       # message_response = requests.post(message_url, json=message_payload)
        #print(f"{self.name}'s message:", message_response.json())
        #return message_response.json()

    # -----------direct messages----------
    def send_direct(self, receiver, text):
        url = f"http://{address}:{port}/messages/direct/send"
        payload = {
            "sender": self.email,
            "password": self.password,
            "receiver": receiver,
            "message": text
        }
        response = requests.post(url, json=payload)
        print("DIRECT:", response.json())
        return response.json()
        
    # ------------group messages------------
    def send_group(self, group_name, text):
        url = f"http://{address}:{port}/messages/group/send"
        payload = {
            "sender": self.email,
            "password": self.password,
            "group_name": group_name,
            "message": text
        }
        response = requests.post(url, json=payload)
        print("GROUP:", response.json())
        return response.json()

    # ------------get direct messages------------
    def get_direct_message(self, message_id):
        url = f"http://{address}:{port}/messages/direct/receive/{message_id}"

        payload = {
            "email": self.email,
            "password": self.password
        }

        response = requests.post(url, json=payload)
        print(f"{self.name} received direct message:", response.json())
        return response.json()
    
    # ------------get group messages------------
    def get_group_message(self, message_id):
        url = f"http://{address}:{port}/messages/group/receive/{message_id}"

        payload = {
            "email": self.email,
            "password": self.password
        }

        response = requests.post(url, json=payload)
        print(f"{self.name} received group message:", response.json())
        return response.json()
        
# endpoints
# no https, 
# buy_url = f"http://{address}:{port}/buy/items"
# buy_url = f"http://{address}:{port}/buy/services"
# sell_url = f"http://{address}:{port}/sell/items"
# sell_url = f"http://{address}:{port}/sell/services"
    # endpoint within an endpoint (buy/sell services & items)
    # easy too do this
    # hw: watch freecodecamp fastapi course for beginners
    # hw to do: 

# edit_profile_url = f"http://{address}:{port}/edit"


# ------------main------------
if __name__=="__main__":
    print("Running")
    # test signup
    # multiple clients
    client1 = Client("JerrySeinfeld", "johndoe13@gmail.com", "junk123")
    client2 = Client("JohnTravolta", "johndoe14@gmail.com", "junk123")
    client3 = Client("GeorgeP", "george12@gmail.com", "pass")

    # Signup users
    client1.signup()
    client2.signup()
    client3.signup()

    # Login users
    client1.login()
    client2.login()
    client3.login()

    # Send direct messages
    client1.send_direct("Hello everyone! - JohnD")
    client3.send_direct("Hi John! - George")

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
