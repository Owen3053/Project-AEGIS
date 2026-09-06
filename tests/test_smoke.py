import os
import tempfile
import unittest

from backend.ai.brain import AegisBrain
from backend.automation.automation_manager import AutomationManager
from backend.core.permission_manager import PermissionManager
from backend.core.router import CommandRouter
from backend.memory.memory_service import MemoryService
from backend.tools.tool_manager import ToolManager
from backend.voice.speech_to_text import SpeechToText
from backend.voice.text_to_speech import TextToSpeech
from backend.voice.voice_manager import VoiceManager


class AegisSmokeTests(unittest.TestCase):

    # ==========================================
    # IMPORT / COMPONENT TESTS
    # ==========================================

    def test_core_components_import(self):

        self.assertIsNotNone(
            CommandRouter
        )

        self.assertIsNotNone(
            ToolManager
        )

        self.assertIsNotNone(
            PermissionManager
        )

        self.assertIsNotNone(
            AutomationManager
        )

        self.assertIsNotNone(
            MemoryService
        )

    def test_voice_components_import(self):

        self.assertIsNotNone(
            SpeechToText
        )

        self.assertIsNotNone(
            TextToSpeech
        )

        self.assertIsNotNone(
            VoiceManager
        )

    # ==========================================
    # TOOL DISCOVERY
    # ==========================================

    def test_tool_discovery(self):

        manager = ToolManager()

        tools = manager.list_tools()

        self.assertIn(
            "calculator",
            tools
        )

        self.assertIn(
            "files",
            tools
        )

        self.assertIn(
            "search",
            tools
        )

        self.assertIn(
            "system_info",
            tools
        )

    # ==========================================
    # ROUTER
    # ==========================================

    def test_router_calculator(self):

        router = CommandRouter()

        result = router.route(
            "calculate 25 * 4"
        )

        self.assertEqual(
            result["type"],
            "tool"
        )

        self.assertEqual(
            result["action"],
            "calculator"
        )

        self.assertEqual(
            result["data"],
            "25 * 4"
        )

    def test_router_file_details(self):

        router = CommandRouter()

        result = router.route(
            "file info .\\README.md"
        )

        self.assertEqual(
            result["type"],
            "tool"
        )

        self.assertEqual(
            result["action"],
            "files"
        )

        self.assertEqual(
            result["data"]["operation"],
            "details"
        )

    def test_router_automation(self):

        router = CommandRouter()

        result = router.route(
            "open calculator"
        )

        self.assertEqual(
            result["type"],
            "automation"
        )

        self.assertEqual(
            result["action"],
            "open"
        )

    def test_router_chat(self):

        router = CommandRouter()

        result = router.route(
            "tell me about artificial intelligence"
        )

        self.assertEqual(
            result["type"],
            "chat"
        )

    # ==========================================
    # PERMISSION SYSTEM
    # ==========================================

    def test_safe_action_allowed(self):

        permissions = (
            PermissionManager()
        )

        result = permissions.check({
            "type": "tool",
            "action": "calculator",
            "data": "25 * 4"
        })

        self.assertTrue(
            result["allowed"]
        )

        self.assertFalse(
            result["requires_confirmation"]
        )

    def test_file_write_requires_confirmation(self):

        permissions = (
            PermissionManager()
        )

        result = permissions.check({
            "type": "tool",
            "action": "files",
            "data": {
                "operation": "write_file",
                "path": ".\\test.txt",
                "content": "hello"
            }
        })

        self.assertTrue(
            result["allowed"]
        )

        self.assertTrue(
            result["requires_confirmation"]
        )

    def test_windows_system_path_blocked(self):

        permissions = (
            PermissionManager()
        )

        result = permissions.check({
            "type": "tool",
            "action": "files",
            "data": {
                "operation": "write_file",
                "path": r"C:\Windows\test.txt",
                "content": "blocked"
            }
        })

        self.assertFalse(
            result["allowed"]
        )

    # ==========================================
    # BRAIN VALIDATION
    # ==========================================

    def test_brain_action_validation(self):

        brain = AegisBrain()

        try:

            result = brain._validate_action({
                "type": "tool",
                "action": "calculator",
                "data": "25 * 4"
            })

            self.assertIsNotNone(
                result
            )

            self.assertEqual(
                result["action"],
                "calculator"
            )

        finally:

            brain.close()

    def test_brain_rejects_unknown_tool(self):

        brain = AegisBrain()

        try:

            result = brain._validate_action({
                "type": "tool",
                "action": "does_not_exist",
                "data": "test"
            })

            self.assertIsNone(
                result
            )

        finally:

            brain.close()

    def test_brain_validates_automation(self):

        brain = AegisBrain()

        try:

            result = brain._validate_action({
                "type": "automation",
                "action": "open",
                "data": "calculator"
            })

            self.assertIsNotNone(
                result
            )

            self.assertEqual(
                result["type"],
                "automation"
            )

        finally:

            brain.close()

    # ==========================================
    # FILE TOOL
    # ==========================================

    def test_file_tool_safe_operations(self):

        manager = ToolManager()

        with tempfile.TemporaryDirectory() as temp_dir:

            result = manager.execute(
                "files",
                {
                    "operation": "create_folder",
                    "path": os.path.join(
                        temp_dir,
                        "test_folder"
                    )
                }
            )

            self.assertTrue(
                result["success"]
            )

            self.assertTrue(
                os.path.isdir(
                    os.path.join(
                        temp_dir,
                        "test_folder"
                    )
                )
            )

    # ==========================================
    # AUTOMATION NON-DESTRUCTIVE CHECK
    # ==========================================

    def test_automation_known_target(self):

        automation = (
            AutomationManager()
        )

        # Do not actually open anything.
        # Verify the configured targets instead.

        self.assertIn(
            "calculator",
            automation.apps
        )

        self.assertIn(
            "youtube",
            automation.websites
        )

    # ==========================================
    # RESULT
    # ==========================================

    def tearDown(self):

        pass


if __name__ == "__main__":

    unittest.main(
        verbosity=2
    )