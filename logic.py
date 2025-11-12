# middleman layer
from sqlalchemy import insert, select
from database import users, engine

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

        print(f"Success: User {email} added!")
        return True
    except Exception as e:
        print("Error adding user:", e)
        return False

