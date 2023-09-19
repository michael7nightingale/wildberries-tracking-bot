import sys
from logging import Logger, Formatter, FileHandler, DEBUG
from rich.console import Console
import os


# file logging to store all the time
logger = Logger(__name__)
logger.setLevel(DEBUG)

handler = FileHandler(filename=os.getcwd() + '/data/wb.log')
handler.setFormatter(
    Formatter("%(asctime)s | %(levelname)s | %(message)s")
)

logger.addHandler(handler)


# stream logger (stdout) to comfort run view
console = Console()


def log_twice(lvl: str, msg: str) -> None:
    """Log both from logger and console. Console is for a comfort view, log is to store"""
    match lvl.upper():  # Python >= 3.10
        case "INFO":
            console.print(f"[green] {msg}")
            logger.info(msg)
        case "DEBUG":
            console.print(f"[green] {msg}")
            logger.info(msg)
        case "ERROR":
            console.print(f"[red] {msg}")
            logger.error(msg)
        case "WARN":
            console.print(f"[yellow] {msg}")
            logger.warn(msg)
        case "CRITICAL":
            console.print(f"[red]!!!!!!!!!!!!!{msg}!!!!!!!!!!!!!!!!!")
            logger.critical("!!!!!!!!!!!!!{msg}!!!!!!!!!!!!!!!!!")
            sys.exit()
        case _:
            print(lvl.upper())
            raise AssertionError("There is no such a log level")
