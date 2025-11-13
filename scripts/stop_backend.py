#!/usr/bin/env python3
"""Stop the backend server without restarting."""

from run_backend import stop_backend


def main() -> int:
    if stop_backend():
        return 0

    print("[INFO] Backend was not running")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

