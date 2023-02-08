from argparse import ArgumentParser
from urllib3.util.url import Url

import os.path
import random
import sqlite3
import requests


class StoryLineTooter:
    def __init__(self, db_dir: str, db_name: str, hostname: str, token: str):
        self.connection = sqlite3.connect(os.path.join(db_dir, db_name))
        self.endpoint = Url(scheme="https",
                            host=hostname,
                            path="/api/v1/statuses").url
        self.headers = {"Authorization": "Bearer " + token}

    def get_story_line(self):
        c = self.connection.cursor()
        c.execute("SELECT MAX(lines.id) FROM lines")
        max_id = c.fetchone()[0]
        # Sqlite's RANDOM() doesn't have a seed, use Python's random.SystemRandom
        idx = random.SystemRandom().randrange(1, max_id + 1)
        c.execute(f"SELECT lines.line FROM lines WHERE id={idx}")
        return c.fetchone()[0]

    def toot(self) -> int:
        text = self.get_story_line()
        status = '\n\n'.join([text, "#hachybots"])
        data = {
            "status": status,
            "visibility": "public"
        }
        response = requests.post(
            url=self.endpoint, data=data, headers=self.headers
        )
        response.raise_for_status()
        return response.status_code


def process_commandline_arguments():
    parser = ArgumentParser()
    parser.add_argument("token", help="server access token")
    return parser.parse_args()


def main():
    args = process_commandline_arguments()
    tooter = StoryLineTooter(
        db_dir="db",
        db_name="bartleby.db",
        hostname="hachyderm.io",
        # this should be secret!
        token=args.token,
    )

    status_code = tooter.toot()
    print(f"Toot of line completed with status {status_code}")


if __name__ == "__main__":
    main()

