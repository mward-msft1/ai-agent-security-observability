import importlib.util
import importlib.metadata
import os
import subprocess
import sys
import unittest
from pathlib import Path

SDK_PRESENT = importlib.util.find_spec("agent_framework") is not None


@unittest.skipUnless(SDK_PRESENT, "SDK dependencies absent; install requirements-sdk.lock for offline SDK checks")
class SdkSmokeTest(unittest.TestCase):
    def test_direct_package_versions_match_tested_pins(self):
        manifest = Path(__file__).resolve().parents[1] / "requirements-sdk.txt"
        for line in manifest.read_text().splitlines():
            if line and not line.startswith("#"):
                name, version = line.split("==")
                self.assertEqual(importlib.metadata.version(name), version, name)

    def run_demo(self, content=False):
        script = """
import runpy, socket, sys
from unittest.mock import patch
sys.argv = ["microsoft_distro"] + (["--record-synthetic-content"] if CONTENT else [])
with patch.object(socket.socket, "connect", side_effect=AssertionError("network forbidden")) as connection:
    runpy.run_module("examples.microsoft_distro", run_name="__main__")
    connection.assert_not_called()
""".replace("CONTENT", repr(content))
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(("OTEL_EXPORTER_OTLP", "A365_"))}
        result = subprocess.run([sys.executable, "-c", script], capture_output=True, text=True,
                                timeout=45, env=env, check=True)
        return result.stdout

    def test_metadata_only_span_without_network(self):
        output = self.run_demo()
        self.assertIn("invoke_agent Synthetic reference agent", output)
        self.assertNotIn("Summarize synthetic EXAMPLE-ONLY.", output)
        self.assertNotIn("Synthetic response;", output)
        self.assertNotIn("Failed to set up", output)

    def test_opt_in_content_span_without_network(self):
        output = self.run_demo(True)
        self.assertIn("Summarize synthetic EXAMPLE-ONLY.", output)
        self.assertIn("Synthetic response;", output)

    def test_framework_symbols_and_construction_without_network(self):
        from agent_framework.observability import create_resource, enable_sensitive_telemetry
        from agent_framework.openai import OpenAIChatClient
        self.assertTrue(callable(create_resource))
        self.assertTrue(callable(enable_sensitive_telemetry))
        client = OpenAIChatClient(model="synthetic", api_key="synthetic-not-a-secret",
                                  base_url="https://example.invalid")
        agent = client.as_agent(name="SyntheticReference", instructions="Synthetic only")
        self.assertTrue(callable(agent.run))
