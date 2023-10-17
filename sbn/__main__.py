# This file is placed in the Public Domain.
#
# pylint: disable=C0412,C0115,C0116,W0212,R0903,C0207,C0413,W0611
# pylint: disable=C0411,E0402,E0611,C2801


"runtime"


import getpass
import os
import pwd
import readline
import sys
import termios
import time
import threading
import traceback


from .methods import parse
from .handler import Broker, Cfg, Client, Errors, Event, command, debug, scan
from .storage import Storage
from .utility import daemon, mods, privileges


from . import handler
from . import modules


NAME = __file__.split(os.sep)[-2]
Storage.workdir = os.path.expanduser(f"~/.{NAME}")
PIDFILE = os.path.join(Storage.workdir, "sbn.pid")
USER = getpass.getuser()


class CLI(Client):

    def announce(self, txt):
        pass

    def raw(self, txt):
        print(txt)
        sys.stdout.flush()


class Console(CLI):

    def dispatch(self, evt):
        parse(evt)
        command(evt)
        evt.wait()

    def poll(self) -> Event:
        return self.event(input("> "))


def wrap(func) -> None:
    old = None
    try:
        old = termios.tcgetattr(sys.stdin.fileno())
    except termios.error:
        pass
    try:
        func()
    except (EOFError, KeyboardInterrupt):
        print("")
        sys.stdout.flush()
    finally:
        if old:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
    Errors.show()


def main():
    parse(Cfg, " ".join(sys.argv[1:]))
    Cfg.mod = ",".join(modules.__dir__())
    if "d" in Cfg.opts:
        daemon()
    if "d" in Cfg.opts or "s" in Cfg.opts:
        privileges(getpass.getuser())
        debug(f"dropped to {USER} privileges")
        scan(modules, Cfg.mod, True)
        while 1:
            time.sleep(1.0)
    elif "c" in Cfg.opts:
        dtime = time.ctime(time.time()).replace("  ", " ")
        debug(f"{NAME.upper()} started at {dtime} {Cfg.opts.upper()} {Cfg.mod.upper()}")
        scan(modules, Cfg.mod, "i" not in Cfg.opts, True)
        csl = Console()
        csl.start()
        csl.forever()
    else:
        cli = CLI()
        scan(modules, Cfg.mod)
        evt = cli.event(Cfg.otxt)
        parse(evt)
        command(evt)
        evt.wait()


def wrapped():
    wrap(main)


if __name__ == "__main__":
    wrapped()
