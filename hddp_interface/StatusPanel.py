import tkinter as tk
import threading
import datetime
from math import ceil
import time
from constants import DEBUG_MODE


class StatusPanel(tk.Frame):
    def __init__(self, master, app, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.app = app
        self.config(bg='#dddddd', height=20)
        self.stopFlagVar = tk.BooleanVar(self)
        self.stopFlagVar.set(False)

        self.progressVar = tk.IntVar(self)
        self.progressVar.set(0)
        self.statusVar = tk.StringVar(self)
        self.statusVar.set('...')

        self.statusText = tk.Label(self, text='test', fg='#0000dd', bg='#dddddd',
                                   font='Helvetica 10 bold', textvariable=self.statusVar)
        self.statusText.pack(side=tk.LEFT, ipadx=5)

        self.stopButton = tk.Button(self, text='Stop', command=self.stop_button_func)
        self.stopButton.pack(side=tk.RIGHT, padx=5)
        self.stopButton['state'] = tk.DISABLED

        self.timeRemainingVar = tk.StringVar(self)
        self.timeRemainingVar.set('...')
        self.timeRemainingLabel = tk.Label(self, textvariable=self.timeRemainingVar, bg='#dddddd')
        self.timeRemainingLabel.pack(side=tk.RIGHT)

        self.timeCounter = TimeCounter(self, self.timeRemainingVar)

        self.progressBar = tk.ttk.Progressbar(self, orient=tk.HORIZONTAL, length=100, mode='determinate')
        self.progressBar.pack(fill=tk.X, expand=1, padx=5)
        self.progressBar['variable'] = self.progressVar

    def init_progress_bar(self, max_value):
        self.progressBar['maximum'] = max_value
        self.progressVar.set(0)

    def inc_progress(self, val=1):
        self.progressVar.set(self.progressVar.get() + val)

    def disable_stop_button(self):
        self.stopButton['state'] = tk.DISABLED

    def enable_stop_button(self):
        self.stopFlagVar.set(False)
        self.stopButton['state'] = tk.NORMAL

    def stop_button_func(self):
        self.stopFlagVar.set(True)
        self.disable_stop_button()

    def get_stop_status(self):
        return self.stopFlagVar.get()

    def set_status(self, text):
        self.statusVar.set(text)


class TimeCounter:
    def __init__(self, master, time_remaining_var):
        self.master = master
        self.counter = 0
        self.stopFlag = False
        self.thread = None
        self.lastProgressValue = 0
        self.secondsRemaining = 0
        self.timeRemainingVar = time_remaining_var
        self.maxProgressVal = 0
        self.progressVar = None

    def reset(self):
        self.counter = 0
        self.stopFlag = False
        self.secondsRemaining = 0

    def start(self, max_progress_val, progress_var, stop_status_func):
        self.maxProgressVal = max_progress_val
        self.progressVar = progress_var
        self.stop_status_func = stop_status_func
        self.secondsRemaining = 0
        self.counter = 0
        self.lastProgressValue = 0
        self.stopFlag = False
        # print('start timer')
        self.master.timeRemainingVar.set('Calculating...')
        self.thread = threading.Thread(target=self.action)
        self.thread.start()
        if DEBUG_MODE:
            print("TEST: timer counter started")

    def action(self):
        # while not self.stopFlag:
        while not self.stop_status_func() and not self.stopFlag:
            # print('counter = %d, secRem = %d, lastProgr = %d' % (self.counter, self.secondsRemaining,
            #                                                      self.lastProgressValue))
            if self.counter < 3:
                if self.secondsRemaining > 0:
                    self.secondsRemaining -= 1
                else:
                    pass
            else:
                self.counter = 0
                cur_val = self.progressVar.get()
                if self.lastProgressValue > 0:
                    dif = cur_val - self.lastProgressValue
                    sec = ceil((self.maxProgressVal - cur_val) * 5 / dif)
                    self.secondsRemaining = sec

                self.lastProgressValue = self.progressVar.get()

            if self.secondsRemaining > 0:
                self.timeRemainingVar.set(str(datetime.timedelta(seconds=self.secondsRemaining))[-5:])
            self.counter += 1
            time.sleep(1)
            # print(self.counter)

        if DEBUG_MODE:
            print("TEST: time counter stopped")

    def stop(self):
        self.stopFlag = True
