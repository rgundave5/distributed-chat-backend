# main.py
# START FastAPI SERVER (from FastAPI's first steps)
from fastapi import FastAPI, Request
from logic import add_user, authenticate_user, save_direct_message, save_group_message, get_message_by_id

# create a FastAPI "instance"
app = FastAPI()

# confirmation check that server is running
@app.get("/")
async def root():
    return {"message": "Server is running!"}


# API ENDPOINTS ------------------------------------------------------------------------------

# API endpoints (the path client takes essentially, like a doorway to the server) --> 
# their HTTP methods or operations (like POST, GET, PUT, DELETE) - used for a specific action
# examples:
# POST: to create data, GET: to read data, PUT: to update data, DELETE: to delete data.

# create /signup endpoint (creating user account)
@app.post("/signup")
async def signup(request: Request):
    data = await request.json() # receives the JSON data from client
    email = data.get("email")
    password = data.get("password")
    
    success = add_user(email, password)
    if success: 
        return {"message": "Data stored successfully", "email": email}  # success message
    else:
        return {"message": "Error storing data"}

# create /login endpoint (authentication)
# login funct - when user logs in, send email, pword --> check if it exists in table --> return true
@app.post("/login")
# this line defines the path operation function
# it's called by FastAPI whenever it receives a request to URL "/" using a POST operation
# async def or just def can be used
async def login(request: Request):
    data = await request.json() 
    # added these two lines after making authenticate_user 
    email = data.get("email")
    password = data.get("password")
    
    success = authenticate_user(email, password)
    if success:
        return {"message": "Logged in successfully", "received": data}
    else:
        return {"message": "Invalid credentials"}


# ------------------------------------------------------
# DIRECT MESSAGE ENDPOINTS
# ------------------------------------------------------

@app.post("/messages/direct/send")
async def send_direct_message(request: Request):
    data = await request.json() 
    email = data.get("sender")
    password = data.get("password")
    receiver = data.get("receiver")
    message_text = data.get("message")

    if not authenticate_user(email, password):
        return {"message": "Invalid credentials"} 
   
    message_id = save_direct_message(
        sender=email,
        receiver=receiver,
        message=message_text
    )

    return {
        "message": "Direct message sent",
        "id": message_id
    }

@app.post("/messages/direct/receive/{message_id}")
async def receive_direct_message(message_id: int):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    if not authenticate_user(email, password):
        return {"message": "Invalid credentials"}

    message = get_message_by_id(message_id)

    if not message or message["receiver"] is None:
        return {"message": "Message not found"}

    return {
        "message": "Direct message retrieved",
        "data": message
    }

# ------------------------------------------------------
# GROUP MESSAGE ENDPOINTS
# ------------------------------------------------------
@app.post("/messages/group/send")
async def send_group_message(request: Request):
    data = await request.json()

    email = data.get("sender")
    password = data.get("password")
    group_name = data.get("group_name")
    message_text = data.get("message")

    if not authenticate_user(email, password):
        return {"message": "Invalid credentials"}

    message_id = save_group_message(
        sender=email,
        group_name=group_name,
        message=message_text
    )

    return {
        "message": "Group message sent",
        "id": message_id
    }

@app.post("/messages/group/receive/{message_id}")
async def receive_group_message(message_id: int):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    if not authenticate_user(email, password):
        return {"message": "Invalid credentials"}
    message = get_message_by_id(message_id)

    if not message or message["group_name"] is None:
        return {"message": "Message not found"}

    return {
        "message": "Group message retrieved",
        "data": message
    }

# 11/25 update
# 1. added new endpoints:
# POST /messages/direct/send
# GET  /messages/direct/receive/{message_id}
# POST /messages/group/send
# GET  /messages/group/receive/{message_id}
# 2. added messages table to db
# 3. logic.py: added message saving logic but didn't do message receiving logic
# 4. logic.py: get_message_by_id
# 5. updated client.py




# task list:
#   1. add endpoints to our chat app, update existing endpoints
#   2. update logic so it can handle the new path params 
#   3. update db logic (tables - store emsssages differently now), returns message id when u send message

# watch: fastapi, sqlalchemny, databses, how to process it, write codeon your own, dont c & p, 

# systems design for doimg the other chat/messages stuff --> always do ssytems design
# systems security --> info in url, info must be secure
# no authentication? then u can talk to js anybody by changing the url {user}
# i can js copy that url and send message to someone idk --> no security
# server should have task of deciding if u can access url or send messages on that url 
# bad idea to put username in path param
# ok to put gc name or person ur talking to's username (this stuff changes frequently)
# benefit of chnaging url path (longer or shorter):
    # can specify versions (so u dont get old data)
    # main benefits: organization 
    # in discord u have image id in url by deault, direct access (another benefit)
    # all info can be stored in url w path params
    # discord url code 
    # for images all info is in url 

    # we coudl do message id's
    # messages/group/send
    # messages/direct/send
    # messages/group/receive
    # messages/direct/receive{message_id}




# to start server run:  uvicorn main:app --reload 
# FastAPI listens at http://127.0.0.1:8000
# send a request using curl command
# FastAPI receives it, runs endpoint, sends JSON back
# {"message": "Server is running!"}

# create client file to test
# make login and signup functions that run direclty - move all yhthe logic from client.py - make its own funct
# learn: python knowledge (freecode camp vids), topics: working w different data types (list, dict, access data, etc)
# try creating multiple clietnt.py and run them separately 

# implement client that will send messages
# hw: write the client to be able to send messages, function added, now do implemenation, client1.message
# we can send memssages to server, we need to be able to receive messages
# implement a get messages endpiint that returns all messages to client and prints it out
    # 1. database.py - messages table
    # 2. logic.py - save_messages() function --> takes users' email + message and inserts into DB, then returns true or false
    # 3. main.py - /messages GET Endpoint
            # to authenticate user first, read messages from DB, send them back to the client as JSON
    # 4. logic.py - added helper function get_all_messages() so that server can fetch messages
    # 5. 