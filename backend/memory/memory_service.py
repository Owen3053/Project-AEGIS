from backend.memory.memory_manager import MemoryManager


class MemoryService:

    def __init__(self):

        self.memory = (
            MemoryManager()
        )

    # ==========================================
    # REMEMBER
    # ==========================================

    def remember(
        self,
        text,
        category="other",
        importance=3
    ):

        return self.memory.remember(
            text,
            category,
            importance
        )

    # ==========================================
    # RECALL
    # ==========================================

    def recall(
        self,
        query,
        limit=5
    ):

        return self.memory.search(
            query,
            limit
        )

    # ==========================================
    # ALL
    # ==========================================

    def get_all(self):

        return self.memory.get_memories()

    # ==========================================
    # DETAILS
    # ==========================================

    def get_details(self):

        return (
            self.memory.get_memory_details()
        )

    # ==========================================
    # FORGET
    # ==========================================

    def forget(
        self,
        keyword
    ):

        return self.memory.forget(
            keyword
        )

    # ==========================================
    # CLOSE
    # ==========================================

    def close(self):

        self.memory.close()