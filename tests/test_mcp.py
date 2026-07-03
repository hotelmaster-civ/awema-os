"""Invariant : le serveur MCP répond correctement au protocole (initialize, tools/list, erreurs)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts"))
import awema_mcp  # noqa: E402


class TestMCP(unittest.TestCase):
    def test_initialize(self):
        r = awema_mcp.handle({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
        self.assertEqual(r["result"]["protocolVersion"], awema_mcp.PROTO)
        self.assertEqual(r["result"]["serverInfo"]["name"], "awema")
        self.assertIn("tools", r["result"]["capabilities"])

    def test_tools_list(self):
        r = awema_mcp.handle({"jsonrpc": "2.0", "id": 2, "method": "tools/list"})
        tools = r["result"]["tools"]
        names = [t["name"] for t in tools]
        self.assertIn("awema_status", names)
        self.assertIn("awema_run_agent", names)
        self.assertIn("awema_client_new", names)
        for t in tools:                                  # chaque outil : description + inputSchema objet
            self.assertTrue(t["description"])
            self.assertEqual(t["inputSchema"]["type"], "object")

    def test_unknown_tool(self):
        r = awema_mcp.handle({"jsonrpc": "2.0", "id": 3, "method": "tools/call", "params": {"name": "nope"}})
        self.assertIn("error", r)

    def test_unknown_method(self):
        r = awema_mcp.handle({"jsonrpc": "2.0", "id": 4, "method": "foo/bar"})
        self.assertIn("error", r)

    def test_notification_sans_reponse(self):
        self.assertIsNone(awema_mcp.handle({"jsonrpc": "2.0", "method": "notifications/initialized"}))


if __name__ == "__main__":
    unittest.main()
