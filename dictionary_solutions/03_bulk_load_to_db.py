import html
import re
import sys
import time

from sqlalchemy import create_engine
from sqlalchemy import insert
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

from dictionary_solutions.db_models import Base
from dictionary_solutions.db_models import DictionaryEntry

DATABASE_URL = "..."

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(bind=engine)


def init_db():
    with engine.begin() as conn:
        # Enable the pg_trgm extension
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))

    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully!")


def ingest_dictionary(filepath: str, chunk_size: int = 10000, start_from_line: int = 0):
    print(f"Starting ingestion of: {filepath}")
    print(f"Chunk size: {chunk_size} rows per batch")
    print(f"Resuming from line: {start_from_line}\n")

    start_time = time.perf_counter()

    lang_from = "de"
    lang_to = "en"
    lang_pattern = re.compile(r"\s([a-zA-Z]+)-([a-zA-Z]+)\s")

    total_lines_processed = 0
    total_rows_inserted = 0
    chunk_data = []

    current_line_num = 0
    chunk_start_line = 0

    try:
        with open(filepath, 'r', encoding='utf-8') as file:
            for line in file:
                current_line_num += 1

                # Skip lines we have already processed in previous runs
                if current_line_num < start_from_line:
                    continue

                clean_line = line.strip()

                if not clean_line:
                    continue

                if clean_line.startswith('#'):
                    match = lang_pattern.search(clean_line)
                    if match:
                        lang_from = match.group(1).lower()
                        lang_to = match.group(2).lower()
                    continue

                total_lines_processed += 1

                clean_line = html.unescape(clean_line)
                parts = clean_line.split('\t')

                if len(parts) >= 2:
                    if not chunk_data:
                        chunk_start_line = current_line_num

                    word_from = parts[0].strip()
                    word_to = parts[1].strip()
                    word_type = parts[2].strip() if len(parts) > 2 and parts[2].strip() else None
                    classification = parts[3].strip() if len(parts) > 3 and parts[3].strip() else None

                    chunk_data.append({
                        "lang_from": lang_from,
                        "lang_to": lang_to,
                        "word_from": word_from,
                        "word_to": word_to,
                        "word_type": word_type,
                        "classification": classification
                    })

                    if len(chunk_data) >= chunk_size:
                        _execute_chunk(chunk_data)
                        total_rows_inserted += len(chunk_data)
                        print(
                            f"  Progress: {total_rows_inserted:,} rows inserted... (Current file line: {current_line_num})")
                        chunk_data = []

            if chunk_data:
                _execute_chunk(chunk_data)
                total_rows_inserted += len(chunk_data)
                print(f"  Progress: {total_rows_inserted:,} rows inserted (Final batch).")

    except OperationalError as e:
        print("\n" + "=" * 60)
        print("DATABASE CONNECTION ERROR (OperationalError)!")
        print(f"Error details: {e.orig}")
        print("-" * 60)
        print(f"The script stopped at file line: {current_line_num}")
        print(f"The failed chunk started at line: {chunk_start_line}")
        print("\nHOW TO RESUME:")
        print(f"1. Fix the database connection issue.")
        print(f"2. Open ingest.py and change RESUME_FROM_LINE to {chunk_start_line}")
        print(f"3. Run the script again.")
        print("=" * 60)
        sys.exit(1)

    except Exception as e:
        print(f"\nAn unexpected error occurred at line {current_line_num}: {e}")
        sys.exit(1)

    end_time = time.perf_counter()
    elapsed = end_time - start_time

    print("-" * 40)
    print("INGESTION COMPLETE!")
    print(f"Total lines processed: {total_lines_processed:,}")
    print(f"Total rows inserted:   {total_rows_inserted:,}")
    print(f"Time taken:            {elapsed:.2f} seconds")


def _execute_chunk(chunk_data: list[dict]):
    with SessionLocal() as session:
        stmt = insert(DictionaryEntry).values(chunk_data)
        session.execute(stmt)
        session.commit()


if __name__ == '__main__':
    # init_db()

    FILE_1_PATH = "data/dictcc_de_en.txt"
    # FILE_2_PATH = "data/dictcc_en_de.txt"
    RESUME_FROM_LINE = 0

    ingest_dictionary(FILE_1_PATH, chunk_size=10000, start_from_line=RESUME_FROM_LINE)
