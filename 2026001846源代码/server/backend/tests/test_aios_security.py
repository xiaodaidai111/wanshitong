import json
import sys
import tempfile
import unittest
import asyncio
from pathlib import Path

import jwt
from flask import Flask

BACKEND_DIR = Path(__file__).resolve().parents[1]
SERVER_DIR = BACKEND_DIR.parent
for path in (BACKEND_DIR, SERVER_DIR):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import security
from routes import monitor, yixiu
from utils import Config


def token(user_id="u-1", role="operator"):
    return jwt.encode({"user_id": user_id, "role": role}, Config.JWT_SECRET_KEY, algorithm="HS256")


class AiosSecurityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        temp_dir = Path(self.tmp.name)
        self.old_yixiu_db = yixiu.DB_PATH
        self.old_security_db = security.SECURITY_DB_PATH
        yixiu.DB_PATH = temp_dir / "yixiu.db"
        security.SECURITY_DB_PATH = temp_dir / "security.db"

        app = Flask(__name__)
        app.register_blueprint(yixiu.yixiu_bp, url_prefix="/api/yixiu")
        app.register_blueprint(monitor.monitor_bp)
        self.client = app.test_client()

    def tearDown(self):
        yixiu.DB_PATH = self.old_yixiu_db
        security.SECURITY_DB_PATH = self.old_security_db
        self.tmp.cleanup()

    def auth_headers(self, role="operator", idem=None):
        headers = {"Authorization": f"Bearer {token(role=role)}"}
        if idem:
            headers["Idempotency-Key"] = idem
        return headers

    def test_aios_status_requires_jwt(self):
        res = self.client.get("/api/yixiu/aios/status")
        self.assertEqual(res.status_code, 401)

    def test_aios_execute_requires_confirmation_and_idempotency(self):
        res = self.client.post(
            "/api/yixiu/aios/execute",
            json={"goal": "inspect motor"},
            headers=self.auth_headers(),
        )
        self.assertEqual(res.status_code, 409)
        self.assertIn("confirmed", res.get_json()["message"])

        res = self.client.post(
            "/api/yixiu/aios/execute",
            json={"goal": "inspect motor", "confirmed": True},
            headers=self.auth_headers(),
        )
        self.assertEqual(res.status_code, 400)
        self.assertIn("Idempotency-Key", res.get_json()["message"])

    def test_aios_execute_replays_same_idempotency_key(self):
        payload = {"goal": "inspect motor", "confirmed": True, "commit": False}
        headers = self.auth_headers(idem="idem-aios-1")

        first = self.client.post("/api/yixiu/aios/execute", json=payload, headers=headers)
        second = self.client.post("/api/yixiu/aios/execute", json=payload, headers=headers)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.get_json()["data"]["run_id"], second.get_json()["data"]["run_id"])

    def test_aios_execute_rejects_idempotency_conflict(self):
        headers = self.auth_headers(idem="idem-aios-conflict")
        first = self.client.post(
            "/api/yixiu/aios/execute",
            json={"goal": "inspect motor", "confirmed": True, "commit": False},
            headers=headers,
        )
        second = self.client.post(
            "/api/yixiu/aios/execute",
            json={"goal": "inspect pump", "confirmed": True, "commit": False},
            headers=headers,
        )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 409)

    def test_monitor_execute_is_disabled_after_admin_auth(self):
        res = self.client.post(
            "/monitor/execute",
            json={"code": "print(1)"},
            headers=self.auth_headers(role="admin"),
        )
        self.assertEqual(res.status_code, 410)
        self.assertEqual(res.get_json()["message"], "monitor code execution is disabled")

    def test_security_audit_records_denied_write(self):
        self.client.post(
            "/api/yixiu/aios/execute",
            json={"goal": "inspect motor"},
            headers=self.auth_headers(),
        )
        with security._security_db() as conn:
            rows = conn.execute("SELECT action, status FROM security_audit_events").fetchall()
        self.assertTrue(any(row["action"] == "aios.execute" and row["status"] == "denied" for row in rows))

    def test_aios_plan_contains_state_machine_and_agent_contracts(self):
        res = self.client.post(
            "/api/yixiu/aios/plan",
            json={"goal": "inspect motor"},
            headers=self.auth_headers(role="auditor"),
        )

        self.assertEqual(res.status_code, 200)
        plan = res.get_json()["data"]
        self.assertIn("state_machine", plan)
        self.assertIn("depends_on", plan["state_machine"]["supports"])
        first_agent = plan["steps"][0]["agent"]
        self.assertIn("prompt", first_agent)
        self.assertIn("tool_allowlist", first_agent)
        self.assertIn("output_schema", first_agent)

    def test_aios_state_machine_blocks_unapproved_write_step(self):
        plan_res = self.client.post(
            "/api/yixiu/aios/plan",
            json={"goal": "inspect motor"},
            headers=self.auth_headers(role="auditor"),
        )
        plan = plan_res.get_json()["data"]
        plan["steps"][0]["state"] = "done"

        res = self.client.post(
            "/api/yixiu/aios/execute",
            json={"plan": plan, "step_key": "operate", "confirmed": True, "commit": False},
            headers=self.auth_headers(idem="idem-approval-block"),
        )

        self.assertEqual(res.status_code, 409)

    def test_aios_execute_all_stops_when_write_step_needs_approval(self):
        res = self.client.post(
            "/api/yixiu/aios/execute",
            json={"goal": "inspect motor", "execute_all": True, "confirmed": True, "commit": False},
            headers=self.auth_headers(idem="idem-execute-all-blocked"),
        )

        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertLess(data["progress"], 100)
        self.assertTrue(any(item["state"] == "waiting_approval" for item in data["next_steps"]))

    def test_aios_execute_all_completes_with_approve_all(self):
        res = self.client.post(
            "/api/yixiu/aios/execute",
            json={"goal": "inspect motor", "execute_all": True, "approve_all": True, "confirmed": True, "commit": False},
            headers=self.auth_headers(idem="idem-execute-all-approved"),
        )

        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        self.assertEqual(data["progress"], 100)
        self.assertEqual(data["status"], "completed")
        self.assertIn("finalize", data["artifacts"])

    def test_aios_state_transition_can_pause_approve_and_compensate(self):
        plan_res = self.client.post(
            "/api/yixiu/aios/plan",
            json={"goal": "inspect motor"},
            headers=self.auth_headers(role="auditor"),
        )
        plan = plan_res.get_json()["data"]

        pause = self.client.post(
            "/api/yixiu/aios/execute",
            json={"plan": plan, "step_key": "retrieve", "event": "pause", "confirmed": True, "commit": False},
            headers=self.auth_headers(idem="idem-pause"),
        )
        self.assertEqual(pause.status_code, 200)
        self.assertEqual(pause.get_json()["data"]["node"]["state"], "paused")

        compensate = self.client.post(
            "/api/yixiu/aios/execute",
            json={"plan": pause.get_json()["data"]["plan"], "step_key": "retrieve", "event": "compensate", "confirmed": True, "commit": False},
            headers=self.auth_headers(idem="idem-compensate"),
        )
        self.assertEqual(compensate.status_code, 200)
        self.assertEqual(compensate.get_json()["data"]["node"]["state"], "compensated")

    def test_aios_failure_recovery_retries_then_fails(self):
        plan_res = self.client.post(
            "/api/yixiu/aios/plan",
            json={"goal": "inspect motor"},
            headers=self.auth_headers(role="auditor"),
        )
        plan = plan_res.get_json()["data"]
        plan["steps"][0]["max_retries"] = 1

        first_fail = self.client.post(
            "/api/yixiu/aios/execute",
            json={"plan": plan, "step_key": "sense", "event": "fail", "error": "temporary outage", "confirmed": True, "commit": False},
            headers=self.auth_headers(idem="idem-fail-1"),
        )
        self.assertEqual(first_fail.status_code, 200)
        self.assertEqual(first_fail.get_json()["data"]["node"]["state"], "retrying")

        second_fail = self.client.post(
            "/api/yixiu/aios/execute",
            json={"plan": first_fail.get_json()["data"]["plan"], "step_key": "sense", "event": "fail", "error": "still down", "confirmed": True, "commit": False},
            headers=self.auth_headers(idem="idem-fail-2"),
        )
        self.assertEqual(second_fail.status_code, 200)
        self.assertEqual(second_fail.get_json()["data"]["node"]["state"], "failed")

    def test_overview_contacts_and_tasks_mark_fallback_sources(self):
        overview = self.client.get("/api/yixiu/overview").get_json()["data"]
        contacts = self.client.get("/api/yixiu/contacts").get_json()["data"]
        tasks = self.client.get("/api/yixiu/tasks").get_json()["data"]

        self.assertIn("data_sources", overview)
        self.assertIn("equipment", overview["data_sources"])
        self.assertTrue(contacts["data_source"]["is_fallback"])
        self.assertIn("data_source", tasks)
        self.assertTrue(all("is_fallback" in item for item in contacts["contacts"]))

    def test_task_memory_requires_auth_then_persists(self):
        denied = self.client.post("/api/yixiu/tasks/t-1/memory", json={"key": "risk", "value": "hot"})
        self.assertEqual(denied.status_code, 401)

        saved = self.client.post(
            "/api/yixiu/tasks/t-1/memory",
            json={"key": "risk", "value": "hot", "confirmed": True},
            headers=self.auth_headers(idem="idem-memory"),
        )
        self.assertEqual(saved.status_code, 200)

        loaded = self.client.get("/api/yixiu/tasks/t-1/memory")
        self.assertEqual(loaded.status_code, 200)
        self.assertEqual(loaded.get_json()["data"]["memory"][0]["memory_key"], "risk")

    def test_conversation_history_requires_auth_then_persists(self):
        denied = self.client.post("/api/yixiu/conversations/c-1/messages", json={"text": "hello"})
        self.assertEqual(denied.status_code, 401)

        saved = self.client.post(
            "/api/yixiu/conversations/c-1/messages",
            json={"text": "hello", "confirmed": True},
            headers=self.auth_headers(idem="idem-message"),
        )
        self.assertEqual(saved.status_code, 200)

        loaded = self.client.get("/api/yixiu/conversations/c-1/messages")
        self.assertEqual(loaded.status_code, 200)
        self.assertEqual(loaded.get_json()["data"]["messages"][0]["text"], "hello")

    def test_task_create_replays_same_idempotency_key(self):
        payload = {"title": "replace bearing", "confirmed": True}
        headers = self.auth_headers(idem="idem-task-create")

        first = self.client.post("/api/yixiu/tasks", json=payload, headers=headers)
        second = self.client.post("/api/yixiu/tasks", json=payload, headers=headers)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.get_json()["data"]["id"], second.get_json()["data"]["id"])

    def test_task_memory_rejects_idempotency_conflict(self):
        headers = self.auth_headers(idem="idem-memory-conflict")
        first = self.client.post(
            "/api/yixiu/tasks/t-1/memory",
            json={"key": "risk", "value": "hot", "confirmed": True},
            headers=headers,
        )
        second = self.client.post(
            "/api/yixiu/tasks/t-1/memory",
            json={"key": "risk", "value": "cold", "confirmed": True},
            headers=headers,
        )

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 409)

    def test_conversation_message_replays_same_idempotency_key(self):
        payload = {"text": "hello", "confirmed": True}
        headers = self.auth_headers(idem="idem-message-replay")

        first = self.client.post("/api/yixiu/conversations/c-2/messages", json=payload, headers=headers)
        second = self.client.post("/api/yixiu/conversations/c-2/messages", json=payload, headers=headers)

        self.assertEqual(first.status_code, 200)
        self.assertEqual(second.status_code, 200)
        self.assertEqual(first.get_json()["data"]["id"], second.get_json()["data"]["id"])

    def test_knowledge_update_requires_confirmed_write(self):
        denied = self.client.post(
            "/api/yixiu/knowledge/update",
            json={"title": "case", "summary": "summary"},
            headers=self.auth_headers(),
        )
        self.assertEqual(denied.status_code, 409)

    def test_miniclaw_fastapi_chat_requires_auth(self):
        from starlette.requests import Request

        from miniclaw.gateway import ChatRequest
        from miniclaw.gateway import MiniClawGateway

        gateway = MiniClawGateway()
        gateway.setup()
        route = next(item for item in gateway.app.routes if getattr(item, "path", "") == "/miniclaw/chat")
        request = Request({"type": "http", "method": "POST", "path": "/miniclaw/chat", "headers": []})

        with self.assertRaises(Exception) as caught:
            asyncio.run(route.endpoint(ChatRequest(message="hello"), request))
        self.assertEqual(getattr(caught.exception, "status_code", None), 401)


if __name__ == "__main__":
    unittest.main()
