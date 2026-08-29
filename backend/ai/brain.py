import ollama

from backend.core.router import CommandRouter
from backend.core.executor import CommandExecutor
from backend.memory.memory_service import MemoryService
from backend.memory.memory_detector import MemoryDetector


class AegisBrain:

    def __init__(self):

        self.model = "qwen3:8b"

        self.router = CommandRouter()

        # One central memory service
        self.memory = MemoryService()

        # Executor uses the same memory service
        self.executor = CommandExecutor(self.memory)

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
    # AUTOMATIC MEMORY DETECTION
    # ==========================================

    def handle_memory_detection(self, message):

        result = self.detector.detect(message)

        if not result["should_remember"]:
            return

        memory = result["memory"].strip()

        if not memory:
            return

        print()
        print(
            "AEGIS: I noticed this may be useful to remember:"
        )
        print()
        print(f'  "{memory}"')
        print()

        confirmation = input(
            "AEGIS: Should I remember this? (yes/no): "
        ).strip().lower()

        if confirmation in ["yes", "y"]:

            saved = self.memory.remember(memory)

            if saved:
                print(
                    "AEGIS: Got it. I'll remember that."
                )
            else:
                print(
                    "AEGIS: I already had that memory."
                )

        else:

            print(
                "AEGIS: Okay, I won't save it."
            )

        print()

    # ==========================================
    # THINK
    # ==========================================

    def think(self, message):

        command = self.router.route(message)

        # --------------------------------------
        # Explicit commands
        # --------------------------------------

        if command["type"] != "chat":
            return self.executor.execute(command)

        # --------------------------------------
        # Automatic memory detection
        # --------------------------------------

        self.handle_memory_detection(message)

        # --------------------------------------
        # Relevant memory retrieval
        # --------------------------------------

        memories = self.memory.recall(message)

        memory_context = ""

        if memories:

            memory_context = (
                "\n\nRELEVANT USER MEMORIES:\n"
                + "\n".join(
                    "- " + memory
                    for memory in memories
                )
            )

        # --------------------------------------
        # AI conversation
        # --------------------------------------

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

        answer = response["message"]["content"]

        self.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )

        return answer

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
    print("             AI Assistant v0.8.0")
    print("=" * 50)

    print("AEGIS is online.")
    print("Type 'exit' or 'quit' to shut down.")
    print()

    try:

        while True:

            try:
                user_input = input("You: ").strip()

            except KeyboardInterrupt:

                print(
                    "\nAEGIS: Shutting down. Goodbye."
                )
                break

            if user_input.lower() in ["exit", "quit"]:

                print(
                    "\nAEGIS: Shutting down. Goodbye."
                )
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

    finally:

        brain.close()


if __name__ == "__main__":
    main()
