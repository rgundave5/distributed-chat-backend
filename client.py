# client.py
import requests
import time

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

    # bad practice to have all these functs in client class, better way to do it:
    
    # -----------create convo-------------
    def create_group_convo(self, name, participants_array):
        url = f"http://{address}:{port}/conversations/group"
        payload = {
            "email": self.email,
            "password": self.password,
            "name": name,
            "participants": participants_array,
        }
        print(payload)
        response = requests.post(url, json=payload)
        print(response.json())
        return response.json()
    
    # implement direct convo, client testing to run all functions, send and recieve messages
   
    # ------------send messages------------
    def send_messages(self, conversation_id, text):
        url = f"http://{address}:{port}/messages/send"
        payload = {
            "sender": self.email,
            "password": self.password,
            "conversation_id": conversation_id,
            "message": text
        }
        response = requests.post(url, json=payload)
        print(response.json())
        return response.json()

    #---------------receive messages--------
    def get_messages(self, conversation_id):
        url = f"http://{address}:{port}/messages/receive/{conversation_id}"
        payload = {
            "email": self.email,
            "password": self.password
        }
        response = requests.post(url, json=payload)
        print(response.json())
        return response.json()

    #----------create direct conversation--------
    def create_direct(self, other_user):
        response = requests.post(
            f"http://{address}:{port}/conversations/direct",
            json={
                "email": self.email,
                "password": self.password,
                "other_user": other_user
            }
        )
        print("Direct Convo Created:", response.json())
        return response.json()

    #----------create group conversation-------- 
    def create_group(self, name, participants):
        response = requests.post(
            f"http://{address}:{port}/conversations/group",
            json={
                "email": self.email,
                "password": self.password,
                "name": name,
                "participants": participants
            }
        )
        print("Group Convo Created:", response.json())

    #----------get all conversations-------- 
    def get_all_conversations(self):
        response = requests.post(
            f"http://{address}:{port}/conversations",
            json={
                "email": self.email,
                "password": self.password
            }
        )
        print("All Conversations:", response.json())

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
    suffix = str(int(time.time()))
    client1 = Client("Jerry",  f"jerry{suffix}@gmail.com",  "pass1")
    client2 = Client("George", f"george{suffix}@gmail.com", "pass2")
    client3 = Client("Elaine", f"elaine{suffix}@gmail.com", "pass3")    

    # Signup users
    client1.signup()
    client2.signup()
    client3.signup()

    # Login users
    client1.login()
    client2.login()
    client3.login()

    # direct convo between client1 and client2
    direct_resp = client1.create_direct(client2.email)
    direct_id = direct_resp.get("conversation_id")

    # group convo with all 3 clients
    group_resp = client1.create_group_convo(
        "Test Group",
        [client1.email, client2.email, client3.email]
    )
    group_id = group_resp.get("conversation_id")

    # conversations for each user
    client1.get_all_conversations()
    client2.get_all_conversations()
    client3.get_all_conversations()

    # send messages on both convos
    client1.send_messages(direct_id, "Hey George, it's you and I talking in this chat!")
    client2.send_messages(direct_id, "Hey Jerry!")

    client1.send_messages(group_id, "Hello everyone!")
    client2.send_messages(group_id, "Hi Jerry!")
    client3.send_messages(group_id, "What's up guys!")
    
    # get messages
    client1.get_messages(direct_id)
    client1.get_messages(group_id)

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



# 107,102, 130 (hard programming)
