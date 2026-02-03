# logic.py
# middleman layer
from sqlalchemy import insert, select, ForeignKey, and_
from database import users, engine, conversations, convo_participants, messages
from datetime import datetime

# -----------------------------------------------------------------------------------
# USERS
# -----------------------------------------------------------------------------------
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

def user_exists(email):
    try:
        with engine.connect() as conn:
            result = conn.execute(
                select(users.c.email).where(users.c.email == email)
            ).fetchone()

            return result is not None
    except Exception as e:
        print("Error checking if user exists:", e)
        return False

# -----------------------------------------------------------------------------------
# CONVERSATIONS
# -----------------------------------------------------------------------------------
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
        conversation_id = convo_result.inserted_primary_key[0]

        conn.execute(insert(convo_participants), [
            {"user_email": user1, "conversation_id": conversation_id},
            {"user_email": user2, "conversation_id": conversation_id},
        ])
        conn.commit()

        return conversation_id


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
                insert(conversations).values(type="group", name=gc_name)
            )
            conversation_id = result.inserted_primary_key[0] # gives primary key of result (convo id)
            # update particpants table with new partipants
            for index in participants_array:
                result = conn.execute(
                    insert(convo_participants).values(user_email=index, conversation_id=conversation_id)
                )
            conn.commit()
            return conversation_id
    except Exception as e:
        print("Error receiving group message:", e)
        return None
# why keep it separate: we canr create the same dm again, reuse the chat
# u can create the same groupchat w the same ppl without resusing the old one (itll create a new one)
# discord ex: diff chats w same ppl for different reasons (discuss diff topics for ex)

# -----------------------------------------------------------------------------------
# MESSAGES
# -----------------------------------------------------------------------------------
# returns messages in convo up to the limit
# OR returns messages after message_id 
def get_message_by_convo_id(conversation_id, after_message_id=None, limit=50):
    # limit variable to avoid spamming
    # message_id var in case user wants 
    try:
        # goal: to be able to get a list of all messages from a specific convo using convo id
        with engine.connect() as conn:
            query = (
                select(messages)
                .where(messages.c.conversation_id == conversation_id)
            )
            # if clients wants message AFTER a certain message
            if after_message_id is not None:
                query = query.where(messages.c.id > after_message_id)
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

# must check if convo exists in the first place
# sender auth, check if sender belongs to convo given by convo id
def save_message(conversation_id, sender, message):
    try:
        with engine.connect() as conn:
            # check if convo exists in db
            conv = conn.execute(
                select(conversations.c.id).where(conversations.c.id == conversation_id)
            ).fetchone()

            if not conv:
                raise Exception("Conversation does not exist")

            # check membership (if sender belongs to convo)
            membership = conn.execute(
                select(convo_participants.c.conversation_id)
                .where(
                    # 2 checks: convo id exists and email matches sender's
                    (conversations.c.conversation_id == conversation_id) &
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


def delete_conversation(convo_id, requester_email):
    try:
        with engine.connect() as conn:
            # 1. Check convo exists
            convo = conn.execute(
                select(conversations.c.id)
                .where(conversations.c.id == convo_id)
            ).fetchone()

            if not convo:
                return False  #convo doesn't exist

            # 2. Check tht the requester is a participant
            membership = conn.execute(
                select(convo_participants.c.id)
                .where(
                    (convo_participants.c.convo_id == convo_id) &
                    (convo_participants.c.user_email == requester_email)
                )
            ).fetchone()

            if not membership:
                return False  #not authorized

            # 3. Delete messages
            conn.execute(
                delete(messages)
                .where(messages.c.conversation_id == convo_id)
            )

            # 4. Delete participants
            conn.execute(
                delete(convo_participants)
                .where(convo_participants.c.convo_id == convo_id)
            )

            # 5. Delete conversation
            conn.execute(
                delete(conversations)
                .where(conversations.c.id == convo_id)
            )

            conn.commit()
            return True

    except Exception as e:
        print("Error deleting conversation:", e)
        return False

# 1/29
# incorporate: list all users in a specific convo
# all convos listed under a user
# table join: joins conversations table w convo participants table, to check which convo ids are under that user
# takes the rows from two tabbles and shuffles them tg
# based on a related column btwn them
# cam be based on ForeignKey relationships too!
# benefit: one query --> utilizes shared column to link both tables tg, able to see more info w given input
# how it will work for this funct: two tables (convo and convo particips tables), join on convo id (shared column)
# if the user email = convo particip's email
# WHY? goal is to return type of convo and the name + convo id user is in, we need all that info --> need both tables
def list_user_conversations (email, password):
try:
    with engine.connect() as conn:
        convo = conn.execute(
            # select where the convo ids match in both tables
            select(convo_participants, conversations)
            .join(convo_participants, conversations.c.id==
            convo_participants.c.convo_id)
            .where(email==convo_participants.c.user_email) # convo_particups is still main table, not interchangable
        ).fetchall()    
        
        # temporary grouping structure
        convos = {}

        for row in rows:
            convo_id = row.conversations.id
            # if that id hasnt been seen before create the convo
            if convo_id not in convos:
                convos[convo_id] = {
                    "conversation_id": convo_id,
                    "type": row.conversations.type,
                    "name": row.conversations.name,
                    "participants": []
                }

            convos[convo_id]["participants"].append(
                row.convo_participants.user_email
            )

        # convert dict into the final respons
        results = []

        for convo in convos.values():
            if convo["type"] == "direct":
                # find the other user
                other_user = [
                    # keep only email thats not me
                    p for p in convo["participants"] if p != email
                ][0]

                results.append({
                    "conversation_id": convo["conversation_id"],
                    "type": "direct",
                    "user": other_user
                })
            else:
                results.append({
                    "conversation_id": convo["conversation_id"],
                    "type": "group",
                    "name": convo["name"],
                    "participants": convo["participants"]
                })

        return results

except Exception as e:
    print("Error retrieving all conversations:", e)
    return False

# hw 1/29: iterate thru all convo rows returned, get various info: id, type, name (bc joined w convo table)
# members, --> do a check: if direct, then only one other particip that isnt our user, if group: 
# participants table: return the participants that are in the selected fields, if 2 particips then we know 
# its direct, if more then we know it's group
# hw 1/29: finish the get all convos endpoint, run client and debug everything, do more testing in client.py
# to see if all endpoints are working, 
# send email to alex before next meeting! 