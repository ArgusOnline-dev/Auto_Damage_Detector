#!/usr/bin/env python3
"""Stop the frontend development server without restarting."""

from run_frontend import stop_frontend


def main() -> int:
    if stop_frontend():
        return 0

    print("[INFO] Frontend was not running")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

