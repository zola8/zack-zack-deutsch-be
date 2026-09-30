import html
import re
import time


def read_and_parse_dictionary(filepath):
    print(f"Starting to read: {filepath}")
    start_time = time.perf_counter()

    total_valid_lines = 0
    parsed_lines = 0
    language_pair = None

    lang_pattern = re.compile(r"\s(\w+)-(\w+)\s")

    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            clean_line = line.strip()

            if not clean_line:
                continue

            if clean_line.startswith('#'):
                match = lang_pattern.search(clean_line)
                if match and not language_pair:
                    language_pair = (match.group(1), match.group(2))
                    print(f"Found Language Pair: {language_pair[0]} -> {language_pair[1]}")
                continue

            total_valid_lines += 1

            clean_line = html.unescape(clean_line)

            parts = clean_line.split('\t')

            if len(parts) >= 2:
                parsed_lines += 1

                word1 = parts[0]
                word2 = parts[1]
                word_type = parts[2] if len(parts) > 2 else None
                classification = parts[3] if len(parts) > 3 else None

                print(f"Sample: [{word1}] | [{word2}] | Type: [{word_type}] | Class: [{classification}]")

    end_time = time.perf_counter()

    print("-" * 30)
    print(f"Finished reading file.")
    print(f"Total valid lines: {total_valid_lines}")
    print(f"Successfully parsed entries: {parsed_lines}")
    if language_pair:
        print(f"Dictionary Languages: {language_pair[0]} to {language_pair[1]}")
    else:
        print("Warning: Language pair not found in comments!")
    print(f"Time taken: {end_time - start_time:.4f} seconds")


if __name__ == "__main__":
    FILE_1_PATH = "data/dictcc_de_en.txt"
    FILE_2_PATH = "data/dictcc_en_de.txt"

    read_and_parse_dictionary(FILE_2_PATH)
