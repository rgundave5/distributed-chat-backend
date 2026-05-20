import jwt
from datetime import datetime, timedelta, timezone

# payload: user email, exp date
# never store keys in actual code! move to environmet files - u will lose api keys if not
# BASE VARIABLES FOR AUTH
KEY = "secret"
ALGORITHM = "HS256" # most common, can be changesd
TOKEN_EXPIRY_MINUTES = 60 * 24 * 7 # how to pick this number, if less secrue (one week), more secure (60 sec)

def create_token(email):
    payload = {
        "sub": email, # "", name of the key is literally "email"
        "exp": datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRY_MINUTES) # utc is undefined
        # standard JWT convention is "sub"
        # common syntax, named params
    }
    token = jwt.encode(payload, KEY, ALGORITHM) # correct order
    return token

def verify_token(token):
    try:
        payload = jwt.decode(token, KEY, algorithms=[ALGORITHM])
        email = payload.get("sub") 
        return email  # returns None automatically if "sub" isn't there
    except jwt.ExpiredSignatureError:
        return None  # token expired
    except jwt.InvalidTokenError:
        return None  # signature is wrong or token is fake

# finish this, get verify_token working
# implement these methods in ALL backend (whenever doing auth, use these functs, during signup login, send token
# call verify token to extract user email)
# handle if no email return --> then token is inalid/expired, dont exec funt in that case
# client has to store this token when its sent back thru signup/login, they send it in all requests called bearer
#  (look into bearer auth), make sure u store and send token (look into storing token inn local storage - borswer 
#  db stores things in a tab and can be accessed later)