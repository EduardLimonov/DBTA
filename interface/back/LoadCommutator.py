from __future__ import annotations
import time
from threading import Thread


class LoadCommutator:
    timeout = 0.09

    def __init__(self, func: callable):
        self.func = func
        self.make_ts = True
        Thread(target=self.ts).start()

    def get_message(self, msg):
        self.func(msg)

    def ts(self):
        from core.app_runner.AppRunner import AppRunner
        while self.make_ts:
            time.sleep(LoadCommutator.timeout)
            AppRunner.repaint_app()
        print('done')
