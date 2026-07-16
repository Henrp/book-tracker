import sqlite3
from pathlib import Path

DB = Path(__file__).parent / "tracker.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS books (
    book_id     TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    author      TEXT,
    cover_url   TEXT,
    added_at    TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS progress (
    book_id        TEXT PRIMARY KEY REFERENCES books(book_id),
    last_read      INTEGER DEFAULT 0,
    last_known     INTEGER,
    updated_time   TEXT,
    last_checked   TEXT,
    status         TEXT DEFAULT 'active'   -- active | dropped | dead
);
"""

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    con.executescript(SCHEMA)
    return con

def add_book(con, book_id, meta):
    con.execute(
        "INSERT OR REPLACE INTO books (book_id, title, author, cover_url) VALUES (?,?,?,?)",
        (book_id, meta["title"], meta["author"], meta["cover_url"]))
    con.execute(
        "INSERT OR IGNORE INTO progress (book_id, last_known, updated_time, last_checked) "
        "VALUES (?,?,?,datetime('now'))",
        (book_id, meta["latest_chapter"], meta["updated_time"]))
    con.commit()

def get_tracked(con):
    return con.execute(
        "SELECT book_id FROM progress WHERE status='active'").fetchall()

def update_progress(con, book_id, meta):
    con.execute("""
        UPDATE progress
        SET last_known   = MAX(COALESCE(last_known, 0), ?),
            updated_time = ?,
            last_checked = datetime('now')
        WHERE book_id = ?""",
        (meta["latest_chapter"], meta["updated_time"], book_id))
    con.commit()

def mark_read(con, book_id, chapter):
    con.execute("UPDATE progress SET last_read=? WHERE book_id=?", (chapter, book_id))
    con.commit()

def all_active(con):
    return con.execute("""
        SELECT b.book_id, b.title, b.author, b.cover_url,
               p.last_read, p.last_known,
               p.last_known - p.last_read AS behind,
               p.updated_time, p.last_checked
        FROM books b JOIN progress p USING (book_id)
        WHERE p.status='active'
        ORDER BY behind DESC""").fetchall()

def unread(con):
    return con.execute("""
        SELECT b.title, b.author, p.last_read, p.last_known,
               p.last_known - p.last_read AS behind, p.updated_time
        FROM books b JOIN progress p USING (book_id)
        WHERE p.status='active' AND p.last_known > p.last_read
        ORDER BY behind DESC""").fetchall()