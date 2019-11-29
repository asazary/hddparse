import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
from math import ceil
from constants import typesDict, hdTypes
import webbrowser
import hddp_utils
from idlelib import tooltip
from tkscrolledframe import ScrolledFrame

SIMPLE_MODE = 'simple'
FULL_MODE = 'full'


class CardsArea(tk.Frame):
    def __init__(self, master, app, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.app = app
        self.currentPageNumber = 1
        self.numberOfPages = 1
        self.areaMode = FULL_MODE  # or 'simple'
        self.TABLE_HEIGHT = int(self.app.winfo_screenheight() * 0.5)
        self.TABLE_WIDTH = int(self.app.winfo_screenwidth() * 0.4)

        # self.table = CardsGrid(self)
        self.scrolledFrameContainter = tk.Frame(self)
        self.scrolledFrameContainter.pack(fill=tk.BOTH, expand=1)
        self.scrolledFrame = ScrolledFrame(self.scrolledFrameContainter,
                                           height=self.TABLE_HEIGHT,
                                           width=self.TABLE_WIDTH)
        self.scrolledFrame.pack(fill=tk.BOTH, expand=1)
        self.scrolledFrame.bind_arrow_keys(self)
        self.scrolledFrame.bind_scroll_wheel(self.scrolledFrameContainter)

        self.table = self.scrolledFrame.display_widget(tk.Frame)

        self.statusPanel = tk.LabelFrame(self)
        self.statusPanel.pack(fill=tk.X, anchor=tk.E, side=tk.BOTTOM)

        self.statusPanel.toLeftButton = tk.Button(self.statusPanel, text='\u21E6 Prev',
                                                  font='Helvetica 12 bold',
                                                  command=self.to_prev_page)
        self.statusPanel.toRightButton = tk.Button(self.statusPanel, text='\u21E8 Next',
                                                   font='Helvetica 12 bold',
                                                   command=self.to_next_page)
        self.statusPanel.currentPageLabel = tk.Label(self.statusPanel,
                                                     text='Page %d of %d' %
                                                          (self.currentPageNumber, self.numberOfPages)
                                                     )

    def set_mode_full(self):
        self.areaMode = FULL_MODE

    def set_mode_simple(self):
        self.areaMode = SIMPLE_MODE

    def init_panels(self):
        if self.table.winfo_exists() == 0:
            # self.table = CardsGrid(self)
            self.table = self.table = ScrolledFrame(self, width=self.TABLE_WIDTH, height=self.TABLE_HEIGHT)
            self.table.pack(fill=tk.BOTH)
        if self.statusPanel.winfo_exists() == 0:
            self.statusPanel = tk.LabelFrame(self)
            self.statusPanel.pack(fill=tk.X)

    def show_page(self, page_number=1):
        rows_per_page = self.app.userCardsControlPanel.rowsPerPageVar.get()
        cols_per_page = self.app.userCardsControlPanel.colsPerPageVar.get()

        if self.areaMode == FULL_MODE:
            # number_of_records = self.app.userCards.size
            number_of_records = self.app.userCards.arrFilterSize
        elif self.areaMode == SIMPLE_MODE:
            number_of_records = self.app.simpleCards.size()
        else:
            number_of_records = self.app.simpleCards.size()

        left_index = (page_number - 1) * rows_per_page * cols_per_page
        right_index = page_number * rows_per_page * cols_per_page - 1
        if number_of_records - 1 < right_index:
            right_index = number_of_records - 1
        self.numberOfPages = ceil(number_of_records / (rows_per_page * cols_per_page))

        for elem in self.table.winfo_children():
            if type(elem) == UserCardView:
                elem.destroy()

        cur_record_num = left_index
        cur_row_num = 1
        cur_col_num = 1

        while cur_record_num <= right_index and cur_record_num < number_of_records:
            if self.areaMode == FULL_MODE:
                cur_card = UserCardView(self.table, self.app, self.app.userCards.get(cur_record_num))
            elif self.areaMode == SIMPLE_MODE:
                cur_card = SimpleCardView(self.table, self.app.simpleCards[cur_record_num])
            else:
                cur_card = SimpleCardView(self.table, self.app.simpleCards[cur_record_num])

            cur_card.grid(row=cur_row_num, column=cur_col_num, padx=10, pady=10)

            cur_col_num += 1
            if cur_col_num > cols_per_page:
                cur_col_num = 1
                cur_row_num += 1
            cur_record_num += 1

        self.draw_status_elements()

    def draw_status_elements(self):
        if self.statusPanel.toLeftButton.winfo_ismapped() == 0:
            self.statusPanel.toLeftButton.pack(side=tk.LEFT)
        if self.statusPanel.currentPageLabel.winfo_ismapped() == 0:
            self.statusPanel.currentPageLabel.pack(side=tk.LEFT, fill=tk.X, expand=1)
        if self.statusPanel.toRightButton.winfo_ismapped() == 0:
            self.statusPanel.toRightButton.pack(side=tk.RIGHT)

        if self.currentPageNumber <= 1:
            self.statusPanel.toLeftButton['state'] = tk.DISABLED
        else:
            self.statusPanel.toLeftButton['state'] = tk.NORMAL

        if self.currentPageNumber >= self.numberOfPages:
            self.statusPanel.toRightButton['state'] = tk.DISABLED
        else:
            self.statusPanel.toRightButton['state'] = tk.NORMAL

        self.statusPanel.currentPageLabel['text'] = 'Page %d of %d' % (self.currentPageNumber, self.numberOfPages)

    def to_prev_page(self):
        if self.currentPageNumber > 1:
            self.currentPageNumber -= 1
            self.show_page(page_number=self.currentPageNumber)

    def to_next_page(self):
        if self.currentPageNumber < self.numberOfPages:
            self.currentPageNumber += 1
            self.show_page(page_number=self.currentPageNumber)


class CardsGrid(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)


class SimpleCardView(tk.Frame):
    def __init__(self, master, card):
        tk.Frame.__init__(self, master)
        self.master = master
        self.card = card

        tkimage = Image.open(BytesIO(card.imgData))
        tkimage = tkimage.resize((200, 200), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(tkimage)
        self.photoLabel = tk.Label(self, image=self.photo)
        self.photoLabel.pack()
        self.nameLabel = tk.Label(self, text='%s, %d лет' % (card.name, card.age),
                                  fg='blue', cursor='hand2')
        self.nameLabel.pack()
        self.nameLabel.bind('<Button-1>', self.open_link)
        self.userTypeLabel = tk.Label(self, text=typesDict[card.type])
        self.userTypeLabel.pack()

    def open_link(self, event):
        webbrowser.open_new(self.card.link)


class UserCardView(tk.Frame):
    def __init__(self, master, app, card):
        tk.Frame.__init__(self, master)
        self.master = master
        self.card = card
        self.app = app

        tkimage = Image.open(BytesIO(card.thumbnailData))
        tkimage = tkimage.resize((200, 200), Image.ANTIALIAS)
        self.photo = ImageTk.PhotoImage(tkimage)
        self.photoLabel = tk.Label(self, image=self.photo)
        # self.photoLabel.grid(row=0, column=0, columnspan=2)
        self.photoLabel.pack()
        self.photoLabel.bind('<Button-1>', self.show_profile)

        self.infoFrame = tk.Frame(self, bg='#EBFAF9')
        self.infoFrame.pack(expand=1, fill=tk.X)
        self.nameLabel = tk.Label(self.infoFrame,
                                  text=' '.join(filter(None, [self.card.firstName, self.card.secondName])),
                                  font='Helvetica 10 bold underline', bg='#EBFAF9', cursor='hand2',
                                  justify=tk.LEFT)
        self.nameLabel.grid(row=0, column=0, sticky='w', columnspan=2)
        self.nameLabel.bind('<Button-1>', self.open_link)
        self.ageLabel = tk.Label(self.infoFrame, text=hddp_utils.get_age_text(self.card.age),
                                 font='Helvetica 10', bg='#EBFAF9', justify=tk.RIGHT)
        self.ageLabel.grid(row=0, column=2, sticky='e')
        self.infoFrame.columnconfigure(0, weight=2)
        self.infoFrame.columnconfigure(2, weight=1)

        self.typeLabel = tk.Label(self.infoFrame, text=hdTypes[self.card.hd_type.lower()].capitalize(),
                                  font='Helveitica 10', anchor='w', bg='#EBFAF9')
        self.typeLabel.grid(row=1, column=0, sticky='w')
        self.profileLabel = tk.Label(self.infoFrame, text=self.card.profile, font='Helvetica 10', anchor='w',
                                     bg='#EBFAF9')
        self.profileLabel.grid(row=1, column=1)
        self.zodiacLabel = tk.Label(self.infoFrame, text=self.card.zodiac, font='Helvetica 10',
                                    bg='#EBFAF9')
        self.zodiacLabel.grid(row=1, column=2, sticky='e')

        self.typeLabel.columnconfigure(0, weight=1)
        self.profileLabel.columnconfigure(1, weight=1)
        self.zodiacLabel.columnconfigure(2, weight=1)

        self.bioInfoFrame = tk.Frame(self, bg='#EBFAF9')
        self.bioInfoFrame.pack(expand=1, fill=tk.X)
        self.bioInfoFrame.columnconfigure(0, weight=1)
        self.bioInfoFrame.columnconfigure(1, weight=1)
        self.bioInfoFrame.columnconfigure(2, weight=1)
        self.bioInfoFrame.columnconfigure(3, weight=1)

        self.bioPhysicalLabel = tk.Label(self.bioInfoFrame, text='%d%%' % self.card.bio_physical,
                                         font='Helvetica 10 bold', fg='#C58080', bg='#EBFAF9')
        self.bioIntellectualLabel = tk.Label(self.bioInfoFrame, text='%d%%' % self.card.bio_intellectual,
                                             font='Helvetica 10 bold', fg='#80B280', bg='#EBFAF9')
        self.bioEmotionalLabel = tk.Label(self.bioInfoFrame, text='%d%%' % self.card.bio_emotional,
                                          font='Helvetica 10 bold', fg='#8080C5', bg='#EBFAF9')
        self.bioPhysicalLabel.grid(row=0, column=0)
        self.bioIntellectualLabel.grid(row=0, column=1)
        self.bioEmotionalLabel.grid(row=0, column=2)

        bioPhysicalTooltip = tooltip.Hovertip(self.bioPhysicalLabel, text='физическая')
        bioIntellectualTooltip = tooltip.Hovertip(self.bioIntellectualLabel, text='интеллектуальная')
        bioEmotionalTooltip = tooltip.Hovertip(self.bioEmotionalLabel, text='эмоциональная')

        self.relationshipTypeLabel = tk.Label(self.bioInfoFrame, text=self.card.relationshipType,
                                              font='Helvetica 10 bold', bg='#EBFAF9')
        self.relationshipTypeLabel.grid(row=0, column=3)


    def open_link(self, event):
        webbrowser.open_new(self.card.link)

    def show_profile(self, event):
        self.app.userProfileArea.show_card(user_card=self.card)

