import threading

import time


def func1():
    t = threading.Thread(target=func2)
    t.start()


def func2():
    while True:
        time.sleep(1)
        print('+++')

t1 = threading.Thread(target=func1, name='subthread1')
# t2 = threading.Thread(target=func2, name='subthread2')

t1.start()

t1.join()

print('结束！！！')
