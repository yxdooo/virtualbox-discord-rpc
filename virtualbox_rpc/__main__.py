import argparse
import logging
import sys
from pathlib import Path

from . import __version__
from .client import VirtualBoxRPC
from .config import Config


def setup_logging(level_name: str, log_file: str = None) -> None:
    """Configures structured standard logging for console and optional file output."""
    level = getattr(logging, level_name.upper(), logging.INFO)
    handlers = [logging.StreamHandler(sys.stdout)]

    if log_file:
        try:
            handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
        except Exception:
            pass

    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="virtualbox-rpc",
        description="Discord Rich Presence client for Oracle VM VirtualBox.",
    )
    parser.add_argument(
        "-c",
        "--config",
        type=Path,
        default=None,
        help="Path to custom JSON configuration file.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging output.",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run a single sync check and exit.",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args()

    config = Config.load(args.config)
    log_level = "DEBUG" if args.debug else config.log_level
    setup_logging(log_level, config.log_file)

    service = VirtualBoxRPC(config)

    if args.once:
        service._sync_presence()
        sys.exit(0)

    service.run()


if __name__ == "__main__":
    main()
