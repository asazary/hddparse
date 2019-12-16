import tkinter as tk
import threading


class NetSearchPanel(tk.Frame):
    def __init__(self, master, app, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.app = app

        label1 = tk.Label(self, text='Возраст от')
        label1.grid(column=0, row=0, pady=5)

        opts = list(str(x) for x in range(16, 50))
        self.varAgeFrom = tk.StringVar(self)
        self.varAgeFrom.set(opts[0])
        self.ageFromSel = tk.OptionMenu(self, self.varAgeFrom, *opts)
        self.ageFromSel.grid(column=1, row=0, pady=5)
        label2 = tk.Label(self, text='до')
        label2.grid(column=2, row=0)
        self.varAgeTo = tk.StringVar(self)
        self.varAgeTo.set(opts[14])
        self.ageToSel = tk.OptionMenu(self, self.varAgeTo, *opts)
        self.ageToSel.grid(column=3, row=0)
        label3 = tk.Label(self, text='лет')
        label3.grid(column=4, row=0)

        gender_opts = ['all', 'male', 'female']
        self.varGender = tk.StringVar(self)
        self.varGender.set(gender_opts[0])
        self.genderSel = tk.OptionMenu(self, self.varGender, *gender_opts)
        self.genderSel.grid(column=5, row=0, padx=10)

        self.varCity = tk.StringVar(self)
        self.varCity.set('Санкт-Петербург')
        self.cityEntry = tk.Entry(self, textvariable=self.varCity)
        self.cityEntry.grid(column=6, row=0)

        threads_opts = list(x for x in range(1, 16))
        self.varThreadsNumber = tk.IntVar(self)
        self.varThreadsNumber.set(threads_opts[4])
        threads_number_label = tk.Label(self, text="threads num")
        threads_number_label.grid(row=0, column=7, padx=5)
        self.threadsNumberSel = tk.OptionMenu(self, self.varThreadsNumber, *threads_opts)
        self.threadsNumberSel.grid(row=0, column=8)

        self.startNetSearchButton = tk.Button(self, text='Net Search', command=self.start_net_search)
        self.startFullNetSearchButton = tk.Button(self, text='Full Net Search', command=self.start_full_net_search)

    def draw_net_search_button(self):
        self.startNetSearchButton.grid(column=9, row=0, padx=5, pady=5)
        self.startFullNetSearchButton.grid(column=10, row=0, padx=5, pady=5)

    def start_net_search(self):
        params = {'ageFrom': self.varAgeFrom.get(),
                  'ageTo': self.varAgeTo.get(),
                  'gender': self.varGender.get(),
                  'city': self.varCity.get()}

        threading.Thread(target=(lambda: self.app.nf.start_search(params))).start()

    def start_full_net_search(self):
        params = {'ageFrom': self.varAgeFrom.get(),
                  'ageTo': self.varAgeTo.get(),
                  'gender': self.varGender.get(),
                  'city': self.varCity.get()}
        threading.Thread(target=(lambda: self.app.nf.start_full_net_search(params,
                                                                           threads_number=self.varThreadsNumber.get()))).start()
