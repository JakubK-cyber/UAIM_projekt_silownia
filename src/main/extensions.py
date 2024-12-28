from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_argon2 import Argon2
from datetime import timedelta
import redis

ACCESS_EXPIRES = timedelta(hours=1)
db = SQLAlchemy()
jwt = JWTManager()
argon2 = Argon2()
jwt_redis_blocklist = redis.StrictRedis(
    host="redis_server", port=6379, db=0, decode_responses=True
)