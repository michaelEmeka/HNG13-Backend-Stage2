from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import os
import tempfile
import atexit
import ssl
from sqlalchemy import text
import base64


load_dotenv()


# using encoded ssl certification due to line break error in environment variable in deployment environment
DB_SSL_CA_B64 = os.getenv("DB_SSL_CA_B64")
if not DB_SSL_CA_B64:
    raise RuntimeError("Missing DB_SSL_CA_B64")

decoded_ca = base64.b64decode(DB_SSL_CA_B64)

print(decoded_ca)

temp_ca_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
temp_ca_file.write(decoded_ca)
temp_ca_file.flush()
# atexit.register(lambda: os.remove(temp_ca_file.name))

# print(DATABASE_URL)
DATABASE_URL = os.getenv("DATABASE_URL")
# print(os.getenv("DEBUG"))
# DATABASE_URL = ""
# DB_SSL_CA = os.getenv("DB_SSL_CA")

# temp_ca_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pem")
# temp_ca_file.write(DB_SSL_CA.encode("utf-8"))
# temp_ca_file.flush()


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "ssl": 
            {
            "ca": temp_ca_file.name,
            "check_hostname": True,
            "verify_mode": ssl.CERT_REQUIRED
            }  # pass SSL parameters as dict
    },
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
# db = SessionLocal()
# print(db.execute(text("SELECT NOW();")).fetchone())
# db.close()
# db = SessionLocal()
