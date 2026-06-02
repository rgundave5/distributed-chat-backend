# main.py
# START FastAPI SERVER (from FastAPI's first steps)

# CORS? security thing
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, HTTPException
from auth import create_token, verify_token
import asyncio

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

from logic import (
    add_user,
    authenticate_user,
    save_message,
    message_by_convo_id,
    create_group_convo,
    list_user_conversations,
    get_or_create_direct_conversation,
    user_exists
)

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
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    success = add_user(email, password)
    if not success: 
        raise HTTPException(status_code=409, detail="Email already in use")
    else:
        return {"message": "Data stored successfully", "email": email}

# login funct - when user logs in, send email, pword --> check if it exists in table --> return true
@app.post("/login")
# this line defines the path operation function
# it's called by FastAPI whenever it receives a request to URL "/" using a POST operation
# async def or just def can be used
async def login(request: Request):
    data = await request.json() 
    email = data.get("email")
    password = data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")

    success = authenticate_user(email, password)
    if not success:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_token(email)
    return {"message": "Logged in successfully", "token": token}


# ------------------------------------------------------
# Message actions
# ------------------------------------------------------
# just have messages/send, same for messages/receive
@app.post("/messages/send")
async def send_message(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    email = verify_token(token)
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    data = await request.json()
    message_text = data.get("message")
    convo_id = data.get("conversation_id")
    
    if not message_text or not message_text.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if convo_id is None:
        raise HTTPException(status_code=400, detail="Missing conversation_id")

    msg_id = save_message(convo_id, email, message_text)

    if msg_id is None:
        raise HTTPException(status_code=403, detail="Not authorized or conversation not found")
    return {
        "message": "Sent",
        "conversation_id": convo_id,
        "message_id": msg_id
    }

@app.post("/messages/receive/{conversation_id}")
async def receive_messages(conversation_id: int, request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    email = verify_token(token)
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    data = await request.json()
    after_id = data.get("after_id")  # will be None if not sent
    
    msgs = message_by_convo_id(conversation_id, after_id)
    if msgs is None:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return {"messages": msgs}

# -----------------------------------------------------------
# Conversation creation
# -----------------------------------------------------------
@app.post("/conversations/group")
async def create_group_conversation(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    email = verify_token(token)

    if email is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    data = await request.json()
    participants = data.get("participants")
   
    if email not in participants:
        participants.append(email)
    
    for participant in participants:
        if not user_exists(participant):
            raise HTTPException(status_code=404, detail=f"{participant} does not exist")

    convo_id = create_group_convo(data.get("name"), participants)

    if convo_id is None:
        raise HTTPException(status_code=500, detail="Something went wrong")

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
@app.post("/conversations")
async def get_all_convos(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    email = verify_token(token)
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    conversations = list_user_conversations(email)
    if conversations is None:
        raise HTTPException(status_code=500, detail="Something went wrong")

    return {"conversations": conversations}

@app.post("/conversations/direct")
async def create_direct_conversation(request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    email = verify_token(token)
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    data = await request.json()
    other_user = data.get("other_user")

    if not other_user:
        raise HTTPException(status_code=400, detail="Missing other_user field")
    if not user_exists(other_user):
        raise HTTPException(status_code=404, detail="User not found")
    convo_id = get_or_create_direct_conversation(email, other_user)

    if convo_id is None:
        raise HTTPException(status_code=500, detail="Something went wrong")

    return {
        "message": "Direct conversation created",
        "conversation_id": convo_id
    }

#---------------------------------------------------------------------------------
# Conversation deletion/leaving
#---------------------------------------------------------------------------------
@app.delete("/conversations/{conversation_id}")
async def delete_conversation_endpoint(conversation_id: int, request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    email = verify_token(token)
    if email is None:
        return {"message": "Invalid or expired token"}

    success = delete_conversation(conversation_id, email)
    if not success:
        return {"message": "Conversation not found/access denied"} # we don't know which error specifically
        # 5/27 we need better error handling, 
        # on client side, we need to see error code, we need way to standarize them
        # "converstaion 123 not found" --> error message, short status codes are better
        # "conversation_id does not exist" ==> standardize it (check wikipedia status code http)
        # gives user more context on what went wrong/how to fix it
        # same for client, BUT not too much info, keep it vagie
        #   ex: if client is malicious, we cant give away too much, js say smt went wrong
        #   if you give away too much, info leaks
    return {
        "message": "Conversation deleted",
        "conversation_id": conversation_id
    }

# long polling endpoint, using token auth
@app.get("/poll/{convo_id}")
async def poll(convo_id: int, last_id: int, request: Request):
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    email = verify_token(token)
    if email is None:
        return {"message": "Invalid or expired token"}

    while True:
        new_msgs = messages_after(convo_id, last_id)
        if new_msgs:
            return {"messages": new_msgs}
        await asyncio.sleep(1)



# 2/26
# CL interface, two termiinals to send messages 
    # 2 ways to go ab it: python based (easier), or website (web app that connects to server w login) --> css
# next step? interface to work w it, then maybe deploy it (kubernetes pod)
# django? 
# html, css, javascript
# could go back and use react, "angular,vue" ==> various frameworks
# intro:
# start w html, js, css
# discord style chatting 

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
# HW: finished messages_by_convo_id, save_messages

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

# to start server run:  2 
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

