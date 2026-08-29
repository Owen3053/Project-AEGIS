import ollama
import json


class MemoryDetector:

    def __init__(self):
        self.model = "qwen3:8b"

    def detect(self, message):

        prompt = f"""
You are a memory detection system for an AI assistant.

Analyze the user's message.

Determine whether it contains useful personal information
that could be remembered for future conversations.

Good memories include:
- projects the user is working on
- programming languages they use
- long-term goals
- preferences
- important recurring interests

Do NOT detect:
- ordinary questions
- temporary requests
- greetings
- random conversation
- information about other people

Return ONLY valid JSON in this format:

{{
    "should_remember": true,
    "memory": "short useful memory"
}}

or:

{{
    "should_remember": false,
    "memory": ""
}}

User message:
{message}
"""

        response = ollama.chat(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        text = response["message"]["content"].strip()

        try:
            result = json.loads(text)

            return {
                "should_remember": bool(
                    result.get("should_remember", False)
                ),
                "memory": str(
                    result.get("memory", "")
                ).strip()
            }

        except json.JSONDecodeError:

            return {
                "should_remember": False,
                "memory": ""
            }
