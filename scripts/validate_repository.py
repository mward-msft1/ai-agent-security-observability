"""Offline structure checks; intentionally not a Kusto compiler or security scanner."""

import ast
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    for folder in ("agent_audit", "examples", "tests", "scripts"):
        for path in (ROOT / folder).rglob("*.py"):
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for folder in ("config", "fixtures", ".config"):
        for path in (ROOT / folder).rglob("*.json"):
            json.loads(path.read_text(encoding="utf-8"))
    direct = set((ROOT / "requirements-sdk.txt").read_text().splitlines())
    locked = set((ROOT / "requirements-sdk.lock").read_text().splitlines())
    require({line for line in direct if line and not line.startswith("#")} <= locked,
            "Direct SDK requirements must match the resolved lock")

    table = json.loads((ROOT / "config/table.json").read_text())["properties"]["schema"]
    dcr = json.loads((ROOT / "config/dcr.json").read_text())["properties"]
    columns = dcr["streamDeclarations"]["Custom-AgentActivity"]["columns"]
    require(columns == table["columns"], "DCR stream columns must match table schema")
    require(dcr["dataFlows"][0]["outputStream"] == "Custom-" + table["name"], "DCR output mismatch")
    sys.path.insert(0, str(ROOT))
    from agent_audit.store import normalize
    for raw in json.loads((ROOT / "fixtures/audit.json").read_text()):
        record = normalize("fixture", raw)
        require(set(record) == {column["name"] for column in columns}, "Normalized fixture keys differ")
        for column in columns:
            expected = dict if column["type"] == "dynamic" else str
            require(isinstance(record[column["name"]], expected), "Normalized column type differs")
        require("Raw" not in record["Data"], "Default fixture must not store full content")

    sources = (ROOT / "docs/sources.md").read_text(encoding="utf-8")
    source_ids = set(re.findall(r"^\| ([A-Z]\d+) \|", sources, re.MULTILINE))
    docs = [*ROOT.glob("*.md"), *(ROOT / "docs").glob("*.md"), *(ROOT / "queries").glob("*.md")]
    queries = list((ROOT / "queries").rglob("*.kql"))
    require(len(queries) >= 12, "Expected query library is incomplete")
    for path in [*docs, *queries]:
        text = path.read_text(encoding="utf-8")
        for group in re.findall(r"\[([A-Z]\d+(?:[-,][A-Z]\d+)*)\]", text):
            for item in group.split(","):
                if "-" in item:
                    first, last = item.split("-")
                    require(first[0] == last[0], "Source ranges must share prefix")
                    ids = [first[0] + str(i) for i in range(int(first[1:]), int(last[1:]) + 1)]
                else:
                    ids = [item]
                require(set(ids) <= source_ids, f"{path.name}: unknown source citation {item}")
        if path.suffix == ".kql":
            require(text.startswith("//") and "|" in text, f"{path.name}: missing query context")
        else:
            for target in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                if target.startswith(("https://", "http://", "#", "mailto:")):
                    continue
                relative = unquote(target.split("#", 1)[0])
                require((path.parent / relative).exists(), f"{path.name}: broken link {target}")

    workflows = list((ROOT / ".github/workflows").glob("*.yml"))
    require(workflows, "Missing GitHub workflows")
    for path in workflows:
        data = yaml.load(path.read_text(), Loader=yaml.BaseLoader)
        require("on" in data and "jobs" in data, f"{path.name}: invalid workflow structure")
        for job in data["jobs"].values():
            require("runs-on" in job and "steps" in job, f"{path.name}: invalid job")
            for step in job["steps"]:
                if "uses" in step:
                    require(re.fullmatch(r"[\w./-]+@[0-9a-f]{40}", step["uses"]),
                            f"{path.name}: action must use immutable SHA")
    pipeline = yaml.safe_load((ROOT / "azure-pipelines.yml").read_text())
    require("steps" in pipeline and "pool" in pipeline, "Invalid Azure Pipeline")
    print(f"Validated Python syntax, JSON/schema, {len(queries)} query shapes, "
          f"{len(source_ids)} source IDs, relative links and {len(workflows)} workflow structures.")
    print("KQL semantic binding, external link availability and live tenant behavior are not checked.")


if __name__ == "__main__":
    main()
