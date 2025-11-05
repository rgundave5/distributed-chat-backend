from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

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

# tells SQLAlchemy to create the tables in the database 
metadata.create_all(engine)

# confirmation message
print("Data stored successfully.")