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
        "--install-startup",
        action="store_true",
        help="Register application to run on Windows startup.",
    )
    parser.add_argument(
        "--uninstall-startup",
        action="store_true",
        help="Remove application from Windows startup.",
    )
    parser.add_argument(
        "--no-tray",
        action="store_true",
        help="Disable system tray icon and run as a pure CLI/console process.",
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

    if args.install_startup:
        from .startup import register_startup

        if register_startup():
            print("Successfully registered VirtualBox Discord RPC for Windows startup.")
            sys.exit(0)
        else:
            print("Failed to register Windows startup entry.", file=sys.stderr)
            sys.exit(1)

    if args.uninstall_startup:
        from .startup import unregister_startup

        if unregister_startup():
            print("Successfully removed VirtualBox Discord RPC from Windows startup.")
            sys.exit(0)
        else:
            print("Failed to remove Windows startup entry.", file=sys.stderr)
            sys.exit(1)

    service = VirtualBoxRPC(config)

    if args.once:
        payload = service.sync_once()
        if payload:
            print(f"Current state: {payload.get('details')} | {payload.get('state')}")
        else:
            print("VirtualBox is not currently active.")
        sys.exit(0)

    if not args.no_tray:
        try:
            from .tray import is_tray_supported, run_with_tray

            if is_tray_supported():
                run_with_tray(service)
                sys.exit(0)
        except Exception as exc:
            logging.getLogger("virtualbox_rpc").debug("System tray initialization skipped: %s", exc)

    service.run()


if __name__ == "__main__":
    main()
