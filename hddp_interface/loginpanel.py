import tkinter as tk
from tkinter import messagebox as mb


class LoginPanel(tk.Frame):
    def __init__(self, master, app, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.app = app

        self.email = tk.StringVar(self)
        self.password = tk.StringVar(self)

        self.emailEntry = tk.Entry(self, textvariable=self.email, width=30)
        self.emailEntry.pack(side=tk.LEFT, padx=5)
        self.passwordEntry = tk.Entry(self, textvariable=self.password, show='*', width=30)
        self.passwordEntry.pack(side=tk.LEFT, padx=5)

        self.loginButton = tk.Button(self, text='Login', command=self.login_func)
        self.loginButton.pack(side=tk.LEFT, padx=5, pady=5)

        self.loginInd = tk.Label(self, text='Not connected')
        self.loginInd.pack(side=tk.LEFT, padx=5, pady=5)

    def login_func(self):
        status, msg = self.app.nf.login_func(email=self.email.get(), password=self.password.get())
        if status:
            self.loginInd['text'] = 'Connected'
            self.loginInd.config(font='Helvetica 12 bold', fg='#009900')
            self.loginButton['state'] = tk.DISABLED

            self.app.simpleSearchPanel.draw_net_search_button()
        else:
            mb.showwarning(title='Error', message=msg)
