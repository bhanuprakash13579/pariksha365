"""Cashfree Payment Gateway client.

Handles order creation, order status lookup, and webhook signature
verification. All network calls are async (httpx).

Env vars required in Railway:
  CASHFREE_APP_ID         — x-client-id header
  CASHFREE_SECRET_KEY     — x-client-secret header + webhook HMAC key
  CASHFREE_WEBHOOK_SECRET — separate webhook signing secret from dashboard
  CASHFREE_ENV            — "TEST" (default) or "PROD"
"""
from __future__ import annotations

import base64
import hashlib
import hmac

import httpx
from fastapi import HTTPException

from app.core.config import settings

_TEST_BASE = "https://sandbox.cashfree.com/pg"
_PROD_BASE = "https://api.cashfree.com/pg"
_API_VERSION = "2023-08-01"


def _base_url() -> str:
    return _PROD_BASE if settings.CASHFREE_ENV.upper() == "PROD" else _TEST_BASE


def _headers() -> dict:
    return {
        "x-client-id": settings.CASHFREE_APP_ID,
        "x-client-secret": settings.CASHFREE_SECRET_KEY,
        "x-api-version": _API_VERSION,
        "Content-Type": "application/json",
    }


async def create_order(
    *,
    order_id: str,
    amount_inr: float,
    customer_id: str,
    customer_name: str,
    customer_email: str,
    customer_phone: str,
    return_url: str,
    notify_url: str,
) -> dict:
    """Create a Cashfree order and return the full response dict.

    The caller uses ``response["payment_session_id"]`` to build the hosted
    checkout URL. ``order_id`` must be unique per order (≤50 chars,
    alphanumeric + hyphen + underscore).
    """
    payload = {
        "order_id": order_id,
        "order_amount": round(amount_inr, 2),
        "order_currency": "INR",
        "customer_details": {
            "customer_id": customer_id,
            "customer_name": customer_name,
            "customer_email": customer_email,
            "customer_phone": customer_phone,
        },
        "order_meta": {
            "return_url": return_url,
            "notify_url": notify_url,
        },
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.post(
            f"{_base_url()}/orders", json=payload, headers=_headers()
        )
        if resp.status_code not in (200, 201):
            raise HTTPException(
                status_code=502,
                detail=f"Cashfree create_order failed ({resp.status_code}): {resp.text}",
            )
        return resp.json()


async def get_order(order_id: str) -> dict:
    """Fetch current order status from Cashfree (used on return-URL verify)."""
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(
            f"{_base_url()}/orders/{order_id}", headers=_headers()
        )
        if resp.status_code == 404:
            raise HTTPException(status_code=404, detail="Cashfree order not found")
        resp.raise_for_status()
        return resp.json()


def verify_webhook_signature(raw_body: bytes, timestamp: str, received_sig: str) -> bool:
    """Return True if the webhook POST is genuinely from Cashfree.

    Cashfree signature = Base64(HMAC-SHA256(timestamp + rawBody, WEBHOOK_SECRET)).
    """
    secret = settings.CASHFREE_WEBHOOK_SECRET
    if not secret:
        return False
    message = timestamp + raw_body.decode("utf-8")
    expected = base64.b64encode(
        hmac.new(
            secret.encode("utf-8"),
            message.encode("utf-8"),
            hashlib.sha256,
        ).digest()
    ).decode("utf-8")
    return hmac.compare_digest(expected, received_sig)


def checkout_page_url(payment_session_id: str) -> str:
    """Hosted checkout URL the frontend redirects to."""
    if settings.CASHFREE_ENV.upper() == "PROD":
        return f"https://payments.cashfree.com/order/#{payment_session_id}"
    return f"https://payments-test.cashfree.com/order/#{payment_session_id}"
