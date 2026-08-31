import json
import re

import ollama

from backend.core.router import CommandRouter
from backend.core.executor import CommandExecutor
from backend.memory.memory_service import MemoryService
from backend.memory.memory_detector import MemoryDetector


class AegisBrain:

    def __init__(self):

        self.model = "qwen3:8b"

        self.router = CommandRouter()

        self.memory = MemoryService()

        self.executor = CommandExecutor(
            self.memory
        )

        self.detector = MemoryDetector()

        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are AEGIS, a personal AI assistant. "
                    "Be helpful, concise, and accurate. "
                    "Use relevant stored memories when answering. "
                    "Never invent memories."
                )
            }
        ]

    # ==========================================
    # AI TOOL SELECTION
    # ==========================================

    def select_tool(self, message):

        tools = self.executor.tools.list_tools()

        tool_descriptions = []

        for name, description in tools.items():

            tool_descriptions.append(
                f"- {name}: {description}"
            )

        available_tools = "\n".join(
            tool_descriptions
        )

        prompt = f"""
You are the tool-selection system for AEGIS.

Available tools:
{available_tools}

Analyze the user's request and decide whether
one of the available tools should be used.

Return ONLY valid JSON.

If a tool is required:

{{
    "use_tool": true,
    "tool": "tool_name",
    "data": "data needed by the tool"
}}

If no tool is required:

{{
    "use_tool": false,
    "tool": null,
    "data": null
}}

Rules:

1. Only select tools from the available tools.
2. Never invent tool names.
3. Do not answer the user.
4. Do not explain your decision.
5. Return JSON only.
6. For calculator requests, put the mathematical
   expression in data.
7. For search requests, put the search query in data.
8. For system information requests, data should be null.

User request:
{message}
"""

        try:

            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    }
                ]
            )

            raw = response[
                "message"
            ][
                "content"
            ].strip()

            raw = re.sub(
                r"```(?:json)?",
                "",
                raw,
                flags=re.IGNORECASE
            ).replace(
                "```",
                ""
            ).strip()

            match = re.search(
                r"\{.*\}",
                raw,
                re.DOTALL
            )

            if not match:
                return None

            result = json.loads(
                match.group(0)
            )

            if not isinstance(
                result,
                dict
            ):
                return None

            if result.get(
                "use_tool"
            ) is not True:
                return None

            tool_name = result.get(
                "tool"
            )

            if not tool_name:
                return None

            if not self.executor.tools.has_tool(
                tool_name
            ):
                return None

            return {
                "type": "tool",
                "action": tool_name,
                "data": result.get("data")
            }

        except Exception:

            return None

    # ==========================================
    # TOOL RESULT REASONING
    # ==========================================

    def interpret_tool_result(
        self,
        result,
        original_request
    ):

        if not isinstance(
            result,
            dict
        ):
            return result

        if not result.get(
            "success",
            False
        ):

            return result.get(
                "error",
                "The tool failed."
            )

        tool_name = result.get(
            "tool"
        )

        data = result.get(
            "data"
        )

        prompt = f"""
You are AEGIS.

The user asked:
{original_request}

A tool was executed.

Tool:
{tool_name}

Tool result:
{json.dumps(data, indent=2, default=str)}

Answer the user's original request using
ONLY the information contained in the tool result.

Rules:

1. Do not invent information.
2. Do not mention internal tool architecture
   unless the user asks about it.
3. Be concise.
4. Answer naturally.
"""

        try:

            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    }
                ]
            )

            return response[
                "message"
            ][
                "content"
            ].strip()

        except Exception:

            return str(data)

    # ==========================================
    # AUTOMATIC MEMORY DETECTION
    # ==========================================

    def handle_memory_detection(
        self,
        message
    ):

        result = self.detector.detect(
            message
        )

        if not result[
            "should_remember"
        ]:
            return

        memory = result[
            "memory"
        ].strip()

        if not memory:
            return

        print()
        print(
            "AEGIS: I noticed this may be "
            "useful to remember:"
        )
        print()

        print(
            f'  "{memory}"'
        )

        print()

        confirmation = input(
            "AEGIS: Should I remember this? "
            "(yes/no): "
        ).strip().lower()

        if confirmation in [
            "yes",
            "y"
        ]:

            saved = self.memory.remember(
                memory
            )

            if saved:

                print(
                    "AEGIS: Got it. "
                    "I'll remember that."
                )

            else:

                print(
                    "AEGIS: I already had "
                    "that memory."
                )

        else:

            print(
                "AEGIS: Okay, I won't save it."
            )

        print()

    # ==========================================
    # NORMAL AI CHAT
    # ==========================================

    def chat(self, message):

        self.handle_memory_detection(
            message
        )

        memories = self.memory.recall(
            message
        )

        memory_context = ""

        if memories:

            memory_context = (
                "\n\nRELEVANT USER MEMORIES:\n"
                + "\n".join(
                    "- " + memory
                    for memory in memories
                )
            )

        enhanced_message = (
            message + memory_context
        )

        self.messages.append(
            {
                "role": "user",
                "content": enhanced_message
            }
        )

        response = ollama.chat(
            model=self.model,
            messages=self.messages
        )

        answer = response[
            "message"
        ][
            "content"
        ]

        self.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return answer

    # ==========================================
    # THINK
    # ==========================================

    def think(self, message):

        command = self.router.route(
            message
        )

        # --------------------------------------
        # Explicit commands
        # --------------------------------------

        if command["type"] != "chat":

            result = self.executor.execute(
                command
            )

            # Tool results need AI interpretation.
            if (
                command["type"] == "tool"
                and isinstance(result, dict)
            ):

                return self.interpret_tool_result(
                    result,
                    message
                )

            return result

        # --------------------------------------
        # AI tool selection
        # --------------------------------------

        ai_command = self.select_tool(
            message
        )

        if ai_command:

            result = self.executor.execute(
                ai_command
            )

            if isinstance(
                result,
                dict
            ):

                return self.interpret_tool_result(
                    result,
                    message
                )

            return result

        # --------------------------------------
        # Normal conversation
        # --------------------------------------

        return self.chat(
            message
        )

    # ==========================================
    # CLOSE
    # ==========================================

    def close(self):

        self.memory.close()


# ==============================================
# MAIN
# ==============================================

def main():

    brain = AegisBrain()

    print("=" * 50)
    print("             PROJECT AEGIS")
    print("             AI Assistant v0.9.6")
    print("=" * 50)

    print(
        "AEGIS is online."
    )

    print(
        "Type 'exit' or 'quit' to shut down."
    )

    print()

    try:

        while True:

            try:

                user_input = input(
                    "You: "
                ).strip()

            except KeyboardInterrupt:

                print(
                    "\nAEGIS: Shutting down. Goodbye."
                )

                break

            if user_input.lower() in [
                "exit",
                "quit"
            ]:

                print(
                    "\nAEGIS: Shutting down. Goodbye."
                )

                break

            if not user_input:
                continue

            try:

                answer = brain.think(
                    user_input
                )

                print()
                print(
                    "AEGIS:",
                    answer
                )
                print()

            except Exception as error:

                print()
                print(
                    "AEGIS ERROR:",
                    error
                )
                print()

    finally:

        brain.close()


if __name__ == "__main__":
    main()