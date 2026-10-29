"""Bounded HTTPS JSON transport. Endpoint evidence: docs/sources.md."""

import email.utils
import json
import logging
import random
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

LOG = logging.getLogger(__name__)


class ApiError(RuntimeError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class Client:
    def __init__(self, token, hosts, opener=None, sleep=time.sleep, attempts=6):
        self.token = token
        self.hosts = frozenset(hosts)
        self.opener = opener or urllib.request.build_opener(NoRedirect())
        self.sleep = sleep
        self.attempts = attempts

    def check_url(self, url):
        parsed = urllib.parse.urlsplit(url)
        if (parsed.scheme != "https" or parsed.hostname not in self.hosts
                or parsed.port not in (None, 443) or parsed.username
                or parsed.password or parsed.fragment):
            raise ValueError("Unapproved HTTPS endpoint; credentials were not sent")

    def request(self, method, url, body=None, headers=None, retry=False):
        self.check_url(url)
        data = None if body is None else json.dumps(body).encode("utf-8")
        for attempt in range(self.attempts):
            request_headers = {"Authorization": f"Bearer {self.token()}",
                               "Accept": "application/json",
                               "Content-Type": "application/json; charset=utf-8"}
            request_headers.update(headers or {})
            req = urllib.request.Request(url, data=data, method=method, headers=request_headers)
            try:
                with self.opener.open(req, timeout=60) as response:
                    payload = response.read(32 * 1024 * 1024 + 1)
                    if len(payload) > 32 * 1024 * 1024:
                        raise ApiError("Response exceeds 32 MiB safety limit; narrow query")
                    return (json.loads(payload) if payload else None,
                            dict(response.headers), response.status)
            except urllib.error.HTTPError as error:
                # Do not log bodies, URLs, query strings, tokens, or interaction data.
                status = error.code
                retry_after = error.headers.get("Retry-After")
                request_id = error.headers.get("request-id", "")
                error.close()
                if not (retry and status in (429, 500, 502, 503, 504)
                        and attempt + 1 < self.attempts):
                    raise ApiError(f"HTTP {status}; request-id={request_id}") from None
                delay = retry_delay(retry_after, attempt)
                LOG.warning("HTTP %s; retry %s in %.1fs", status, attempt + 1, delay)
                self.sleep(delay)
            except (urllib.error.URLError, TimeoutError) as error:
                if not retry or attempt + 1 == self.attempts:
                    raise ApiError("HTTPS transport failed; checkpoint retained") from error
                self.sleep(retry_delay(None, attempt))
        raise ApiError("Retry budget exhausted")


def retry_delay(value, attempt):
    if value:
        try:
            delay = max(0, float(value))
        except ValueError:
            try:
                date = email.utils.parsedate_to_datetime(value)
                delay = max(0, (date - datetime.now(timezone.utc)).total_seconds())
            except (ValueError, TypeError) as error:
                raise ApiError("Invalid Retry-After header") from error
        if delay > 300:
            raise ApiError("Retry-After exceeds 300s; stop and retry later, never early")
        return delay
    return min(60, 2 ** attempt) + random.random()


def token_provider(resource, mode="environment"):
    if mode == "environment":
        import os
        def token():
            value = os.environ.get("ACCESS_TOKEN", "")
            if not value:
                raise ValueError("Set ACCESS_TOKEN for the documented resource; never pass it in arguments")
            return value
        return token
    from azure.identity import AzureCliCredential, WorkloadIdentityCredential
    credential = (AzureCliCredential() if mode == "cli" else WorkloadIdentityCredential())
    return lambda: credential.get_token(f"{resource}/.default").token
