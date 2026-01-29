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

    # bad practice to have all these functs in client class, better way to do it:
    
    # -----------create convo-------------
    def create_group_convo(self, participants_array):
        url = f"http://{address}:{port}/conversations/group"
        payload = {
            "email": self.email,
            "password": self.password,
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
    client1 = Client("JerrySeinfeld", "johndoe15@gmail.com", "junk123")
    client2 = Client("JohnTravolta", "johndoe16@gmail.com", "junk123")
    client3 = Client("GeorgeP", "george12@gmail.com", "pass")

    # Signup users
    client1.signup()
    client2.signup()
    client3.signup()

    # Login users
    client1.login()
    client2.login()
    client3.login()

    participants_array1 = ["johndoe15@gmail.com", "johndoe16@gmail.com", "george12@gmail.com"]
    convo_id = client1.create_group_convo(participants_array1)
    print(convo_id)

    # Send direct messages
    #client1.send_messages(convo_id, "Hello John16!")
    #client3.send_messages(convo_id, "Hey!!")

    
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
