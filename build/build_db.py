#!/usr/bin/env python3

from argparse import ArgumentParser
import os.path
import re
import sqlite3
import sys
import nltk
# required for sentence tokenization
nltk.download("punkt")


def connect(db_path: str) -> sqlite3.Connection:
    """ Connect to the SQLite DB. """
    return sqlite3.connect(db_path)
    

def clean_text(text_path: str) -> str:
    """ Remove problematic characters from text. """
    with open(text_path) as r:
        text = r.read()
        # smart quotes confuse the tokenizer
        text = re.sub('[“”]', '"', text)
        # replace random whitespace with a single space
        return re.sub("\s+", " ", text)


def tokenize_story(text: str) -> list[tuple[int, str]]:
    """ Tokenize text into sentences, returns tuples of indices and lines."""
    tokens = nltk.sent_tokenize(text)
    return [(idx, elem) for idx, elem in enumerate(tokens)]


def create_lines_table(connection: sqlite3.Connection) -> None:
    """" Create the table containing the story. """
    command = """ CREATE TABLE IF NOT EXISTS lines (
                      id INTEGER PRIMARY KEY,
                      line TEXT NOT NULL
                  );"""
    c = connection.cursor()
    c.execute(command)


def process_command_arguments():
    parser = ArgumentParser()
    parser.add_argument("story", help="name of story")
    parser.add_argument(
        "-d", "--db-dir",
        default="db",
        help="SQLite DB directory (default=./db)"
    )
    parser.add_argument(
        "-t", "--text-dir",
        default="text",
        help="story text file directory (default=./text)"
    )
    args = parser.parse_args()
    db_path = os.path.join(args.db_dir, f"{args.story}.db")
    text_path = os.path.join(args.text_dir, f"{args.story}.txt")
    if not os.path.exists(text_path):
        print(
            "\033[91m {}\033[00m".format(
                f"ERROR: "
                f"File {os.path.abspath(args.text_dir)}/{args.story}.txt "
                "does not exist"
            ),
            file=sys.stderr)
        exit(1)
    return db_path, text_path


def main(db: str, text: str):
    try:
        conn = connect(db)
        create_lines_table(conn)
        story = clean_text(text)
        data = tokenize_story(story)
        conn.executemany("""
            INSERT INTO lines(id, line) VALUES (?,?)
                ON CONFLICT(id) DO UPDATE set line=excluded.line
            """, data)
        conn.commit()
    except sqlite3.Error as e:
        print(e)
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    db_path, text_path = process_command_arguments()
    main(db_path, text_path)
