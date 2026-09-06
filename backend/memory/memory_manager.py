import math
import sqlite3
from datetime import datetime, timezone

import ollama


class MemoryManager:

    EMBEDDING_MODEL = "nomic-embed-text:latest"

    DUPLICATE_THRESHOLD = 0.92
    RECALL_THRESHOLD = 0.35

    def __init__(
        self,
        db_name="aegis_memory.db"
    ):

        self.db_name = db_name

        self.connection = sqlite3.connect(
            self.db_name
        )

        self.cursor = (
            self.connection.cursor()
        )

        self._create_tables()
        self._migrate_schema()

    # ==========================================
    # DATABASE SETUP
    # ==========================================

    def _create_tables(self):

        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory TEXT NOT NULL,
                embedding TEXT,
                category TEXT,
                importance INTEGER DEFAULT 3,
                created_at TEXT,
                updated_at TEXT
            )
        """)

        self.connection.commit()

    def _migrate_schema(self):

        self.cursor.execute(
            "PRAGMA table_info(memories)"
        )

        columns = {
            row[1]
            for row in self.cursor.fetchall()
        }

        if "category" not in columns:

            self.cursor.execute(
                """
                ALTER TABLE memories
                ADD COLUMN category TEXT
                """
            )

        if "importance" not in columns:

            self.cursor.execute(
                """
                ALTER TABLE memories
                ADD COLUMN importance INTEGER DEFAULT 3
                """
            )

        if "created_at" not in columns:

            self.cursor.execute(
                """
                ALTER TABLE memories
                ADD COLUMN created_at TEXT
                """
            )

        if "updated_at" not in columns:

            self.cursor.execute(
                """
                ALTER TABLE memories
                ADD COLUMN updated_at TEXT
                """
            )

        now = self._timestamp()

        self.cursor.execute(
            """
            UPDATE memories
            SET
                category = COALESCE(
                    NULLIF(category, ''),
                    'other'
                ),
                importance = COALESCE(
                    importance,
                    3
                ),
                created_at = COALESCE(
                    created_at,
                    ?
                ),
                updated_at = COALESCE(
                    updated_at,
                    ?
                )
            """,
            (
                now,
                now,
            )
        )

        self.connection.commit()

    # ==========================================
    # EMBEDDINGS
    # ==========================================

    def create_embedding(self, text):

        response = ollama.embed(
            model=self.EMBEDDING_MODEL,
            input=text
        )

        embeddings = response.get(
            "embeddings",
            []
        )

        if not embeddings:
            raise ValueError(
                "Embedding model returned no embedding."
            )

        return embeddings[0]

    @staticmethod
    def _embedding_to_text(
        embedding
    ):

        return ",".join(
            str(value)
            for value in embedding
        )

    @staticmethod
    def _text_to_embedding(
        embedding_text
    ):

        return [
            float(value)
            for value
            in embedding_text.split(",")
        ]

    # ==========================================
    # SIMILARITY
    # ==========================================

    def cosine_similarity(self, a, b):

        dot_product = sum(
            x * y
            for x, y in zip(a, b)
        )

        magnitude_a = math.sqrt(
            sum(
                x * x
                for x in a
            )
        )

        magnitude_b = math.sqrt(
            sum(
                x * x
                for x in b
            )
        )

        if (
            magnitude_a == 0
            or magnitude_b == 0
        ):
            return 0

        return (
            dot_product
            / (
                magnitude_a
                * magnitude_b
            )
        )

    # ==========================================
    # REMEMBER
    # ==========================================

    def remember(
        self,
        memory,
        category="other",
        importance=3
    ):

        memory = str(
            memory
        ).strip()

        if not memory:
            return False

        category = str(
            category or "other"
        ).strip().lower()

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

        try:
            importance = int(
                importance
            )
        except (
            TypeError,
            ValueError
        ):
            importance = 3

        importance = max(
            1,
            min(
                importance,
                5
            )
        )

        # --------------------------------------
        # Exact duplicate
        # --------------------------------------

        self.cursor.execute(
            """
            SELECT id
            FROM memories
            WHERE LOWER(TRIM(memory))
                = LOWER(TRIM(?))
            LIMIT 1
            """,
            (memory,)
        )

        existing_exact = (
            self.cursor.fetchone()
        )

        if existing_exact:

            self._update_memory_metadata(
                existing_exact[0],
                category,
                importance
            )

            return False

        # --------------------------------------
        # Create embedding
        # --------------------------------------

        try:

            embedding = (
                self.create_embedding(
                    memory
                )
            )

        except Exception:

            return False

        embedding_text = (
            self._embedding_to_text(
                embedding
            )
        )

        # --------------------------------------
        # Near duplicate detection
        # --------------------------------------

        similar_id = (
            self._find_similar_memory(
                embedding
            )
        )

        now = self._timestamp()

        if similar_id is not None:

            self.cursor.execute(
                """
                UPDATE memories
                SET
                    memory = ?,
                    embedding = ?,
                    category = ?,
                    importance = ?,
                    updated_at = ?
                WHERE id = ?
                """,
                (
                    memory,
                    embedding_text,
                    category,
                    importance,
                    now,
                    similar_id,
                )
            )

            self.connection.commit()

            return False

        # --------------------------------------
        # Insert new memory
        # --------------------------------------

        self.cursor.execute(
            """
            INSERT INTO memories (
                memory,
                embedding,
                category,
                importance,
                created_at,
                updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                memory,
                embedding_text,
                category,
                importance,
                now,
                now,
            )
        )

        self.connection.commit()

        return True

    # ==========================================
    # SIMILAR MEMORY
    # ==========================================

    def _find_similar_memory(
        self,
        query_embedding
    ):

        self.cursor.execute(
            """
            SELECT id, embedding
            FROM memories
            WHERE embedding IS NOT NULL
            """
        )

        rows = self.cursor.fetchall()

        best_id = None
        best_score = 0.0

        for memory_id, embedding_text in rows:

            try:

                memory_embedding = (
                    self._text_to_embedding(
                        embedding_text
                    )
                )

                score = (
                    self.cosine_similarity(
                        query_embedding,
                        memory_embedding
                    )
                )

            except Exception:

                continue

            if score > best_score:

                best_score = score
                best_id = memory_id

        if (
            best_id is not None
            and best_score
            >= self.DUPLICATE_THRESHOLD
        ):

            return best_id

        return None

    # ==========================================
    # RECALL
    # ==========================================

    def search(
        self,
        query,
        limit=5
    ):

        query = str(
            query
        ).strip()

        if not query:
            return []

        try:

            query_embedding = (
                self.create_embedding(
                    query
                )
            )

        except Exception:

            return []

        self.cursor.execute(
            """
            SELECT
                id,
                memory,
                embedding,
                category,
                importance
            FROM memories
            WHERE embedding IS NOT NULL
            """
        )

        rows = self.cursor.fetchall()

        results = []

        for (
            memory_id,
            memory,
            embedding_text,
            category,
            importance
        ) in rows:

            try:

                memory_embedding = (
                    self._text_to_embedding(
                        embedding_text
                    )
                )

                similarity = (
                    self.cosine_similarity(
                        query_embedding,
                        memory_embedding
                    )
                )

                if (
                    similarity
                    < self.RECALL_THRESHOLD
                ):
                    continue

                importance_value = (
                    int(
                        importance or 3
                    )
                )

                # Small importance boost.
                adjusted_score = (
                    similarity
                    + (
                        0.02
                        * max(
                            0,
                            importance_value - 3
                        )
                    )
                )

                results.append(
                    (
                        adjusted_score,
                        similarity,
                        memory_id,
                        memory,
                        category,
                        importance_value,
                    )
                )

            except Exception:

                continue

        results.sort(
            key=lambda item: item[0],
            reverse=True
        )

        return [
            memory
            for (
                _adjusted_score,
                _similarity,
                _memory_id,
                memory,
                _category,
                _importance
            )
            in results[:limit]
        ]

    # ==========================================
    # ALL MEMORIES
    # ==========================================

    def get_memories(self):

        self.cursor.execute(
            """
            SELECT memory
            FROM memories
            ORDER BY id ASC
            """
        )

        rows = self.cursor.fetchall()

        return [
            row[0]
            for row in rows
        ]

    # ==========================================
    # MEMORY DETAILS
    # ==========================================

    def get_memory_details(
        self
    ):

        self.cursor.execute(
            """
            SELECT
                id,
                memory,
                category,
                importance,
                created_at,
                updated_at
            FROM memories
            ORDER BY id ASC
            """
        )

        rows = self.cursor.fetchall()

        return [
            {
                "id": row[0],
                "memory": row[1],
                "category": row[2],
                "importance": row[3],
                "created_at": row[4],
                "updated_at": row[5],
            }
            for row in rows
        ]

    # ==========================================
    # UPDATE METADATA
    # ==========================================

    def _update_memory_metadata(
        self,
        memory_id,
        category,
        importance
    ):

        now = self._timestamp()

        self.cursor.execute(
            """
            UPDATE memories
            SET
                category = ?,
                importance = ?,
                updated_at = ?
            WHERE id = ?
            """,
            (
                category,
                importance,
                now,
                memory_id,
            )
        )

        self.connection.commit()

    # ==========================================
    # FORGET
    # ==========================================

    def forget(
        self,
        keyword
    ):

        keyword = str(
            keyword
        ).strip()

        if not keyword:
            return 0

        self.cursor.execute(
            """
            DELETE FROM memories
            WHERE LOWER(memory)
                LIKE LOWER(?)
            """,
            (
                "%" + keyword + "%",
            )
        )

        deleted = (
            self.cursor.rowcount
        )

        self.connection.commit()

        return deleted

    # ==========================================
    # TIMESTAMP
    # ==========================================

    @staticmethod
    def _timestamp():

        return datetime.now(
            timezone.utc
        ).isoformat(
            timespec="seconds"
        )

    # ==========================================
    # CLOSE
    # ==========================================

    def close(self):

        if self.connection:

            self.connection.close()

            self.connection = None
            self.cursor = None


if __name__ == "__main__":

    memory = MemoryManager()

    tests = [
        (
            "I am building "
            "Project AEGIS.",
            "project",
            5
        ),
        (
            "I use Python "
            "for development.",
            "skill",
            4
        ),
        (
            "I want to become "
            "better at cybersecurity.",
            "goal",
            4
        ),
    ]

    for (
        text,
        category,
        importance
    ) in tests:

        print(
            "\nREMEMBER:",
            text
        )

        print(
            memory.remember(
                text,
                category,
                importance
            )
        )

    print(
        "\nALL MEMORIES:"
    )

    print(
        memory.get_memory_details()
    )

    memory.close()