#!/usr/bin/env python3

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from kick_chat.client import Client


def main(argv=sys.argv) -> int:
    if len(argv) != 2:
        print("Usage: kick-chat <channel_name>")
        return 1
    client = Client(username=argv[1])
    client.listen()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
