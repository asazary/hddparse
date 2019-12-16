import tkinter as tk
from tkinter import messagebox as mb
from constants import FileExistanceError


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

        self.rewriteFileFlag = tk.BooleanVar()
        self.rewriteFileFlag.set(0)
        self.rewriteFileCheckbox = tk.Checkbutton(self.row1, text='rewrite file',
                                                  variable=self.rewriteFileFlag,
                                                  onvalue=1, offvalue=0)
        # self.rewriteFileRadio.grid(row=0, column=3)
        self.rewriteFileCheckbox.pack(side=tk.LEFT)
        self.rewriteRecordsFlag = tk.BooleanVar()
        self.rewriteRecordsFlag.set(0)
        self.rewriteRecordsCheckbox = tk.Checkbutton(self.row1, text='rewrite records',
                                                     variable=self.rewriteRecordsFlag,
                                                     onvalue=1, offvalue=0)
        # self.rewriteRecordsCheckbox.grid(row=0, column=4)
        self.rewriteRecordsCheckbox.pack(side=tk.LEFT)

        self.showSizeButton = tk.Button(self.row1, text='Show number', command=self.show_size)
        # self.showSizeButton.grid(row=0, column=5)
        self.showSizeButton.pack(side=tk.LEFT)


    def load_from_file_and_show(self):
        self.app.statusPanel.set_status('Loading...')
        cnt = 0
        try:
            cnt = self.app.simpleCards.load_from_file(init_progress_func=self.app.statusPanel.init_progress_bar,
                                                      inc_progress_func=self.app.statusPanel.inc_progress)
        except FileExistanceError as e:
            mb.showwarning(title='Error', message=str(e))
        self.app.statusPanel.set_status('Loaded %d simple cards' % cnt)


    def save_to_file(self):
        rewrite_file_flag = self.rewriteFileFlag.get()
        rewrite_records_flag = self.rewriteRecordsFlag.get()

        self.app.statusPanel.set_status('Saving...')
        self.app.statusPanel.init_progress_bar(max_value=self.app.simpleCards.size())
        cnt = 0
        try:
            cnt = self.app.simpleCards.save_to_file(rewrite_file=rewrite_file_flag,
                                                    rewrite_records=rewrite_records_flag,
                                                    inc_progress_func=self.app.statusPanel.inc_progress)
        except FileExistanceError as e:
            mb.showwarning(title='Error', message=str(e))
        self.app.statusPanel.set_status('%d simple cards saved' % cnt)

    def show_size(self):
        self.app.statusPanel.set_status('%d simple cards in memory' % self.app.simpleCards.size())

    def show_simple_cards(self):
        self.app.simpleCardsArea.show_page()
