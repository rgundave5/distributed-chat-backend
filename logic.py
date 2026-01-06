# logic.py
# middleman layer
from sqlalchemy import insert, select, ForeignKey, and_
from database import users, engine, conversations, convo_participants, messages
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



# -----------message receiving logic----------------------------------------------------
# if it dne, it will create a dm 
# check if convo exists first, if nto create it
# 1. for any convo of type dircet, fetch all direct convo rows
# 2. for every direct convo row, return any user emails where the convo id of that participants row = convestaions row we are iterating on
# refer to ss
# create or reuse direct convo
# allows next messages to reuse same conversation
##
def get_or_create_direct_conversation(user1, user2):
    # could raise error 
    if (user1 == user2):
        raise ValueError("user 1 and 2 are the same") 
    
    with engine.connect() as conn:
        # find existing direct convo
        query = (
            select(conversations.c.id)
            .select_from(
                conversations.join(
                    convo_participants,
                    conversations.c.id == convo_participants.c.conversation_id
                )
            )
            .where(conversations.c.type == "direct")
            .where(convo_participants.c.user_email.in_([user1, user2]))
            .group_by(conversations.c.id)
            .having(conversations.c.id.count() == 2)
        )

        result = conn.execute(query).fetchone()
        if result:
            return result[0]

        # create new convo
        convo_result = conn.execute(
            insert(conversations).values(type="direct")
        )
        conn.commit()
        convo_id = convo_result.inserted_primary_key[0]

        conn.execute(insert(convo_participants), [
            {"user_email": user1, "conversation_id": convo_id},
            {"user_email": user2, "conversation_id": convo_id},
        ])
        conn.commit()

        return convo_id


# param is array of participants
# gc names are unique, no duplicates
# check 1: is gc_name valid, if string itself is valid, could also check if it exists in the db
# check 2: check if there are at least 3 users (valid array)
def create_group_convo(gc_name, participants_array):
    if (gc_name==None or gc_name=="" or len(participants_array) < 3):
        return None

    try:
        with engine.connect() as conn:
            result = conn.execute(
                # id param can be omitted handled already
                insert("conversations").values(type="group", name=gc_name)
            )
            convo_id = result.inserted_primary_key # gives primary key of result (convo id)
            # update particpants table with new partipants
            for index in participants_array:
                result = conn.execute(
                    insert(convo_participants).values(user_email=index, convo_id=convo_id)
                )
            conn.commit()
            return convo_id
    except Exception as e:
        print("Error receiving group message:", e)
        return None

#----------------------------------------------
# returns messages in convo up to the limit
# OR returns messages after message_id 
def get_message_by_convo_id(convo_id, limit=50, after_message_id):
    # limit variable to avoid spamming
    # message_id var in case user wants 
    try:
        # goal: to be able to get a list of all messages from a specific convo using convo id
        with engine.connect() as conn:
            query = (
                select(messages)
                .where(messages.c.conversation_id == convo_id)
            )
            # if clients wants message AFTER a certain message
            if after_message_id is not None:
                query = query.where(message.c.id > after_message_if)
            # if it's none then just continue with ordering
            query = query.order_by(messages.c.date.asc())

            # limit messages returned
            query = query.limit(limit)
            result = conn.execute(query)

            # Each row is a SQLAlchemy Row object in: result = conn.execute(query)
            # SQL (database rows) --> Python dictionaries
            # row._mapping is a mapping-like object
            # this line converts the row mapping object to a python dict
            # python dict --> fast api --> JSON response
            return [dict(result._mapping) for row in result]

    except Exception as e:
        print("Error retrieving message:", e)
        return None

# -----------message saving logic----------------------------------------------------
# must check if convo exists in the first place
# sender auth, check if sender belongs to convo given by convo id
def save_message(conversation_id, sender, message):
    try:
        with engine.connect() as conn:
            # check if convo exists in db
            conv = conn.execute(
                select(conversations.c.id).where(conversation.c.id == conversation_id)
            ).fetchone()

            if not conv:
                raise Execption("Conversation does not exist")

            # check membership (if sender belongs to convo)
            membership = conn.execute(
                select(convo_participants.c.convo_id)
                .where(
                    # 2 checks: convo id exists and email matches sender's
                    (conversations.c.convo_id == conversation_id) &
                    (conversations.c.user_email == sender)
                )
            ).fetchone()

            if not membership:
                raise Execption("Sender not authorized")

            result = conn.execute(
                insert(messages).values(
                    conversation_id=conversation_id,
                    sender=sender,
                    message=message,
                    date=datetime.utcnow()
                )
            )
            conn.commit()
            # meaning of this line: Return the ID of the row that was just inserted into the db
            # why do we need to return the message id: client needs it for future messages
            return result.inserted_primary_key[0]
    except Exception as e:
        print("Error saving message:", e)
        return None
