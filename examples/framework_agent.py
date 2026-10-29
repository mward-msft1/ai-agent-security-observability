"""Agent Framework + Azure Monitor. Sources: [S3,S4]. Live model calls are opt-in."""

import argparse
import asyncio
import os


async def run():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--record-synthetic-content", action="store_true")
    args = parser.parse_args()
    if not args.live:
        raise SystemExit("No model invoked; use --live after configuring endpoint, deployment and RBAC.")
    os.environ["ENABLE_SENSITIVE_DATA"] = "false"
    os.environ["OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT"] = "false"
    os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "false"
    from agent_framework.observability import create_resource, enable_sensitive_telemetry
    from agent_framework.openai import OpenAIChatClient
    from azure.identity.aio import AzureCliCredential
    from azure.monitor.opentelemetry import configure_azure_monitor
    from opentelemetry import trace
    connection = os.environ["APPLICATIONINSIGHTS_CONNECTION_STRING"]
    endpoint = os.environ["AZURE_OPENAI_ENDPOINT"]
    deployment = os.environ["AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"]
    configure_azure_monitor(connection_string=connection, resource=create_resource())
    if args.record_synthetic_content:
        enable_sensitive_telemetry()
    async with AzureCliCredential() as credential:
        client = OpenAIChatClient(credential=credential, azure_endpoint=endpoint, model=deployment)
        agent = client.as_agent(name="SyntheticReference",
                                instructions="Only summarize the synthetic input; do not use external tools.")
        result = await agent.run("Summarize: EXAMPLE-ONLY document contains three synthetic items.")
    # Do not log model output in the default path.
    print("Invocation completed; content omitted. Response type:", type(result).__name__)
    if not trace.get_tracer_provider().force_flush():
        raise RuntimeError("Telemetry flush timed out; verify destination health")


if __name__ == "__main__":
    asyncio.run(run())
