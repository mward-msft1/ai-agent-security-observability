import os
import unittest


@unittest.skipUnless(os.environ.get("RUN_LIVE_READ_TESTS") == "true",
                     "Live tenant prerequisites absent; explicit RUN_LIVE_READ_TESTS=true required")
class LiveReadTest(unittest.TestCase):
    def test_authorized_directory_audit_page(self):
        from agent_audit.http import Client, token_provider
        mode = os.environ.get("LIVE_AUTH_MODE", "environment")
        self.assertIn(mode, ("environment", "cli", "workload"))
        client = Client(token_provider("https://graph.microsoft.com", mode), ["graph.microsoft.com"])
        result, _, status = client.request(
            "GET", "https://graph.microsoft.com/v1.0/auditLogs/directoryAudits?$top=1", retry=True)
        self.assertEqual(status, 200)
        self.assertTrue(isinstance(result, dict) and isinstance(result.get("value"), list),
                        "Unexpected directory audit response schema; content omitted")
        # Do not log or persist returned live personal data.
