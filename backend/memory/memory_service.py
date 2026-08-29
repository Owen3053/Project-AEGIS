from backend.memory.memory_manager import MemoryManager


class MemoryService:

    def __init__(self):
        self.memory = MemoryManager()

    def remember(self, text):
        return self.memory.remember(text)

    def recall(self, query, limit=5):
        return self.memory.search(query, limit)

    def get_all(self):
        return self.memory.get_memories()

    def forget(self, keyword):
        return self.memory.forget(keyword)

    def close(self):
        self.memory.close()
