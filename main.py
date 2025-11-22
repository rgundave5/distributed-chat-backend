# main.py
# START FastAPI SERVER (from FastAPI's first steps)
from fastapi import FastAPI, Request
from logic import add_user, authenticate_user, save_message, get_all_messages

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

# chat endpoint
@app.post("/chat")
async def chat(request: Request):
    data = await request.json() 
    
    email = data.get("email")
    password = data.get("password")

    success = authenticate_user(email, password) 
    if success:
        message = data.get("message")
        if save_message(email, message):
            return {"message": "Message saved successfully!", "received": data}
        else:
            return {"message": "Message not saved!"} 
    else:
        return {"message": "Invalid credentials"}

# messages endpoint
@app.post("/messages")
async def messages(requests: Request):
    data = await request.json()
    email = data.get("email")
    password = data.get("password")

    # authentications (1st step)
    if not authenticate_user(email, password):
        return {"message": "Invalid credentials"}
    
    messages = get_all_messages()
    return {"message": "Messages retrieved", "messages": messages}

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