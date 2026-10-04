import sqlite3

if __name__ == '__main__':
    conn = sqlite3.connect("c:/DEV/zack-zack-deutsch/_dict/dictionary_wal.db")
    cursor = conn.cursor()

    # Enable WAL mode
    cursor.execute("PRAGMA journal_mode=WAL;")
    print(cursor.fetchone()[0])  # Should print 'wal'

    conn.close()
