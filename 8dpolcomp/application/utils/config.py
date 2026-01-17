
import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "DEV")
DB_ENV = os.getenv("DB_ENV", "DEV")  # DEV // SSH // PROD


""" ===== GLOBALS ===== """

SQLALCHEMY_POOL_RECYCLE = os.getenv("SQLALCHEMY_POOL_RECYCLE")
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "false").lower() == "true"

HCAPTCHA_VERIFY_URL = os.getenv("HCAPTCHA_VERIFY_URL")
HCAPTCHA_SITE_KEY = os.getenv("HCAPTCHA_SITE_KEY")
HCAPTCHA_SECRET_KEY = os.getenv("HCAPTCHA_SECRET_KEY")

# Relative directory
if ENVIRONMENT == "DEV":
    import sys
    REL_DIR = f"{sys.path[0]}"
else:
    REL_DIR = os.getenv("REL_DIR_PROD")


""" ===== DATABASE CONNECTION ===== """



# Connect to local db
if DB_ENV == "DEV":
    DB_USER = os.getenv("DB_USER_DEV")
    DB_PASS = os.getenv("DB_PASS_DEV")
    DB_NAME = os.getenv("DB_NAME_DEV")
    DB_HOST = os.getenv("DB_HOST_DEV")
    DB_PORT = os.getenv("DB_PORT_DEV")
    
# Connect to prod db via ssh
elif DB_ENV == "SSH":
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME_DEV")
    DB_HOST = os.getenv("DB_HOST_DEV")
    DB_PORT = os.getenv("DB_PORT_DEV")

# Connect to prod db directly
elif DB_ENV == "PROD":
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_NAME = os.getenv("DB_NAME")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    
SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
