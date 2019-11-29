import tkinter as tk
from tkinter import messagebox as mb
from constants import FileExistanceError
from idlelib import tooltip
import threading


class SimpleCardsControlPanel(tk.Frame):
    def __init__(self, master, app, *args, **kwargs):
        tk.Frame.__init__(self, master, args, **kwargs)
        self.app = app

        self.row1 = tk.Frame(self)
        self.row1.pack(fill=tk.X)
        self.statusText = tk.Label(self.row1, fg='#000099', font='Helvetica 10', text='...')
        # self.statusText.grid(row=0, column=1, padx=(10, 10))
        # self.statusText.pack(side=tk.LEFT, padx=(10, 10))
        self.loadFromFileButton = tk.Button(self.row1, text='Load from file', command=self.load_from_file_and_show)
        # self.loadFromFileButton.grid(row=0, column=1, padx=5, pady=5)
        self.loadFromFileButton.pack(side=tk.LEFT, padx=5, pady=5)
        self.saveToFileButton = tk.Button(self.row1, text='Save to file', command=self.save_to_file)
        # self.saveToFileButton.grid(row=0, column=2, padx=5)
        self.saveToFileButton.pack(side=tk.LEFT, padx=5)

        self.rewriteFileFlag = tk.BooleanVar(self)
        self.rewriteFileFlag.set(0)
        self.rewriteFileRadio = tk.Radiobutton(self.row1, text='rewrite file',
                                               variable=self.rewriteFileFlag,
                                               value=1)
        # self.rewriteFileRadio.grid(row=0, column=3)
        self.rewriteFileRadio.pack(side=tk.LEFT)
        tooltip.Hovertip(self.rewriteFileRadio, text='All records in file will be removed')

        self.addRecordsRadio = tk.Radiobutton(self.row1, text='add records',
                                              variable=self.rewriteFileFlag,
                                              value=0)
        self.addRecordsRadio.pack(side=tk.LEFT)
        tooltip.Hovertip(self.addRecordsRadio, text='New records will be added in existing file')

        self.rewriteRecordsFlag = tk.BooleanVar(self)
        self.rewriteRecordsFlag.set(0)
        self.rewriteRecordsCheckbox = tk.Checkbutton(self.row1, text='rewrite records',
                                                     variable=self.rewriteRecordsFlag,
                                                     onvalue=1, offvalue=0)
        # self.rewriteRecordsCheckbox.grid(row=0, column=4)
        self.rewriteRecordsCheckbox.pack(side=tk.LEFT)
        tooltip.Hovertip(self.rewriteRecordsCheckbox, text='If a record exists in file, it will be replaced')

        self.showSizeButton = tk.Button(self.row1, text='Show number', command=self.show_size)
        # self.showSizeButton.grid(row=0, column=5)
        self.showSizeButton.pack(side=tk.LEFT)

        self.clearMemoryButton = tk.Button(self.row1, text='Clear memory', command=self.clear_memory)
        self.clearMemoryButton.pack(side=tk.LEFT, padx=5)

    def load_from_file_and_show(self):
        self.app.statusVar.set('Loading...')
        cnt = 0
        self.sizeVar = tk.IntVar(self)
        self.sizeVar.set(0)
        try:
            #cnt = self.app.userCards.load_from_file(init_progress_func=self.app.statusPanel.init_progress_bar,
            #                                        inc_progress_func=self.app.statusPanel.inc_progress)
            threading.Thread(target=(lambda: self.app.userCards.load_from_file(
                init_progress_func=self.app.statusPanel.init_progress_bar,
                inc_progress_func=self.app.statusPanel.inc_progress,
                size_var=self.sizeVar))).start()
            # cnt = self.sizeVar.get()

        except FileExistanceError as e:
            mb.showwarning(title='Error', message=str(e))
        # self.app.statusVar.set('Loaded %d cards' % cnt)

    def save_to_file(self):
        rewrite_file_flag = self.rewriteFileFlag.get()
        rewrite_records_flag = self.rewriteRecordsFlag.get()

        self.app.statusVar.set('Saving...')
        self.app.statusPanel.init_progress_bar(max_value=self.app.userCards.size)
        cnt = 0
        try:
            # cnt = self.app.userCards.save_to_file(rewrite_file=rewrite_file_flag,
            #                                       rewrite_records=rewrite_records_flag,
            #                                      inc_progress_func=self.app.statusPanel.inc_progress)
            threading.Thread(target=(lambda: self.app.userCards.save_to_file(
                rewrite_file=rewrite_file_flag,
                rewrite_records=rewrite_records_flag,
                inc_progress_func=self.app.statusPanel.inc_progress))).start()

        except FileExistanceError as e:
            mb.showwarning(title='Error', message=str(e))
        # self.app.statusVar.set('%d cards saved' % cnt)

    def show_size(self):
        self.app.statusVar.set('%d cards in memory' % self.app.userCards.size)

    def show_cards(self):
        # self.app.cardsArea.show_page()
        pass

    def clear_memory(self):
        self.app.userCards.clear_all()
        self.app.statusVar.set('Memory cleared')
