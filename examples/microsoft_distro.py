"""Microsoft OpenTelemetry Distro synthetic invocation. Sources: [S1,S2]."""

import argparse
import os
import uuid


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record-synthetic-content", action="store_true")
    parser.add_argument("--agent365", action="store_true")
    args = parser.parse_args()
    if any(value for key, value in os.environ.items() if key.startswith("OTEL_EXPORTER_OTLP")):
        raise SystemExit("Remove ambient OTLP configuration; this demo only approves console or explicit Agent 365 export")
    # Prevent inherited content switches from making the metadata-only demo unsafe.
    os.environ["ENABLE_SENSITIVE_DATA"] = "false"
    os.environ["APPLICATIONINSIGHTS_STATSBEAT_DISABLED_ALL"] = "true"
    os.environ["APPLICATIONINSIGHTS_SDKSTATS_DISABLED"] = "true"
    from microsoft.opentelemetry import use_microsoft_opentelemetry
    from microsoft.opentelemetry.a365.core import (
        AgentDetails, BaggageBuilder, Channel, InvokeAgentScope,
        InvokeAgentScopeDetails, Request, ServiceEndpoint,
    )
    from opentelemetry import trace
    from opentelemetry.sdk.resources import Resource
    tenant = os.environ.get("A365_TENANT_ID", str(uuid.UUID(int=0)))
    agent = os.environ.get("A365_AGENT_ID", str(uuid.UUID(int=1)))
    os.environ["ENABLE_A365_OBSERVABILITY_EXPORTER"] = str(args.agent365).lower()
    config = {"enable_console": True, "enable_a365": True, "enable_azure_monitor": False,
              "enable_sensitive_data": False,
              "a365_enable_observability_exporter": args.agent365,
              "instrumentation_options": {"openai_agents": {"enabled": False}},
              "resource": Resource({"service.name": "synthetic-reference"})}
    if args.agent365:
        token = os.environ.get("A365_OBSERVABILITY_TOKEN")
        if not token or tenant == str(uuid.UUID(int=0)) or agent == str(uuid.UUID(int=1)):
            raise SystemExit("A365 tenant, registered agent ID and observability-scoped token required")
        config.update(a365_enable_observability_exporter=True,
                      a365_use_s2s_endpoint=True, a365_token_resolver=lambda *_: token)
    use_microsoft_opentelemetry(**config)
    request = Request(content="", session_id="synthetic-session", conversation_id="synthetic-conversation",
                      channel=Channel(name="reference-console"))
    details = AgentDetails(agent_id=agent, tenant_id=tenant, agent_name="Synthetic reference agent",
                           agent_description="Synthetic instrumentation demo")
    with BaggageBuilder().tenant_id(tenant).agent_id(agent).build():
        with InvokeAgentScope.start(request=request,
                                    scope_details=InvokeAgentScopeDetails(
                                        endpoint=ServiceEndpoint(hostname="example.invalid", port=443)),
                                    agent_details=details) as scope:
            if args.record_synthetic_content:
                scope.record_input_messages(["Summarize synthetic EXAMPLE-ONLY."])
                scope.record_output_messages(["Synthetic response; no real records accessed."])
    if not trace.get_tracer_provider().force_flush():
        raise RuntimeError("Telemetry flush timed out; destination receipt is not established")
    if args.agent365:
        print("Export requested, not receipt-confirmed. Verify the synthetic span in Agent 365.")


if __name__ == "__main__":
    main()
