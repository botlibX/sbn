# This file is placed in the Public Domain.
#
# pylint: disable=C0116


"utilities"


import getpass
import os
import pathlib
import pwd
import sys
import termios


def cdir(pth) -> None:
    if not pth.endswith(os.sep):
        pth = os.path.dirname(pth)
    pth = pathlib.Path(pth)
    os.makedirs(pth, exist_ok=True)


def daemon():
    pid = os.fork()
    if pid != 0:
        os._exit(0)
    os.setsid()
    #pid2 = os.fork()
    #if pid2 != 0:
    #    os._exit(0)
    with open('/dev/null', 'r', encoding="utf-8") as sis:
        os.dup2(sis.fileno(), sys.stdin.fileno())
    with open('/dev/null', 'a+', encoding="utf-8") as sos:
        os.dup2(sos.fileno(), sys.stdout.fileno())
    with open('/dev/null', 'a+', encoding="utf-8") as ses:
        os.dup2(ses.fileno(), sys.stderr.fileno())
    os.umask(0)
    os.chdir("/")
    if os.path.exists(PIDFILE):
        os.unlink(PIDFILE)
    with open(PIDFILE, "w") as fd:
        fd.write(str(os.getpid()))



def laps(seconds, short=True) -> str:
    txt = ""
    nsec = float(seconds)
    if nsec < 1:
        return f"{nsec:.2f}s"
    year = 365*24*60*60
    week = 7*24*60*60
    nday = 24*60*60
    hour = 60*60
    minute = 60
    years = int(nsec/year)
    nsec -= years*year
    weeks = int(nsec/week)
    nsec -= weeks*week
    nrdays = int(nsec/nday)
    nsec -= nrdays*nday
    hours = int(nsec/hour)
    nsec -= hours*hour
    minutes = int(nsec/minute)
    nsec -= int(minute*minutes)
    sec = int(nsec)
    if years:
        txt += f"{years}y"
    if weeks:
        nrdays += weeks * 7
    if nrdays:
        txt += f"{nrdays}d"
    if nrdays and short and txt:
        return txt.strip()
    if hours:
        txt += f"{hours}h"
    if minutes:
        txt += f"{minutes}m"
    if sec:
        txt += f"{sec}s"
    txt = txt.strip()
    return txt


def mods(path):
    res = []
    for fnm in os.listdir(path):
        if fnm.endswith("~"):
            continue
        if not fnm.endswith(".py"):
            continue
        if fnm in ["__main__.py", "__init__.py"]:
            continue
        res.append(fnm[:-3])
    return sorted(res)


def privileges(username):
    #if os.getuid() != 0:
    #    return
    pwnam = pwd.getpwnam(username)
    os.setgid(pwnam.pw_gid)
    os.setuid(pwnam.pw_uid)
    #os.setgroups([])


def spl(txt) -> []:
    try:
        res = txt.split(',')
    except (TypeError, ValueError):
        res = txt
    return [x for x in res if x]


def strip(pth) -> str:
    return os.sep.join(pth.split(os.sep)[-4:])
