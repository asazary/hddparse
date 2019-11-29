import tkinter as tk
from constants import hdTypes
import tkcalendar
from datetime import datetime
from idlelib import tooltip


class UserCardsControlPanel(tk.Frame):
    def __init__(self, master, app, *args, **kwargs):
        tk.Frame.__init__(self, master, args, **kwargs)
        self.app = app

        self.rowsPerPageVar = tk.IntVar(self)
        self.colsPerPageVar = tk.IntVar(self)
        self.rowsPerPageVar.set(3)
        self.colsPerPageVar.set(3)

        self.row1 = tk.Frame(self)
        self.row1.pack(fill=tk.X)

        label1 = tk.Label(self.row1, text='Возраст от')
        label1.pack(side=tk.LEFT, pady=5)

        opts = list(range(16, 50))
        self.varAgeFrom = tk.IntVar(self)
        self.varAgeFrom.set(opts[0])
        self.ageFromSel = tk.OptionMenu(self.row1, self.varAgeFrom, *opts)
        self.ageFromSel.pack(side=tk.LEFT, pady=5)
        label2 = tk.Label(self.row1, text='до')
        label2.pack(side=tk.LEFT)
        self.varAgeTo = tk.IntVar(self)
        self.varAgeTo.set(opts[14])
        self.ageToSel = tk.OptionMenu(self.row1, self.varAgeTo, *opts)
        self.ageToSel.pack(side=tk.LEFT)
        label3 = tk.Label(self.row1, text='лет')
        label3.pack(side=tk.LEFT)

        self.varType = tk.StringVar(self)
        self.varType.set('все')
        self.hdTypeSel = tk.OptionMenu(self.row1, self.varType, *(['все'] + list(hdTypes.keys())))
        self.hdTypeSel.pack(side=tk.LEFT)

        self.bioParamsFrame = tk.Frame(self.row1)
        self.bioParamsFrame.pack(side=tk.LEFT)

        self.varBioPhysical = tk.IntVar(self)
        self.varBioIntellectual = tk.IntVar(self)
        self.varBioEmotional = tk.IntVar(self)
        self.varBioPhysical.set(50)
        self.varBioIntellectual.set(50)
        self.varBioEmotional.set(50)
        self.bioPhysicalScale = tk.Scale(self.bioParamsFrame, from_=0, to=100, resolution=1,
                                         orient=tk.HORIZONTAL, variable=self.varBioPhysical)
        self.bioIntellectualScale = tk.Scale(self.bioParamsFrame, from_=0, to=100, resolution=1,
                                             orient=tk.HORIZONTAL, variable=self.varBioIntellectual)
        self.bioEmotionalScale = tk.Scale(self.bioParamsFrame, from_=0, to=100, resolution=1,
                                          orient=tk.HORIZONTAL, variable=self.varBioEmotional)
        self.bioPhysicalScale.grid(row=0, column=0)
        self.bioIntellectualScale.grid(row=0, column=1)
        self.bioEmotionalScale.grid(row=0, column=2)
        bioPhysicalLabel = tk.Label(self.bioParamsFrame, text='физ', font='Helvetica 8')
        bioPhysicalLabel.grid(row=1, column=0)
        bioIntellectualLabel = tk.Label(self.bioParamsFrame, text='инт', font='Helvetica 8')
        bioIntellectualLabel.grid(row=1, column=1)
        bioEmotionalLabel = tk.Label(self.bioParamsFrame, text='эмо', font='Helvetica 8')
        bioEmotionalLabel.grid(row=1, column=2)

        init_month = datetime.now().month - 1
        init_year = datetime.now().year
        if init_month == 0:
            init_month = 12
            init_year -= 1
        self.minLastLoginDate = tkcalendar.DateEntry(self.row1, month=init_month, year=init_year,
                                                     locale='ru_RU')
        self.minLastLoginDate.pack(side=tk.LEFT)
        tooltip.Hovertip(self.minLastLoginDate, text='Minimum last login date')

        # ---------------------------------------

        self.row2 = tk.Frame(self)
        self.row2.pack(fill=tk.X)

        rowsPerPageList = list(range(1, 10))
        self.rowsPerPage = tk.OptionMenu(self.row2, self.rowsPerPageVar, *rowsPerPageList)
        colsPerPageList = list(range(2, 6))
        self.colsPerPage = tk.OptionMenu(self.row2, self.colsPerPageVar, *colsPerPageList)
        tk.Label(self.row2, text='rows').pack(side=tk.LEFT)
        self.rowsPerPage.pack(side=tk.LEFT)
        tk.Label(self.row2, text='cols').pack(side=tk.LEFT)
        self.colsPerPage.pack(side=tk.LEFT)

        self.resizeCardsAreaButton = tk.Button(self.row2, text='Resize cards area', command=self.resize_cards_area)
        self.resizeCardsAreaButton.pack(side=tk.LEFT, padx=5)

        self.showSimpleCardsButton = tk.Button(self.row2, text='All simple cards', command=self.show_simple_cards)
        self.showSimpleCardsButton.pack(side=tk.LEFT, padx=5)
        self.showFilteredUserCardsButton = tk.Button(self.row2, text='Show user cards',
                                                     command=self.show_filtered_cards)
        self.showFilteredUserCardsButton.pack(side=tk.LEFT, padx=5)


    def show_simple_cards(self):
        self.app.cardsArea.set_mode_simple()
        self.app.cardsArea.show_page()

    def show_filtered_cards(self):
        self.app.cardsArea.set_mode_full()
        self.app.userCards.filter(age_min=self.varAgeFrom.get(), age_max=self.varAgeTo.get(),
                                  hd_type=self.varType.get(), bio_physical_min=self.varBioPhysical.get(),
                                  bio_intellectual_min=self.varBioIntellectual.get(),
                                  bio_emotional_min=self.varBioEmotional.get(),
                                  min_last_login_date=self.minLastLoginDate.get_date())
        #self.app.statusVar.set('%d cards selected' % self.app.userCards.arrFilterSize)
        self.app.cardsArea.show_page()

    def resize_cards_area(self):
        height = (200 + 100) * self.rowsPerPageVar.get()
        width = 230 * self.colsPerPageVar.get()

        work_height = self.app.MAX_HEIGHT - self.app.tabPanel.winfo_height() \
            - self.app.statusPanel.winfo_height() - self.app.cardsArea.statusPanel.winfo_height() - 40
        work_width = self.app.MAX_WIDTH - 200

        if height > work_height:
            height = work_height
        if width > work_width:
            width = work_width

        self.app.cardsArea.scrolledFrame['height'] = height
        self.app.cardsArea.scrolledFrame['width'] = width
