#!/usr/bin/env python

# Copyright 2018 Techliu
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import owhash
import queue
import time
import threading


UPDATE_INTERVAL_SEC = 10
CACHE_DURATION_SEC = 120


class HashEntry(object):
    def __init__(self, hash, time_sec):
        self.hash = hash
        self.time_sec = time_sec


class IndexTimePair(object):
    def __init__(self, index, time_sec):
        self.index = index
        self.time_sec = time_sec


class TimeUserSet(object):
    def __init__(self):
        self.valid_user_ids = []
        self.user_hashes = {}

        t = threading.Thread(target=self.update_user_hash, args=(UPDATE_INTERVAL_SEC,))
        t.start()

    def update_user_hash(self, interval):
        now_sec = int(time.time())
        last_sec = now_sec - CACHE_DURATION_SEC
        hash2remove = queue.Queue(maxsize=CACHE_DURATION_SEC*3*len(self.valid_user_ids))
        last_sec2remove = now_sec
        id_hash = owhash.TimeHash()
        while True:
            now_sec = int(time.time())
            remove2sec = now_sec - CACHE_DURATION_SEC

            if remove2sec > last_sec2remove:
                while last_sec2remove + 1 < remove2sec:
                    entry = hash2remove.get()
                    last_sec2remove = entry.time_sec
                    del self.user_hashes[entry.hash]

            for last_sec in range(last_sec, now_sec+CACHE_DURATION_SEC):
                for idx, uid in enumerate(self.valid_user_ids):
                    user_hash = id_hash.hash(uid.bytes, last_sec)
                    hash2remove.put(HashEntry(user_hash.hex(), last_sec))
                    self.user_hashes[user_hash.hex()] = IndexTimePair(idx, last_sec)
            last_sec += 1
            time.sleep(interval)
        pass

    def add_user(self, user):
        self.valid_user_ids.append(user.id)
        return

    def get_user(self, user_hash):
        try:
            pair = self.user_hashes[user_hash.hex()]
            return self.valid_user_ids[pair.index], pair.time_sec
        except KeyError:
            return None, None
