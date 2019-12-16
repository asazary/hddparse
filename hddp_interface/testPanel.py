import tkinter as tk
import threading
import time

class TestPanel(tk.Frame):
    def __init__(self, master, app, *args, **kwargs):
        tk.Frame.__init__(self)
        self.app = app

        self.testButton1 = tk.Button(self, text='show search results',
                                     command=self.test_search_test_results)
        self.testButton1.pack(side=tk.LEFT)

        self.showOneRecordButton = tk.Button(self, text='show one', command=self.show_one_record)
        self.showOneRecordButton.pack(side=tk.LEFT)

        self.startTimerButton = tk.Button(self, text='start timer', command=self.start_timer)
        self.startTimerButton.pack(side=tk.LEFT, padx=10)

        self.stopTimerButton = tk.Button(self, text='stop timer', command=self.stop_timer)
        self.stopTimerButton.pack(side=tk.LEFT, padx=5)

        self.startTimerTestButton = tk.Button(self, text='start test', command=self.start_timer_test)
        self.startTimerTestButton.pack(side=tk.LEFT, padx=5)

        self.resizeScrolledFrameButton = tk.Button(self, text='resize scr frame', command=self.resize_scrolled_frame)
        self.resizeScrolledFrameButton.pack(side=tk.LEFT, padx=5)


    def test_search_f(self):
        self.app.nf.test_search()

    def test_search_test_results(self):
        for item in self.app.simpleCards.arr:
            print(item.name + ' ' + item.age + ' ' + item.type)

    def show_one_record(self, num=1):
        if num < self.app.userCards.size:
            #rec = self.app.userCards[num]
            #print(rec.uid, rec.firstName, rec.secondName)
            #print(rec.age, rec.zodiac, rec.hd_type, rec.profile)
            #print(rec.bio_physical, rec.bio_intellectual, rec.bio_emotional)
            self.app.userCards[num].test_print()

    def start_timer(self):
        self.counter = 0
        self.timerStopFlag = False
        self.thread = threading.Thread(target=self.timer_action)
        self.thread.start()

    def timer_action(self):
        while not self.timerStopFlag:
            self.counter += 1
            print(self.counter)
            time.sleep(1)
        print('timer stopped')

    def stop_timer(self):
        self.timerStopFlag = True

    def start_timer_test(self):
        self.counter = 120
        self.app.statusPanel.init_progress_bar(max_value=self.counter)

        self.progrStopFlag = False
        self.app.statusPanel.timeCounter.start(max_progress_val=self.counter,
                                               progress_var=self.app.statusPanel.progressVar)
        threading.Thread(target=self.inc_progr).start()

    def inc_progr(self):
        while not self.progrStopFlag and self.counter > 0:
            self.app.statusPanel.inc_progress()
            self.counter -= 1
            time.sleep(0.5)
        self.app.statusPanel.timeCounter.stop()

    def resize_scrolled_frame(self):
        # self.app.cardsArea.scrolledFrame._canvas['width'] = 200
        # self.app.cardsArea.scrolledFrame._canvas['height'] = 200
        self.app.cardsArea.scrolledFrame['width'] = 200
        self.app.cardsArea.scrolledFrame['height'] = 200