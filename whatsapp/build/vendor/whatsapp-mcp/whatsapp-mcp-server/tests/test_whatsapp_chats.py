import os
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path


SERVER_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SERVER_DIR))

import whatsapp  # noqa: E402


class ListChatsTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "messages.db")
        self.original_db_path = whatsapp.MESSAGES_DB_PATH
        whatsapp.MESSAGES_DB_PATH = self.db_path
        self._init_db()

    def tearDown(self):
        whatsapp.MESSAGES_DB_PATH = self.original_db_path
        self.temp_dir.cleanup()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE chats (
                    jid TEXT PRIMARY KEY,
                    name TEXT,
                    last_message_time TIMESTAMP
                )
            """)
            cursor.execute("""
                CREATE TABLE messages (
                    id TEXT,
                    chat_jid TEXT,
                    sender TEXT,
                    content TEXT,
                    timestamp TIMESTAMP,
                    is_from_me BOOLEAN,
                    media_type TEXT,
                    filename TEXT,
                    url TEXT,
                    media_key BLOB,
                    file_sha256 BLOB,
                    file_enc_sha256 BLOB,
                    file_length INTEGER,
                    PRIMARY KEY (id, chat_jid)
                )
            """)
            cursor.execute(
                "INSERT INTO chats VALUES (?, ?, ?)",
                ("111@s.whatsapp.net", "Alice", "2026-06-06T12:01:00+08:00"),
            )
            cursor.execute(
                "INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, NULL, NULL, NULL, NULL, NULL)",
                (
                    "older",
                    "111@s.whatsapp.net",
                    "111@s.whatsapp.net",
                    "older message",
                    "2026-06-06T11:59:00+08:00",
                    0,
                ),
            )
            cursor.execute(
                "INSERT INTO messages VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, NULL, NULL, NULL, NULL, NULL)",
                (
                    "latest",
                    "111@s.whatsapp.net",
                    "111@s.whatsapp.net",
                    "latest message",
                    "2026-06-06T12:00:00+08:00",
                    0,
                ),
            )
            conn.commit()
        finally:
            conn.close()

    def test_list_chats_without_last_message_does_not_join_messages(self):
        chats = whatsapp.list_chats(include_last_message=False)

        self.assertEqual(len(chats), 1)
        self.assertEqual(chats[0].jid, "111@s.whatsapp.net")
        self.assertIsNone(chats[0].last_message)
        self.assertIsNone(chats[0].last_sender)
        self.assertIsNone(chats[0].last_is_from_me)

    def test_list_chats_uses_latest_message_when_timestamp_does_not_match(self):
        chats = whatsapp.list_chats(include_last_message=True)

        self.assertEqual(len(chats), 1)
        self.assertEqual(chats[0].last_message, "latest message")
        self.assertEqual(chats[0].last_sender, "111@s.whatsapp.net")
        self.assertEqual(chats[0].last_is_from_me, 0)


if __name__ == "__main__":
    unittest.main()
