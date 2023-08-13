import sys

from client import Client


def main(argv) -> int:
    if len(argv) != 2:
        print(f"Usage: {argv[0]} <channel_name>")
        return 1
    client = Client(username=argv[1])
    client.listen()
    print(1)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
