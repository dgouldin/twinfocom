#!/usr/bin/env python
import anyjson
import atexit
import hashlib
import multiprocessing
import os
import urllib
import subprocess
import sys

def twitter_stream(username, password, handler, **kwargs):
    qs = urllib.urlencode(kwargs)
    pipe_path = '/tmp/twitter_stream_%s' % hashlib.md5(qs).hexdigest()
    if not os.path.exists(pipe_path):
        os.mkfifo(pipe_path)

    current_path = os.path.dirname(
        os.path.abspath(sys.modules[__name__].__file__))
    process = multiprocessing.Process(target=subprocess.call, args=([
        os.path.join(current_path, 'twitter_stream_create.sh'),
        pipe_path,
        username,
        password,
        qs,
    ],))
    process.start()

    def at_exit():
        print 'terminating'
        if process.is_alive():
            process.terminate()
    atexit.register(at_exit)

    while True:
        with open(pipe_path, 'r') as pipe:
            while True:
                last_line = pipe.readline()
                if last_line == '':
                    break
                elif last_line == '\n':
                    continue

                try:
                    tweet = anyjson.deserialize(last_line)
                except ValueError:
                    print 'Error decoding tweet: "%s"' % last_line
                else:
                    print 'Received tweet'
                    handler(tweet)

