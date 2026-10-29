"""SQLite outbox: atomic records + cursor; delivery remains at-least-once."""

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def normalize(source, record, namespace="", include_content=False):
    """Metadata allowlist, not a general-purpose content/PII redactor."""
    identifier = str(record.get("id") or record.get("Id") or record.get("conversationtranscriptid")
                     or digest(record))
    data = {key: record[key] for key in (
        "interactionType", "appClass", "riskLevel", "riskState", "riskEventType",
        "identityType", "blueprintId", "agentIdentityBlueprintId", "accountEnabled",
        "servicePrincipalType", "severity", "status", "serviceSource",
        "riskLevelAggregated", "conditionalAccessStatus", "resourceId", "appId",
    ) if key in record and not isinstance(record[key], (dict, list))}
    data["NativeId"] = identifier
    nested = record.get("auditData", {})
    if isinstance(nested, str):
        nested = json.loads(nested)
    if not isinstance(nested, dict):
        raise ValueError("auditData must be an object or JSON object string")
    event = record.get("CopilotEventData") or nested.get("CopilotEventData") or {}
    if event:
        data["AppHost"] = event.get("AppHost")
        data["AccessedResourceCount"] = len(event.get("AccessedResources", []))
        data["MessageCount"] = len(event.get("Messages", []))
    if include_content:
        data["Raw"] = record
    return {
        "TimeGenerated": record.get("createdDateTime") or record.get("CreationTime")
        or record.get("activityDateTime") or record.get("riskLastModifiedDateTime")
        or record.get("createdon") or record.get("Timestamp")
        or datetime.now(timezone.utc).isoformat(),
        "Source": source,
        "RecordId": digest([source, namespace, identifier, digest(record),
                            "raw" if include_content else "metadata"]),
        "Operation": record.get("operation") or record.get("Operation")
        or record.get("activityDisplayName") or record.get("interactionType") or source,
        "ActorId": record.get("userId") or record.get("UserKey") or "",
        "AgentId": record.get("agentId") or record.get("appId")
        or (identifier if source in ("risky-agents", "agent-identities") else ""),
        "CorrelationId": record.get("requestId") or record.get("correlationId")
        or event.get("ThreadId") or "",
        "Data": data,
    }


class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS cursors (
                job TEXT PRIMARY KEY, value TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS delivered (
                destination TEXT, id TEXT, PRIMARY KEY(destination,id));
        """)

    def cursor(self, job):
        row = self.db.execute("SELECT value FROM cursors WHERE job=?", (job,)).fetchone()
        return json.loads(row[0]) if row else None

    def save(self, job, rows, cursor=None):
        with self.db:
            for row in rows:
                # Changed snapshots have different IDs; identical replays are deduplicated.
                self.db.execute("INSERT OR IGNORE INTO events VALUES (?,?)",
                                (row["RecordId"], json.dumps(row, sort_keys=True)))
            if cursor is None:
                self.db.execute("DELETE FROM cursors WHERE job=?", (job,))
            else:
                self.db.execute("INSERT OR REPLACE INTO cursors VALUES (?,?)",
                                (job, json.dumps(cursor)))

    def events(self):
        for row in self.db.execute("SELECT payload FROM events ORDER BY id"):
            yield json.loads(row[0])

    def pending(self, destination):
        for row in self.db.execute("""
            SELECT e.id,e.payload FROM events e LEFT JOIN delivered d
            ON d.destination=? AND d.id=e.id WHERE d.id IS NULL ORDER BY e.id
        """, (destination,)):
            yield row[0], json.loads(row[1])

    def acknowledge(self, destination, ids):
        with self.db:
            self.db.executemany("INSERT OR IGNORE INTO delivered VALUES (?,?)",
                                ((destination, identifier) for identifier in ids))

    def close(self):
        self.db.close()
