#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 16 16:03:20 2022

@author: bernhard
"""

import asyncore
from smtpd import SMTPServer
import urllib.parse
import requests
import os
import signal
import re


PIDFILE=os.environ["HOME"] + "/smtp_2_telegram.pid"
SHUTDOWN_PERFORMED = 0

LISTENADDR='localhost'
LISTENPORT=10025

BOTAPI="xxxxxxxxxx:yyyyyyyyyyyyyyyyyyyyyyyyyyyyyy"
CHATID="1234567"


def write_pid_file():
    try:
        pid=os.getpid()
        print(f"creating pid file: {PIDFILE} with pid={pid}")
        with open(PIDFILE, "w") as pidfile:
            print(pid, end=None, file=pidfile)
    except:
        pass


def remove_pid_file():
    try:
        print(f"deleting pid file: {PIDFILE}")
        if os.path.exists(PIDFILE):
            os.remove(PIDFILE)
    except:
        pass


def handle_signal (*ignore):
    global SHUTDOWN_PERFORMED
    print("caught TERM, exitting")
    if not SHUTDOWN_PERFORMED:
        asyncore.socket_map.clear()
        SHUTDOWN_PERFORMED = 1
        raise asyncore.ExitNow



def handle_haproxy_message(msg):
    # HAProxy alerts are configured from alerts@dbX.yyy.zzz
    # HAProxy has a terrible long Subject line and server down message
    # just making it a litte shorter
    if ("HAProxy" in msg):
        match = re.search(r'alerts@(db[1-9]).*?Server\s+([a-z0-9_]+)(?::\d+)?/(\S+) is (UP|DOWN)', msg, re.I+re.M+re.S)
        if match:
            msg=f"""HAProxy {match.group(1)}: {match.group(2)} backend {match.group(3)} is {match.group(4)}"""
    return msg



class EmlServer(SMTPServer):

    no = 0

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        # parse data and send it to telegram
        data = data.decode("utf-8")
        data = handle_haproxy_message(data)
        # write it to console or screen
        print(data)
        msg = urllib.parse.quote(data.encode("utf-8"))
        requests.post(f"https://api.telegram.org/bot{BOTAPI}/sendMessage?chat_id={CHATID}&text={msg}")



def run():

    signal.signal (signal.SIGTERM, handle_signal)

    write_pid_file()
    print(f"smtp2telegram listening on {LISTENADDR}:{LISTENPORT}")
    EmlServer((LISTENADDR, LISTENPORT), None)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        pass
    except asyncore.ExitNow:
        pass
    remove_pid_file()


if __name__ == '__main__':
    run()
