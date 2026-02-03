# main.py
# START FastAPI SERVER (from FastAPI's first steps)
from fastapi import FastAPI, Request
from logic import (
    add_user,
    authenticate_user,
    save_message,
    get_message_by_convo_id,
    create_group_convo,
    get_or_create_direct_conversation,
    user_exists
)

# create a FastAPI "instance"
app = FastAPI()

# An async function is a special function that handles long-running tasks 
# (like network requests or file reading) without freezing your application
#   must use await keyword --> data = await request.json()
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

# login funct - when user logs in, send email, pword --> check if it exists in table --> return true
@app.post("/login")
# this line defines the path operation function
# it's called by FastAPI whenever it receives a request to URL "/" using a POST operation
# async def or just def can be used
async def login(request: Request):
    data = await request.json() 

    email = data.get("email")
    password = data.get("password")
    
    success = authenticate_user(email, password)
    if success:
        return {"message": "Logged in successfully", "received": data}
    else:
        return {"message": "Invalid credentials"}


# ------------------------------------------------------
# Message actions
# ------------------------------------------------------
# just have messages/send, same for messages/receive
@app.post("/messages/send")
async def send_message(request: Request):
    data = await request.json() 
    email = data.get("sender")
    password = data.get("password")
    # not needed
    # receiver = data.get("receiver")
    # update variables
    message_text = data.get("message")
    convo_id = data.get("conversation_id")

    if not authenticate_user(email, password):
        return {"message": "Invalid credentials"} 

    # make funct to chcek if convo id is valid in logic.py
    # check if user exists in convo with funct in logic.py
    msg_id = save_message(convo_id, email, message_text)

    if msg_id is None:
        return {"message": "Not authorized or conversation invalid"}

    return {
        "message": "Sent",
        "conversation_id": convo_id,
        "message_id": msg_id
    }

# swap message id w receiver or gc --> do this in url, or request's body
@app.post("/messages/receive/{conversation_id}")
async def receive_messages(conversation_id: int, request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    if not authenticate_user(email, password):
        return {"message": "Invalid credentials"}
    ##
    # verify membership (2nd security check)
    with engine.connect() as conn:
        membership = conn.execute(
            select(convo_participants)
            .where(
                (convo_participants.c.conversation_id == conversation_id) &
                (convo_participants.c.user_email == email)
            )
        ).fetchone()

        if not membership:
            return {"error": "Access denied"}

        msgs = conn.execute(
            select(messages)
            .where(messages.c.conversation_id == conversation_id)
            .order_by(messages.c.date)
        )

        return {
            "messages": [dict(row._mapping) for row in msgs]
        }

# -----------------------------------------------------------
# Conversation creation
# -----------------------------------------------------------
@app.post("/conversations/group")
async def create_group_conversation(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")
    participants = data.get("participants")
    print(email, password)

    if not authenticate_user(email, password):
        print("authenticate_user entered")
        return {"message": "Invalid credentials, authentication error"}
   
    if email not in participants:
        participants.append(email)
    
    for key in participants:
        if user_exists(key) is False: 
            return {"message": "Invalid credentials, participants are invalid"}

    convo_id = create_group_convo(gc_name, participants_array)

    if convo_id is None:
        return {"message": "Failed to create group"}

    return {
        "message": "Group created",
        "conversation_id": convo_id
    }

# another endpoint: loads convo given convo id!!

# is user closes app and wants to see all convos theyre in again
# input: user email, password for auth
# output: list of all the convos they're in (list of convo ids)
# brainstorm of endpoint structure:
#   flow from user side to server and back to user
#   client sends POST request to access all convos --> main.py --> logic.py --> db --> main.py --> client
#   top down development/coding (preferred bc things are always changing --> indep project): brainstorm endpoint assuming db and logic.py are already made, start w high levelled, then low levelled 
#   as opposed to down top dev: low levlled --> high levelled
# idea generation: incubation, validated learning (talk to users, check market) --> keep validating the idea
# ece 186
@app.post("conversations")
async def get_all_convos(request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    if not authenticate_user(email, password):
        return {"message": "Invalid credentials"}

    conversations = list_user_conversations(email)

    return {
        "conversations": conversations
    }
    # call logic.py funct
    # return all convo ids

@app.post("/conversations/direct")
async def create_direct_conversation(request: Request):
    data = await request.json()

    email = data.get("email")
    password = data.get("password")
    other_user = data.get("other_user")

    if not authenticate_user(email, password):
        return {"message": "Invalid credentials, email is invalid"}

    if not user_exists(other_user):
        return {"message": "Invalid credentials, other email provided is invalid"}

    convo_id = get_or_create_direct_conversation(email, other_user)

    if convo_id is None:
        return {"message": "Failed to create group"}

    return {
        "message": "Direct conversation created",
        "conversation_id": convo_id
    }

#---------------------------------------------------------------------------------
# Conversation deletion/leaving
#---------------------------------------------------------------------------------
@app.delete("/conversations/{conversation_id}")
async def delete_conversation_endpoint(conversation_id: int, request: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    if not authenticate_user(email, password):
        return {"message": "Invalid credentials"}

    success = delete_conversation(conversation_id, email)

    if not success:
        return {"message": "Conversation not found/access denied"}

    return {
        "message": "Conversation deleted",
        "conversation_id": conversation_id
    }



# 1/6
# just have send and receive, don't have separate for group and direct (except for making convos in logic.py)
# work on create_direct_conversation in main.py (for groyp too, (messages/send enpoint, messages/receive endpoint) pass convo id for these) 
# and update logic.py (user_exists funct for receiver's email)
# implement as many endpoints as u can 

# Update:
# Videos: 
#   ! How the Web Works HTTP REST APIs
#   ! python syntax specific to chat app
#   ! SQL Tutorial - Full Database Course
#       sql (language) --> sqlite (db) --> sqlalchemy (translator (ORM): python -> sql -> sends to sqlite)
#   Database Design
#   SQLAlchemy Core
#   FastAPI & FastAPI Security
#   Backend System Design Basics
#   Chat System System Design
#   Distributed Systems
# Understanding existing code: 
# HW: finished get_messages_by_convo_id, save_messages

# 12/30
# finish get_messages_by_convo_id in logic.py
# try to start save_messages 
# ask abt combining mentorship program w gdgc (proposal), talk to harshada 


# 12/3
# client doesnt have message id --> receiving logic?
# receive messages by gc id or receiver id --> maybe add column in messages table for group and direct (split)
# all messages in direct message
# make sure messages are specific to the receiver (w receiver id and group chat id)
# i could be getting messages not sent to me
# option1: store everything in gc id or direct message id --> do this
# option2: uses existing receive message id funct, store message id itself --> more requests needed for each message fetched (less efficient)
# update client too!
# freecodecamp: sql basics (foreign key tutorial) WATCH

# 

# 11/25 update
# 1. added new endpoints:
# POST /messages/direct/send
# GET  /messages/direct/receive/{message_id}
# POST /messages/group/send
# GET  /messages/group/receive/{message_id}
# 2. added messages table to db
# 3. logic.py: added message saving logic and message receiving logic
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
