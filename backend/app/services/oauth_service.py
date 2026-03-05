from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import HTTPException, status
from app.core.config import settings

def verify_google_token(token: str) -> dict:
    """
    Verifies a Google ID token and returns the decoded payload.
    Raises an HTTPException if the token is invalid or the audience doesn't match.
    """
    try:
        # We verify the token. google-auth fetches the public keys automatically.
        # We don't enforce a single audience here initially, but we check if the 
        # decoded audience is in our list of known client IDs for security.
        idinfo = id_token.verify_oauth2_token(
            token, 
            requests.Request()
        )

        if idinfo['aud'] not in settings.GOOGLE_CLIENT_IDS:
            raise ValueError(f"Unrecognized client ID: {idinfo['aud']}")

        # Ensure it's a valid Google account issuer
        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # ID token is valid.
        return idinfo
    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
