import html
import os
import re
import sqlite3
import time


def build_sqlite_database(db_filepath: str = "dictionary.db"):
    """
    Reads the CSV file and builds a SQLite database with FTS5 full-text search.
    """
    print(f"Output file: {db_filepath}\n")

    if os.path.exists(db_filepath):
        os.remove(db_filepath)
        print("Removed existing database file.")

    conn = sqlite3.connect(db_filepath)
    cursor = conn.cursor()

    cursor.execute("PRAGMA journal_mode=DELETE")

    cursor.execute("""
        CREATE TABLE dictionary_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lang_from TEXT NOT NULL,
            lang_to TEXT NOT NULL,
            word_from TEXT NOT NULL,
            word_to TEXT NOT NULL,
            word_type TEXT,
            classification TEXT
        )
    """)

    # Create FTS5 virtual table for full-text search
    # This indexes word_from and word_to for lightning-fast %text% searches
    cursor.execute("""
        CREATE VIRTUAL TABLE dictionary_fts USING fts5(
            word_from,
            word_to,
            content='dictionary_entries',
            content_rowid='id'
        )
    """)

    # Create triggers to keep FTS index in sync (not needed for read-only, but good practice)
    cursor.execute("""
        CREATE TRIGGER dict_fts_insert AFTER INSERT ON dictionary_entries BEGIN
            INSERT INTO dictionary_fts(rowid, word_from, word_to)
            VALUES (new.id, new.word_from, new.word_to);
        END
    """)

    cursor.execute("CREATE INDEX idx_lang_from ON dictionary_entries(lang_from)")
    cursor.execute("CREATE INDEX idx_lang_to ON dictionary_entries(lang_to)")

    conn.commit()
    conn.close()

    print("Database schema created...\n")


def ingest_dictionary(dict_filepath: str, db_filepath: str = "dictionary.db", lang_from="en", lang_to="de"):
    print(f"Building SQLite database from: {dict_filepath}")
    start_time = time.perf_counter()

    conn = sqlite3.connect(db_filepath)
    cursor = conn.cursor()

    lang_pattern = re.compile(r"\s([a-zA-Z]+)-([a-zA-Z]+)\s")

    total_lines = 0
    total_inserted = 0
    batch_data = []
    batch_size = 10000

    with open(dict_filepath, 'r', encoding='utf-8') as file:
        for line in file:
            total_lines += 1
            clean_line = line.strip()

            if not clean_line:
                continue

            if clean_line.startswith('#'):
                match = lang_pattern.search(clean_line)
                if match:
                    lang_from = match.group(1).lower()
                    lang_to = match.group(2).lower()
                continue

            clean_line = html.unescape(clean_line)
            parts = clean_line.split('\t')

            if len(parts) >= 2:
                word_from = parts[0].strip()
                word_to = parts[1].strip()
                word_type = parts[2].strip() if len(parts) > 2 and parts[2].strip() else None
                classification = parts[3].strip() if len(parts) > 3 and parts[3].strip() else None

                batch_data.append((
                    lang_from, lang_to, word_from, word_to, word_type, classification
                ))

                if len(batch_data) >= batch_size:
                    cursor.executemany("""
                        INSERT INTO dictionary_entries 
                        (lang_from, lang_to, word_from, word_to, word_type, classification)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, batch_data)
                    total_inserted += len(batch_data)
                    print(f"  Inserted {total_inserted:,} rows...")
                    batch_data = []

    # Insert remaining rows
    if batch_data:
        cursor.executemany("""
            INSERT INTO dictionary_entries 
            (lang_from, lang_to, word_from, word_to, word_type, classification)
            VALUES (?, ?, ?, ?, ?, ?)
        """, batch_data)
        total_inserted += len(batch_data)

    conn.commit()

    # Optimize the FTS index
    print("\nOptimizing FTS index...")
    cursor.execute("INSERT INTO dictionary_fts(dictionary_fts) VALUES('optimize')")
    conn.commit()

    conn.close()

    end_time = time.perf_counter()
    elapsed = end_time - start_time

    file_size_mb = os.path.getsize(db_filepath) / (1024 * 1024)

    print("\n" + "=" * 50)
    print("SQLITE DATABASE BUILD COMPLETE!")
    print(f"Total lines processed: {total_lines:,}")
    print(f"Total rows inserted:   {total_inserted:,}")
    print(f"Database file size:    {file_size_mb:.2f} MB")
    print(f"Time taken:            {elapsed:.2f} seconds")
    print("=" * 50)


if __name__ == "__main__":
    build_sqlite_database()
    ingest_dictionary("data/dictcc_de_en.txt", "dictionary.db", "de", "en")
    ingest_dictionary("data/dictcc_en_de.txt", "dictionary.db", "en", "de")
