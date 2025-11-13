from passlib.context import CryptContext

pwd_context = CryptContext(
            schemes=["argon2", "bcrypt"],
            default="argon2",
            argon2__time_cost=3,
            argon2__memory_cost=65536,
            argon2__parallelism=2,
            bcrypt__rounds=12,
            deprecated="auto"
        )

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)
