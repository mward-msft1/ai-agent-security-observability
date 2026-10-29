import io
import json
import tempfile
import unittest
import urllib.error
from unittest.mock import MagicMock
from datetime import datetime, timezone
from pathlib import Path

from agent_audit import collect, export
from agent_audit.http import ApiError, Client, retry_delay
from agent_audit.purview import PolicyBlocked, probe
from agent_audit.store import Store, normalize


class FakeClient:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.calls = []

    def check_url(self, url):
        Client(lambda: "fake", ["graph.microsoft.com", "manage.office.com"]).check_url(url)

    def request(self, method, url, body=None, headers=None, retry=False):
        self.calls.append((method, url, body, headers, retry))
        value = next(self.replies)
        if isinstance(value, Exception):
            raise value
        return value if isinstance(value, tuple) else (value, {}, 200)


class StoreTest(unittest.TestCase):
    def setUp(self):
        self.folder = tempfile.TemporaryDirectory()
        self.store = Store(Path(self.folder.name) / "state.sqlite")

    def tearDown(self):
        self.store.close()
        self.folder.cleanup()

    def test_metadata_drops_all_content_containers(self):
        row = normalize("x", {"id": "1", "body": {"content": "SECRET"},
                            "attachments": [{"content": "SECRET"}], "content": "SECRET"})
        self.assertNotIn("SECRET", json.dumps(row))

    def test_content_is_explicit(self):
        self.assertIn("Raw", normalize("x", {"body": "synthetic"}, include_content=True)["Data"])

    def test_replay_dedup_and_changed_snapshot(self):
        a = normalize("risk", {"id": "1", "riskLevel": "low"})
        b = normalize("risk", {"id": "1", "riskLevel": "high"})
        self.store.save("j", [a, a, b])
        self.assertEqual(len(list(self.store.events())), 2)

    def test_content_projection_has_independent_delivery_receipt(self):
        raw = {"id": "1", "body": "synthetic-only"}
        metadata = normalize("x", raw)
        content = normalize("x", raw, include_content=True)
        self.store.save("metadata", [metadata])
        self.store.acknowledge("sink", [metadata["RecordId"]])
        self.store.save("content", [content])
        pending = list(self.store.pending("sink"))
        self.assertEqual([identifier for identifier, _ in pending], [content["RecordId"]])
        self.assertNotEqual(metadata["RecordId"], content["RecordId"])

    def test_replay_does_not_mutate_acknowledged_payload(self):
        row = normalize("x", {"id": "1"})
        self.store.save("j", [row])
        replay = {**row, "TimeGenerated": "2099-01-01T00:00:00Z"}
        self.store.save("j", [replay])
        self.assertEqual(list(self.store.events())[0]["TimeGenerated"], row["TimeGenerated"])

    def test_pagination_resume_and_replay(self):
        url = "https://graph.microsoft.com/v1.0/security/alerts_v2"
        nxt = url + "?next=1"
        first = FakeClient([{"value": [{"id": "1"}], "@odata.nextLink": nxt}, ApiError("failed")])
        with self.assertRaises(ApiError):
            collect.pages(first, self.store, url, "alerts")
        resumed = FakeClient([{"value": [{"id": "2"}]}])
        collect.pages(resumed, self.store, url, "alerts")
        self.assertEqual(resumed.calls[0][1], nxt)
        collect.pages(FakeClient([{"value": [{"id": "1"}, {"id": "2"}]}]),
                      self.store, url, "alerts")
        self.assertEqual(len(list(self.store.events())), 2)

    def test_pagination_rejects_bad_schema_without_commit(self):
        with self.assertRaises(ValueError):
            collect.pages(FakeClient([{}]), self.store, "https://graph.microsoft.com/v1.0/x", "x")
        self.assertEqual(list(self.store.events()), [])

    def test_pagination_rejects_foreign_nextlink(self):
        with self.assertRaises(ValueError):
            collect.pages(FakeClient([{"value": [], "@odata.nextLink": "https://evil.invalid"}]),
                          self.store, "https://graph.microsoft.com/v1.0/x", "x")

    def test_audit_poll_and_records(self):
        client = FakeClient([{"id": "q"}, {"status": "running"}, {"status": "succeeded"},
                             {"value": [{"id": "r", "auditData": {"Operation": "CopilotInteraction"}}]}])
        collect.audit_search(client, self.store, "2026-10-27T00:00:00Z",
                             "2026-10-28T00:00:00Z", sleep=lambda _: None)
        self.assertEqual(len(list(self.store.events())), 1)

    def test_audit_resume_after_timeout(self):
        start, end = "2026-10-27T00:00:00Z", "2026-10-28T00:00:00Z"
        with self.assertRaises(TimeoutError):
            collect.audit_search(FakeClient([{"id": "q"}, {"status": "running"}]),
                                 self.store, start, end, max_polls=1, sleep=lambda _: None)
        client = FakeClient([{"status": "succeeded"}, {"value": []}])
        collect.audit_search(client, self.store, start, end)
        self.assertEqual(client.calls[0][0], "GET")

    def test_audit_failure_is_not_empty_success(self):
        with self.assertRaises(RuntimeError):
            collect.audit_search(FakeClient([{"id": "q"}, {"status": "failed"}]), self.store,
                                 "2026-10-27T00:00:00Z", "2026-10-28T00:00:00Z")

    def test_management_nextpage_and_blobs(self):
        root = "https://manage.office.com"
        client = FakeClient([
            ([{"contentUri": root + "/blob1"}], {"NextPageUri": root + "/next"}, 200),
            [{"Id": "1"}], [{"contentUri": root + "/blob2"}], [{"Id": "2"}]])
        collect.management(client, self.store, "tenant", "2026-10-27T00:00:00Z",
                           "2026-10-28T00:00:00Z",
                           now=datetime(2026, 10, 28, tzinfo=timezone.utc))
        self.assertEqual(len(list(self.store.events())), 2)

    def test_management_rejects_oversize_window(self):
        with self.assertRaises(ValueError):
            collect.management(FakeClient([]), self.store, "t", "2026-10-20T00:00:00Z",
                               "2026-10-28T00:00:00Z")

    def test_export_ack_and_dedup(self):
        self.store.save("x", [normalize("x", {"id": "1"})])
        client = FakeClient([(None, {}, 204)])
        url = "https://graph.microsoft.com/synthetic-sink"
        export.send(self.store, client, url)
        export.send(self.store, client, url)
        self.assertEqual(len(client.calls), 1)
        self.assertIn("Idempotency-Key", client.calls[0][3])

    def test_export_failure_not_acknowledged(self):
        self.store.save("x", [normalize("x", {"id": "1"})])
        with self.assertRaises(ApiError):
            export.send(self.store, FakeClient([ApiError("failed")]),
                        "https://graph.microsoft.com/synthetic-sink")
        self.assertEqual(len(list(self.store.pending("not-a-real-destination"))), 1)

    def test_export_202_not_acknowledged(self):
        self.store.save("x", [normalize("x", {"id": "1"})])
        with self.assertRaises(RuntimeError):
            export.send(self.store, FakeClient([(None, {}, 202)]),
                        "https://graph.microsoft.com/synthetic-sink")

    def test_splunk_application_error(self):
        self.store.save("x", [normalize("x", {"id": "1"})])
        with self.assertRaises(RuntimeError):
            export.send(self.store, FakeClient([{"code": 6}]),
                        "https://graph.microsoft.com/synthetic-sink", "splunk")

    def test_jsonl_roundtrip(self):
        self.store.save("x", [normalize("x", {"id": "1"})])
        path = Path(self.folder.name) / "out.jsonl"
        export.jsonl(self.store, path)
        self.assertEqual(json.loads(path.read_text())["Source"], "x")


class HttpTest(unittest.TestCase):
    def test_authentication_header_uses_current_token(self):
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = b'{"value":[]}'
        response.headers = {}
        response.status = 200
        opener = MagicMock()
        opener.open.return_value = response
        client = Client(lambda: "synthetic-token-not-valid", ["graph.microsoft.com"], opener=opener)
        client.request("GET", "https://graph.microsoft.com/v1.0/auditLogs/directoryAudits")
        request = opener.open.call_args.args[0]
        self.assertEqual(request.get_header("Authorization"), "Bearer " + "synthetic-token-not-valid")

    def test_endpoint_allowlist(self):
        client = Client(lambda: "never-sent", ["graph.microsoft.com"])
        for url in ("http://graph.microsoft.com", "https://evil.invalid",
                    "https://graph.microsoft.com@evil.invalid", "https://graph.microsoft.com:8443",
                    "https://user@graph.microsoft.com", "https://graph.microsoft.com/#fragment"):
            with self.assertRaises(ValueError):
                client.check_url(url)

    def test_retry_after(self):
        self.assertEqual(retry_delay("3", 1), 3)
        self.assertEqual(retry_delay("Wed, 21 Oct 2015 07:28:00 GMT", 1), 0)
        with self.assertRaises(ApiError):
            retry_delay("900", 1)

    def test_throttle_then_success(self):
        class Response(io.BytesIO):
            status = 200
            headers = {}
        class Opener:
            count = 0
            def open(self, request, timeout):
                self.count += 1
                if self.count == 1:
                    raise urllib.error.HTTPError(request.full_url, 429, "throttle",
                                                 {"Retry-After": "0"}, None)
                return Response(b'{"value":[]}')
        client = Client(lambda: "synthetic", ["graph.microsoft.com"],
                        opener=Opener(), sleep=lambda _: None)
        self.assertEqual(client.request("GET", "https://graph.microsoft.com", retry=True)[0], {"value": []})

    def test_post_not_retried_by_default(self):
        class Opener:
            def open(self, request, timeout):
                raise urllib.error.HTTPError(request.full_url, 503, "failed", {}, None)
        with self.assertRaises(ApiError):
            Client(lambda: "x", ["graph.microsoft.com"], opener=Opener()).request(
                "POST", "https://graph.microsoft.com", {})

    def test_preview_explicit(self):
        with self.assertRaises(ValueError):
            collect.graph_url("risky-agents", "2026-10-27T00:00:00Z", "2026-10-28T00:00:00Z")

    def test_invalid_window(self):
        with self.assertRaises(ValueError):
            collect.window("2026-10-28", "2026-10-27")


class PurviewTest(unittest.TestCase):
    def evaluate(self, replies):
        return probe(FakeClient(replies), "user", "app", "uploadText", "synthetic", "thread", 0)

    def scope(self, mode="evaluateInline", actions=None):
        return ({"value": [{"activities": "uploadText", "executionMode": mode,
                             "policyActions": actions or []}]}, {"ETag": '"synthetic"'}, 200)

    def test_inline_allow(self):
        self.assertEqual(self.evaluate([self.scope(), {
            "protectionScopeState": "notModified", "policyActions": [], "processingErrors": []}]),
            "evaluated-inline-no-actions")

    def test_inline_block(self):
        with self.assertRaises(PolicyBlocked):
            self.evaluate([self.scope(), {"protectionScopeState": "notModified",
                "policyActions": [{"action": "restrictAccess", "restrictionAction": "block"}],
                "processingErrors": []}])

    def test_no_scope_sends_no_content(self):
        client = FakeClient([{"value": []}, (None, {}, 201)])
        probe(client, "u", "a", "uploadText", "DO-NOT-SEND", "thread", 0)
        self.assertNotIn("DO-NOT-SEND", json.dumps(client.calls))

    def test_inline_202_fails_closed(self):
        with self.assertRaises(PolicyBlocked):
            self.evaluate([self.scope(), (None, {}, 202)])

    def test_offline_is_not_an_enforcement_verdict(self):
        self.assertIn("not-an-enforcement", self.evaluate([
            self.scope("evaluateOffline"), (None, {}, 202)]))

    def test_processing_error_fails_closed(self):
        with self.assertRaises(PolicyBlocked):
            self.evaluate([self.scope(), {"processingErrors": [{"code": "error"}], "policyActions": []}])

    def test_unknown_action_fails_closed(self):
        with self.assertRaises(PolicyBlocked):
            self.evaluate([self.scope(), {"processingErrors": [],
                "policyActions": [{"action": "futureAction"}], "protectionScopeState": "notModified"}])

    def test_modified_policy_recomputed(self):
        result = self.evaluate([self.scope(), {"processingErrors": [], "policyActions": [],
            "protectionScopeState": "modified"}, self.scope(), {"processingErrors": [],
            "policyActions": [], "protectionScopeState": "notModified"}])
        self.assertEqual(result, "evaluated-inline-no-actions")


if __name__ == "__main__":
    unittest.main()
