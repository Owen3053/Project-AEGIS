import ollama
from backend.memory.memory_manager import MemoryManager


class AegisBrain:

    def __init__(self):
        self.model = "qwen3:8b"
        self.memory = MemoryManager()

        self.messages = [
            {
                "role": "system",
                "content": (
                    "You are AEGIS, a personal AI assistant. "
                    "You are intelligent, helpful, calm, concise, "
                    "and proactive. "
                    "You assist the user with learning, programming, "
                    "research, planning, and everyday tasks."
                )
            }
        ]

    def think(self, message):

        text = message.lower().strip()

        # ==========================================
        # REMEMBER COMMAND
        # ==========================================

        if text.startswith("remember that "):

            memory = message[len("remember that "):].strip()

            if memory:
                self.memory.remember(memory)

                return f"I'll remember that: {memory}"

            return "What would you like me to remember?"

        # ==========================================
        # RECALL COMMAND
        # ==========================================

        if text in [
            "what do you remember about me?",
            "what do you remember?",
            "show my memories"
        ]:

            memories = self.memory.get_memories()

            if not memories:
                return "I don't have any saved memories yet."

            return "Here's what I remember:\n- " + "\n- ".join(memories)

        # ==========================================
        # FORGET COMMAND
        # ==========================================

        if text.startswith("forget "):

            keyword = message[7:].strip()

            if not keyword:
                return "What would you like me to forget?"

            deleted = self.memory.forget(keyword)

            if deleted:
                return (
                    f"I've forgotten {deleted} memory "
                    f"item(s) matching '{keyword}'."
                )

            return (
                f"I couldn't find any memory matching "
                f"'{keyword}'."
            )

        # ==========================================
        # NORMAL AI CONVERSATION
        # ==========================================

        self.messages.append(
            {
                "role": "user",
                "content": message
            }
        )

        response = ollama.chat(
            model=self.model,
            messages=self.messages
        )

        answer = response["message"]["content"]

        self.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return answer


def main():

    brain = AegisBrain()

    print("=" * 50)
    print("        PROJECT AEGIS")
    print("        AI Assistant v0.1")
    print("=" * 50)
    print("AEGIS is online.")
    print("Type 'exit' to shut down.\n")

    while True:

        user_input = input("You: ")

        if user_input.lower() in ["exit", "quit"]:

            print("\nAEGIS: Shutting down. Goodbye.")
            break

        if not user_input.strip():
            continue

        answer = brain.think(user_input)

        print(f"\nAEGIS: {answer}\n")


if __name__ == "__main__":
    main()