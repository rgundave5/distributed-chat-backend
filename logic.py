# logic.py
# middleman layer
from sqlalchemy import insert, select
from database import users, engine, messages
from datetime import datetime

# function to add a new user to the users table
def add_user(email, password):
    try:
        # Creates a temporary connection object, called conn
        with engine.connect() as conn:
            # opens connection to db and inserts data into a table (users)
            conn.execute(insert(users).values(email=email, password=password))
            # changes saved (always commit otherwise data will be added but won't save)
            conn.commit()
        print(f"Success: User {email} added!")
        return True
    except Exception as e:
        print("Error adding user:", e)
        return False

# view all users (for testing)
# use to verify data is added
def get_all_users():
    with engine.connect() as conn:
        result = conn.execute(select(users))
        return [dict(row._mapping) for row in result]

# implement /login with authentication
def authenticate_user(email, password):
    try:
        # Creates a temporary connection object, called conn
        with engine.connect() as conn:
            # SQLAlchemy query
            # select all columns from the "users" table but only where `email` column equals the 
            # value received from the client
            # conn.execute runs this query
            # result now equals all the rows that match the query
            result = conn.execute(select(users).where(users.c.email == email))
            # grab first row that matches the query (this row object behaves like a dictionary)
            user = result.fetchone()

            # if no match found (email), return None
            # this checks if what client enters for password matches the password in the db
            if user:
                if user._mapping["password"] == password:
                    print(f"Login successful for user: {email}")
                    return True
                else:
                    print(f"Invalid password for user: {email}")
                    return False
            else:
                print(f"No user found with email: {email}")
                return False

    except Exception as e:
        print("Error authenticating user:", e)
        return False

# -----------message saving logic----------------------------------------------------
def save_direct_message(sender, receiver, message):
    try:
        with engine.connect() as conn:
            result = conn.execute(
                insert(messages).values(
                    sender = sender,
                    receiver = receiver,
                    message = message,
                    date = datetime.now(),
                )
            )
            conn.commit()
            message_id = result.inserted_primary_key[0]
            print(f"DIRECT Saved message {message_id} from {sender} to {receiver}")
            return message_id

    except Exception as e:
        print("Error saving direct message:", e)
        return None


def save_group_message(sender, group_name, message):
    try:
        with engine.connect() as conn:
            result = conn.execute(
                insert(messages).values(
                    sender=sender,
                    receiver=None,
                    group_name=group_name,
                    message=message,
                    date=datetime.now(),
                )
            )
            conn.commit()

            message_id = result.inserted_primary_key[0]
            print(f"GROUP Saved message {message_id} from {sender} in {group_name}")
            return message_id

    except Exception as e:
        print("Error saving group message:", e)
        return None

# -----------message receiving logic----------------------------------------------------
# if it dne, it will create a dm 
# check if convo exists first, if nto create it
# 1. for any convo of type dircet, fetch all direct convo rows
# 2. for every direct convo row, return any user emails where the convo id of that participants row = convestaions row we are iterating on
# refer to ss
def get_or_create_dm(user1, user2):
    try:
        with engine.connect() as conn:
            # update!
            query = select(messages).where((messages.c.dm_id == dm_id)
            )
            result = conn.execute(query)
            return [dict(row._mapping) for row in result]
    except Exception as e:
        print("Error receiving direct message:", e)
        return None

# param is array of participants
def create_group_convo(gc_name, participants_array):
    try:
        with engine.connect() as conn:
            # update!
            query = select(messages).where(messages.c.gc_id == gc_id)
            result = conn.execute(query)
            return [dict(row._mapping) for row in result]
    except Exception as e:
        print("Error receiving group message:", e)
        return None

#----------------------------------------------
def get_message_by_id(message_id):
    # select from messages table where message id matches
    #query = messages.select().where(messages.c.id == message_id)
    # get one row --> if the message exists then result becomes a row object
    #result = engine.execute(query).fetchone()
    # convert the SQL row into a Python dictionary
    #return dict(result) if result else None
    try:
        with engine.connect() as conn:
            query = select(messages).where(messages.c.id == message_id)
            result = conn.execute(query).fetchone()
            return dict(result._mapping) if result else None
    except Exception as e:
        print("Error retrieving message:", e)
        return None