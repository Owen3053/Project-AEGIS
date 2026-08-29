import ollama

from backend.core.router import CommandRouter
from backend.core.executor import CommandExecutor
from backend.memory.memory_manager import MemoryManager
from backend.memory.memory_detector import MemoryDetector


class AegisBrain:

    def __init__(self):
        self.model = "qwen3:8b"

        self.router = CommandRouter()
        self.executor = CommandExecutor()
        self.memory = MemoryManager()
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

    def handle_memory_detection(self, message):

        result = self.detector.detect(message)

        if not result["should_remember"]:
            return False

        memory = result["memory"].strip()

        if not memory:
            return False

        print()
        print("AEGIS: I noticed this may be useful to remember:")
        print()
        print(f'  "{memory}"')
        print()

        confirmation = input(
            "AEGIS: Should I remember this? (yes/no): "
        ).strip().lower()

        if confirmation in ["yes", "y"]:

            saved = self.memory.remember(memory)

            if saved:
                print("AEGIS: Got it. I'll remember that.")
            else:
                print("AEGIS: I already had that memory.")

        else:
            print("AEGIS: Okay, I won't save it.")

        print()

        return True

    def think(self, message):

        command = self.router.route(message)

        # Handle explicit commands first
        if command["type"] != "chat":
            return self.executor.execute(command)

        # Automatically detect useful memories
        self.handle_memory_detection(message)

        # Search relevant memories
        memories = self.memory.search(message)

        memory_context = ""

        if memories:
            memory_context = (
                "\n\nRELEVANT USER MEMORIES:\n"
                + "\n".join(
                    "- " + memory
                    for memory in memories
                )
            )

        enhanced_message = message + memory_context

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
    print("             PROJECT AEGIS")
    print("             AI Assistant v0.7.1")
    print("=" * 50)

    print("AEGIS is online.")
    print("Type 'exit' or 'quit' to shut down.")
    print()

    while True:

        try:
            user_input = input("You: ").strip()

        except KeyboardInterrupt:
            print("\nAEGIS: Shutting down. Goodbye.")
            break

        if user_input.lower() in ["exit", "quit"]:
            print("\nAEGIS: Shutting down. Goodbye.")
            break

        if not user_input:
            continue

        try:
            answer = brain.think(user_input)

            print()
            print("AEGIS:", answer)
            print()

        except Exception as error:
            print()
            print("AEGIS ERROR:", error)
            print()


if __name__ == "__main__":
    main()
