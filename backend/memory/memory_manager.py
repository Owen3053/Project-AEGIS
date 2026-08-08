import sqlite3
from pathlib import Path


class MemoryManager:

    def __init__(self):
        project_root = Path(__file__).resolve().parents[2]
        memory_folder = project_root / "memory"

        memory_folder.mkdir(exist_ok=True)

        self.database = memory_folder / "aegis_memory.db"

        self.create_database()

    def create_database(self):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory TEXT NOT NULL
            )
        """)

        connection.commit()
        connection.close()

    def remember(self, memory):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        cursor.execute(
            "INSERT INTO memories (memory) VALUES (?)",
            (memory,)
        )

        connection.commit()
        connection.close()

    def get_memories(self):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        cursor.execute("SELECT memory FROM memories")

        memories = cursor.fetchall()

        connection.close()

        return [memory[0] for memory in memories]

    def search(self, keyword):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        cursor.execute(
            "SELECT memory FROM memories WHERE memory LIKE ?",
            (f"%{keyword}%",)
        )

        memories = cursor.fetchall()

        connection.close()

        return [memory[0] for memory in memories]

    # Forget memories matching a keyword
    def forget(self, keyword):
        connection = sqlite3.connect(self.database)
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM memories WHERE memory LIKE ?",
            (f"%{keyword}%",)
        )

        deleted = cursor.rowcount

        connection.commit()
        connection.close()

        return deleted