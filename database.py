# database.py
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, UniqueConstraint
from datetime import datetime
# every backend app needs 1. connection to db, 2. description of what tables exist, 
# 3. command to actually create or initialize those tables

# create database engine, create SQLite database file called chat.db (step 1)
engine = create_engine("sqlite:///chat.db", echo=True)

# metdata for info abt tables, like a container (step 2)
metadata = MetaData()

# users data structure
users = Table(
    "users", metadata,
    Column("id", Integer, primary_key=True), #increments automatically for each promary key
    Column("email", String, unique=True, nullable=False), # must be unique, no two emails can be same
    Column("password", String, nullable=False) 
)

messages = Table(
    "messages", metadata,
    Column("id", Integer, primary_key=True), # id assigned to each message
    Column("conversation_id", ForeignKey("conversations.id"), nullable=False),
    Column("sender", String, nullable=False),
    # this info doesnt matter anymore, stored elsewhere
    # Column("receiver", String, nullable=True),   # direct messages
    # Column("group_name", String, nullable=True), # group messages
    Column("message", String, nullable=False), # actual message - the content
    Column("date", DateTime, nullable=False)
)

# conversations table instead of dm_id and gc_id tables?
conversations = Table(
    "conversations", metadata,
    Column("id", Integer, primary_key=True), # this is referenced in next table
    Column("type", Integer, nullable=False), # direct (1) or group (0)
    Column("name", String, nullable=True) # gc name (not needed for dm, bc name is js receiver)
)

# to verify what convos someone has access to
# returns everyone who exists in a convo (ex: massive gc)
convo_participants = Table(
    "convo_participants", metadata,
    Column("id", Integer, primary_key=True),
    Column("user_email", String, ForeignKey("users.email"), nullable=False),
    
    # foreign key: id here is same as it is in conversations table
    Column("convo_id", Integer, ForeignKey("conversations.id"), nullable=False), # sql doesnt allow arrays cleanly, how to show gc particpants
    # use foreign key: way to use external table key, js refers to the id of another table (more direct connection)
    # refer to diagram for this table "id | user_email | convo_id"
    # in ten gc, my convo id will be diff for each gc
    # unique constraint: constraint that forces two values to not be same, no two users in same convo
    UniqueConstraint("user_email", "convo_id", name="unique_user_convo")   
)

# tells SQLAlchemy to create the tables in the database 
metadata.create_all(engine)

# confirmation message
print("Data stored successfully.")

