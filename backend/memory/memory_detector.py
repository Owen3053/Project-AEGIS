import json
import re

import ollama


class MemoryDetector:

    def __init__(self):
        self.model = "qwen3:8b"

    def detect(self, message):

        if not message or not message.strip():
            return {
                "should_remember": False,
                "memory": "",
                "category": "",
                "importance": 0
            }

        prompt = f"""
You are the memory detection system for AEGIS, a personal AI assistant.

Analyze the user's message and determine whether it contains
useful long-term information that should be remembered.

Good memories include:
- long-term projects
- programming languages or technologies the user regularly uses
- persistent goals
- stable preferences
- recurring interests
- important workflow preferences
- long-term plans

Do NOT remember:
- greetings
- ordinary questions
- temporary requests
- one-time tasks
- random conversation
- information about other people
- temporary moods or passing comments
- obvious commands such as "open calculator"
- temporary file operations

A useful memory should be:
- concise
- written as a factual statement
- useful in future conversations
- about the user

Choose one category:
- project
- skill
- goal
- preference
- interest
- workflow
- other

Importance must be an integer from 1 to 5.

Return ONLY valid JSON in exactly this structure:

{{
    "should_remember": true,
    "memory": "short useful memory",
    "category": "project",
    "importance": 4
}}

or:

{{
    "should_remember": false,
    "memory": "",
    "category": "",
    "importance": 0
}}

User message:
{message}
"""

        try:

            response = ollama.chat(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            raw = response[
                "message"
            ][
                "content"
            ].strip()

            result = self._parse_json(
                raw
            )

            if not isinstance(
                result,
                dict
            ):
                return self._empty_result()

            should_remember = (
                result.get(
                    "should_remember",
                    False
                )
                is True
            )

            memory = str(
                result.get(
                    "memory",
                    ""
                )
            ).strip()

            category = str(
                result.get(
                    "category",
                    ""
                )
            ).strip().lower()

            try:
                importance = int(
                    result.get(
                        "importance",
                        0
                    )
                )
            except (
                TypeError,
                ValueError
            ):
                importance = 0

            importance = max(
                0,
                min(
                    importance,
                    5
                )
            )

            valid_categories = {
                "project",
                "skill",
                "goal",
                "preference",
                "interest",
                "workflow",
                "other",
            }

            if category not in valid_categories:
                category = "other"

            if not should_remember:
                return self._empty_result()

            if not memory:
                return self._empty_result()

            if len(memory) < 8:
                return self._empty_result()

            if importance <= 0:
                importance = 3

            if self._looks_temporary(
                memory
            ):
                return self._empty_result()

            return {
                "should_remember": True,
                "memory": memory,
                "category": category,
                "importance": importance
            }

        except Exception:

            return self._empty_result()

    @staticmethod
    def _parse_json(raw):

        cleaned = re.sub(
            r"```(?:json)?",
            "",
            raw,
            flags=re.IGNORECASE
        ).replace(
            "```",
            ""
        ).strip()

        try:
            return json.loads(
                cleaned
            )
        except json.JSONDecodeError:
            pass

        match = re.search(
            r"\{.*\}",
            cleaned,
            re.DOTALL
        )

        if not match:
            return None

        try:
            return json.loads(
                match.group(0)
            )
        except json.JSONDecodeError:
            return None

    @staticmethod
    def _looks_temporary(memory):

        temporary_phrases = [
            "right now",
            "at the moment",
            "today",
            "tonight",
            "this morning",
            "this afternoon",
            "for now",
            "currently doing",
            "temporary",
            "just for today",
        ]

        normalized = memory.lower()

        return any(
            phrase in normalized
            for phrase in temporary_phrases
        )

    @staticmethod
    def _empty_result():

        return {
            "should_remember": False,
            "memory": "",
            "category": "",
            "importance": 0
        }


if __name__ == "__main__":

    detector = MemoryDetector()

    tests = [
        "I am building Project AEGIS.",
        "I like Python.",
        "What is the weather today?",
        "Open calculator.",
    ]

    for test in tests:

        print(
            f"\nINPUT: {test}"
        )

        print(
            detector.detect(test)
        )