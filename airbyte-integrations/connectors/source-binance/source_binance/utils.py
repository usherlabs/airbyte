import hashlib
import hmac
import urllib.parse


def encoded_string(query):
    return urllib.parse.urlencode(query, True).replace("%40", "@")


def get_signature(secret: str, payload: dict = None, ):
    if payload is None:
        payload = {}
    query_string = encoded_string(payload)
    signature = hmac_sha256(secret, query_string)
    return signature


def hmac_sha256(secret_key: str, query_string: str) -> str:
    return hmac.new(secret_key.encode("utf-8"), query_string.encode("utf-8"), hashlib.sha256).hexdigest()
