import hashlib
import hmac
import secrets

PASSWORD_ALGORITHM = "pbkdf2_sha256"
PASSWORD_ITERATIONS = 210_000


def hash_password(password: str) -> str:
    """Genera un hash seguro para una contrasena."""
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_ITERATIONS,
    )
    return f"{PASSWORD_ALGORITHM}${PASSWORD_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded_password: str) -> bool:
    """Compara una contrasena con su hash almacenado."""
    try:
        algorithm, iterations, salt, expected_digest = encoded_password.split("$", 3)
        if algorithm != PASSWORD_ALGORITHM:
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt),
            int(iterations),
        )
    except (TypeError, ValueError):
        return False
    return hmac.compare_digest(digest.hex(), expected_digest)


def create_session_token() -> str:
    """Crea un token opaco para una sesion."""
    return secrets.token_urlsafe(32)


def hash_session_token(token: str) -> str:
    """Genera la huella de un token de sesion."""
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
