from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from fastapi import HTTPException, status
from app.core.config import settings


# Tolerate small clock drift between Google's auth server and our server.
# The google-auth library defaults to 10s, which is tight for Railway/serverless
# environments whose clocks occasionally drift a bit more; 30s is a safe headroom
# without meaningfully weakening the token's freshness guarantees.
_GOOGLE_CLOCK_SKEW = 30


def verify_google_token(token: str) -> dict:
    """
    Verifies a Google ID token and returns the decoded payload.
    Raises an HTTPException (401) on any verification failure with a specific
    reason in the `detail` so frontend can surface useful diagnostics.
    """
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            clock_skew_in_seconds=_GOOGLE_CLOCK_SKEW,
        )

        aud = idinfo.get("aud")
        if aud not in settings.GOOGLE_CLIENT_IDS:
            raise ValueError(
                f"Token audience '{aud}' is not in the allowed client-ID list. "
                "If this is a legitimate client, add its OAuth client ID to "
                "settings.GOOGLE_CLIENT_IDS and redeploy."
            )

        iss = idinfo.get("iss")
        if iss not in ("accounts.google.com", "https://accounts.google.com"):
            raise ValueError(f"Unexpected token issuer: {iss!r}")

        if not idinfo.get("email_verified", False):
            # Google sometimes issues tokens for unverified emails; we refuse
            # them so we never provision an account we can't trust to belong
            # to the Google-identified user.
            raise ValueError("Google account email is not verified.")

        return idinfo

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {e}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        # Network error reaching Google's cert endpoint, transient SSL issues,
        # etc. Return 503 so the frontend shows a retry-able error rather than
        # a login-error red herring.
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Google token verification transient failure: {e}",
        )
