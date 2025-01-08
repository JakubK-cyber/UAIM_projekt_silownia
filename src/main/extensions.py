from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_argon2 import Argon2
from datetime import timedelta
import redis

# Określenie czasu wygaśnięcia tokenów dostępu (1 godzina)
ACCESS_EXPIRES = timedelta(hours=1)

# Inicjalizacja obiektu SQLAlchemy do pracy z bazą danych
db = SQLAlchemy()

# Inicjalizacja obiektu JWTManager do zarządzania tokenami JWT
jwt = JWTManager()

# Inicjalizacja obiektu Argon2 do hashowania haseł
argon2 = Argon2()

# Konfiguracja połączenia z serwerem Redis jako blocklisty JWT
jwt_redis_blocklist = redis.StrictRedis(
    host="redis_server", port=6379, db=0, decode_responses=True
)