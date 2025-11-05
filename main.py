# START FastAPI SERVER (from FastAPI's first steps)
from fastapi import FastAPI, Request
from logic import add_user

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
@app.post("/login")
# this line defines the path operation function
# it's called by FastAPI whenever it receives a request to URL "/" using a POST operation
# async def or just def can be used
async def login(request: Request):
    data = await request.json() 
    print("Login data received", data) 
    # return the data
    return {"message": "Login endpoint works.", "received": data} 

# testing??
# to start server run:  uvicorn main:app --reload 
# FastAPI listens at http://127.0.0.1:8000
# send a request using curl command
# FastAPI receives it, runs endpoint, sends JSON back
# {"message": "Server is running!"}


