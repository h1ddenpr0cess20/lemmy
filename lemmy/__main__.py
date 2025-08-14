from __future__ import annotations

# Route module execution to the CLI so flags work with `python -m lemmy`.
from .cli import main as cli_main


def main() -> None:
    cli_main()


if __name__ == "__main__":
    main()
