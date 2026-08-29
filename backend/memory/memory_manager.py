import sqlite3
import math
import ollama


class MemoryManager:

    def __init__(self, db_name="aegis_memory.db"):
        self.db_name = db_name
        self.connection = sqlite3.connect(self.db_name)
        self.cursor = self.connection.cursor()

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory TEXT NOT NULL,
                embedding TEXT
            )
        """)

        self.connection.commit()

    def create_embedding(self, text):
        response = ollama.embed(
            model="nomic-embed-text:latest",
            input=text
        )

        return response["embeddings"][0]

    def cosine_similarity(self, a, b):
        dot_product = sum(
            x * y for x, y in zip(a, b)
        )

        magnitude_a = math.sqrt(
            sum(x * x for x in a)
        )

        magnitude_b = math.sqrt(
            sum(x * x for x in b)
        )

        if magnitude_a == 0 or magnitude_b == 0:
            return 0

        return dot_product / (
            magnitude_a * magnitude_b
        )

    def remember(self, memory):
        memory = memory.strip()

        if not memory:
            return False

        self.cursor.execute(
            """
            SELECT id
            FROM memories
            WHERE LOWER(TRIM(memory)) = LOWER(TRIM(?))
            LIMIT 1
            """,
            (memory,)
        )

        if self.cursor.fetchone():
            return False

        embedding = self.create_embedding(memory)

        embedding_text = ",".join(
            str(value) for value in embedding
        )

        self.cursor.execute(
            """
            INSERT INTO memories (memory, embedding)
            VALUES (?, ?)
            """,
            (memory, embedding_text)
        )

        self.connection.commit()

        return True

    def search(self, query, limit=5):
        query = query.strip()

        if not query:
            return []

        query_embedding = self.create_embedding(query)

        self.cursor.execute(
            """
            SELECT memory, embedding
            FROM memories
            WHERE embedding IS NOT NULL
            """
        )

        rows = self.cursor.fetchall()

        results = []

        for memory, embedding_text in rows:
            try:
                memory_embedding = [
                    float(value)
                    for value in embedding_text.split(",")
                ]

                score = self.cosine_similarity(
                    query_embedding,
                    memory_embedding
                )

                results.append((score, memory))

            except Exception:
                continue

        results.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return [
            memory
            for score, memory in results[:limit]
        ]

    def get_memories(self):
        self.cursor.execute(
            """
            SELECT memory
            FROM memories
            ORDER BY id ASC
            """
        )

        rows = self.cursor.fetchall()

        return [row[0] for row in rows]

    def forget(self, keyword):
        keyword = keyword.strip()

        if not keyword:
            return 0

        self.cursor.execute(
            """
            DELETE FROM memories
            WHERE LOWER(memory) LIKE LOWER(?)
            """,
            ("%" + keyword + "%",)
        )

        deleted = self.cursor.rowcount

        self.connection.commit()

        return deleted

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
