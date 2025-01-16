from os.path import basename
from enum import IntEnum
from datetime import datetime
from inspect import getframeinfo, stack

class LogLevel(IntEnum):
  ERROR     = 0
  WARNING   = 1
  INFO      = 2
  DEBUG     = 3
  TRACE     = 4

def start_logger(level):
    global CURRENT_LOG_LEVEL
    CURRENT_LOG_LEVEL = level

def LOG_ERROR(message : str):
  log(LogLevel.ERROR, message)

def LOG_WARNING(message : str):
  log(LogLevel.WARNING, message)

def LOG_INFO(message : str):
  log(LogLevel.INFO, message)

def LOG_DEBUG(message : str):
  log(LogLevel.DEBUG, message)

def LOG_TRACE(message : str):
  log(LogLevel.TRACE, message)

def printLevel(level : LogLevel) -> str:
    if level == LogLevel.ERROR:
        return "[\033[91mE\033[00m]"
    elif level == LogLevel.WARNING:
        return "[\033[93mW\033[00m]"
    elif level == LogLevel.INFO:
        return "[\033[92mI\033[00m]"
    elif level == LogLevel.DEBUG:
        return "[\033[96mD\033[00m]"
    elif level == LogLevel.TRACE:
        return "[\033[94mT\033[00m]"

def log(level: LogLevel, message : str) -> None:
    if level.value <= CURRENT_LOG_LEVEL.value:
        caller = getframeinfo(stack()[2][0])
        print(f"{datetime.now()} {printLevel(level)} {basename(caller.filename)}:{caller.lineno}: {message}")
