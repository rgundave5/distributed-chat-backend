# START FastAPI SERVER (from FastAPI's first steps)
from fastapi import FastAPI, Request
from logic import add_user, authenticate_user

# create a FastAPI "instance"
app = FastAPI()


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



# to start server run:  uvicorn main:app --reload 
# FastAPI listens at http://127.0.0.1:8000
# send a request using curl command
# FastAPI receives it, runs endpoint, sends JSON back
# {"message": "Server is running!"}

# create client file to test
# make login and signup functions that run direclty - move all yhthe logic from client.py - make its own funct
# learn: python knowledge (freecode camp vids), topics: working w different data types (list, dict, access data, etc)
# try creating multiple clietnt.py and run them separately 