import sqlite3

DB_PATH = "dictionary.db"


def query_with_like():
    conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro&immutable=1", uri=True)

    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("=" * 60)
    print("LIKE Query Examples")
    print("=" * 60)

    # Example 1: Contains "apple" anywhere
    print("\n1. Search for entries containing 'apple':")
    cursor.execute("""
        SELECT word_from, word_to, word_type
        FROM dictionary_entries
        WHERE word_from LIKE '%apple%'
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"   {row['word_from']} → {row['word_to']}")

    # Example 2: Contains "Kugel" in German
    print("\n2. Search for entries containing 'Kugel' (German):")
    cursor.execute("""
        SELECT word_from, word_to, word_type
        FROM dictionary_entries
        WHERE word_to LIKE '%Kugel%'
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"   {row['word_from']} → {row['word_to']}")

    # Example 3: Case-insensitive search (ILIKE doesn't exist in SQLite, use LIKE with COLLATE)
    print("\n3. Case-insensitive search for 'bot' in classification:")
    cursor.execute("""
        SELECT word_from, word_to, classification
        FROM dictionary_entries
        WHERE classification LIKE '%bot%' COLLATE NOCASE
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"   {row['word_from']} → {row['word_to']} [{row['classification']}]")

    # Example 4: Starts with "app"
    print("\n4. Words starting with 'app':")
    cursor.execute("""
        SELECT word_from, word_to
        FROM dictionary_entries
        WHERE word_from LIKE 'app%'
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"   {row['word_from']} → {row['word_to']}")

    # Example 5: Ends with "tion"
    print("\n5. Words ending with 'tion':")
    cursor.execute("""
        SELECT word_from, word_to
        FROM dictionary_entries
        WHERE word_from LIKE '%tion'
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"   {row['word_from']} → {row['word_to']}")

    # Example 6
    print("\nExample 6")
    # FTS5 is much faster than LIKE for substring search
    cursor.execute("""
        SELECT e.word_from, e.word_to
        FROM dictionary_fts fts
        JOIN dictionary_entries e ON e.id = fts.rowid
        WHERE dictionary_fts MATCH 'apple*'
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"   {row['word_from']} → {row['word_to']}")

    conn.close()


if __name__ == "__main__":
    query_with_like()
