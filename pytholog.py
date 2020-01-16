#!/usr/bin/python3.6

import os
import re
import time
import queue
import threading
from pathlib import Path
from dateutil.parser import parse
from storages import StorageSqlite

# Regular expression for the Unix log format (like 'Dec 8 23:11:01').
# Also, it matches the Apache log format (like '24/Nov/2019:23:11:01').
# Assumption is made that the date and time are in the beginning of the log.
log_pats = r'(?P<datestamp>(^[a-zA-Z]{3}\s{1,2}\d{1,2})|'\
           r'(^\d{2}/[a-zA-Z]{3}/\d{4}))(\s|:)'\
           r'(?P<timestamp>\d{2}:\d{2}:\d{2}) (?P<msg>.*$)'
log_pat = re.compile(log_pats)

LOCATION = '/var/log/'
DB_NAME = '/opt/logs2019.db'
SCHEMA = '''create table if not exists logs
            (id INTEGER PRIMARY KEY, timestamp TEXT, msg TEXT,
            logfile TEXT)'''
query_insert = 'INSERT into logs (timestamp, msg, logfile) values (?, ?, ?)'


def convert_time(dstamp, tstamp):
    """Adjust date and time to YYYY-MM-DD HH:mm:ss format."""
    return parse('{} {}'.format(dstamp, tstamp), fuzzy=True)


def normalize(lines):
    """Return tuples of normalized fields from logs."""
    groups = ((log_pat.match(line), filename) for line, filename in lines)
    tuples = ((str(convert_time(g.group('datestamp'), g.group('timestamp'))),
               g.group('msg'), filename) for g, filename in groups if g)
    return tuples


def tail_file(src):
    """Generate constantly lines from the log, check if the file is rotated."""
    current = open(src, 'r')
    curino = os.fstat(current.fileno()).st_ino
    current.seek(0, 2)
    while True:
        while True:
            line = current.readline().rstrip()
            if not line:
                break
            yield line, src

        try:
            if os.stat(src).st_ino != curino:
                new = open(src, 'r')
                current.close()
                current = new
                curino = os.fstat(current.fileno()).st_ino
                continue
        except IOError:
            pass
        time.sleep(1)


def gen_cat(sources):
    """Concatenate one source after another."""
    for src in sources:
        yield from src


def sendto_queue(source, thequeue):
    """Send log lines to the shared queue."""
    for line in source:
        thequeue.put(line)
    thequeue.put(StopIteration)


def genfrom_queue(thequeue):
    """Generate lines received on the shared queue."""
    while True:
        line = thequeue.get()
        if line is StopIteration:
            break
        yield line


def multiplex(sources):
    """Aggregate logs from multiple sources on the per-thread basis."""
    thequeue = queue.Queue()
    consumers = []
    for src in sources:
        t = threading.Thread(target=sendto_queue, args=(src, thequeue))
        t.start()
        consumers.append(genfrom_queue(thequeue))
    return gen_cat(consumers)


def write_logs(log):
    """Send log lines to the database object."""
    db = StorageSqlite(DB_NAME, SCHEMA)
    db.write(query_insert, log)
    db.close()


if __name__ == '__main__':
    res = multiplex([tail_file(str(f)) for f in Path(LOCATION).rglob('*.log')])

    for item in normalize(res):
        write_logs(item)
