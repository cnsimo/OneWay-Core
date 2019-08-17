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

import queue

BUFFER_SIZE = 16


class Way(object):
    '''
        以outbound和inbound为主体对象产生的方法：
            outbound_input/outbound_output: 对outbound的输入输出队列
            inbound_input/inbound_output： 对inbound的输入输出队列
        bound就相当于一道门，都有出和入
    '''
    def __init__(self):
        self.input = queue.Queue(maxsize=BUFFER_SIZE)
        self.output = queue.Queue(maxsize=BUFFER_SIZE)

    def outbound_input(self):
        return self.input

    def outbound_output(self):
        return self.output

    def inbound_input(self):
        return self.input

    def inbound_output(self):
        return self.output
