#!/usr/bin/python3
# -*- coding: utf-8 -*-

# @file timer.py
# @brief
# @author QRS
# @blog qrsforever.gitee.io
# @version 1.0
# @date 2023-03-16 11:27


from threading import Timer


class TimerCycle(Timer): 
    def run(self):
        self.finished.wait(self.interval)
        while not self.finished.is_set():
            self.function(*self.args, **self.kwargs)
            self.finished.wait(self.interval)


if __name__ == "__main__":
    import time

    def _echo(arg):
        print(arg)

    t = TimerCycle(2.0, _echo, args=(8,))
    t.start()
    time.sleep(8)
    t.cancel()
