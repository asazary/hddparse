import tkinter as tk
from PIL import Image, ImageTk
from io import BytesIO
from hddp_utils import get_age_text


class UserProfileArea(tk.Frame):
    def __init__(self, master, app, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.app = app

        self.area = tk.Frame(self)
        self.area.pack(fill=tk.BOTH, expand=1)
        self.area.userProfile = None

    def show_card(self, user_card):
        if self.area.userProfile:
            self.area.userProfile.destroy()
        self.area.userProfile = UserProfile(self.area, self.app, user_card)
        self.area.userProfile.pack(fill=tk.BOTH, expand=1)


class UserProfile(tk.Frame):
    def __init__(self, master, app, user_card, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)
        self.master = master
        self.app = app

        self.topPanel = tk.Frame(self)
        self.topPanel.pack(side=tk.TOP, fill=tk.X)
        self.closeButton = tk.Button(self.topPanel, text='close', command=self.close)
        self.closeButton.pack(side=tk.RIGHT)

        tkimage = Image.open(BytesIO(user_card.thumbnailData))
        self.profilePhoto = ImageTk.PhotoImage(tkimage)
        self.profilePhotoLabel = tk.Label(self, image=self.profilePhoto)
        self.profilePhotoLabel.pack(side=tk.TOP)

        self.name = tk.Label(self,
                             text=(' '.join(filter(None, [user_card.firstName, user_card.secondName]))),
                             font='Helvetica 16 bold')
        self.name.pack(side=tk.TOP)

        self.info0 = tk.Frame(self)
        self.info0.pack(fill=tk.X)
        self.info0.columnconfigure(1, weight=1)

        parse_date = tk.Label(self.info0, text='Date of parse: ' + user_card.parseDate.strftime('%d.%m.%Y %H:%M'),
                              font='Helvetica 12')
        parse_date.grid(row=0, column=1, sticky='e')
        last_login_date = tk.Label(self.info0, text='Last login: ' + user_card.lastLogin.strftime('%d.%m.%Y %H:%M'),
                                   font='Helvetica 12')
        last_login_date.grid(row=1, column=1, sticky='e')

        self.info1 = tk.Frame(self)
        self.info1.pack(fill=tk.X)
        self.info1.columnconfigure(0, weight=1)
        self.info1.columnconfigure(1, weight=1)
        self.info1.columnconfigure(2, weight=1)

        info1_font = 'Helvetica 14'
        info1_font_bold = 'Helvetica 14 bold'
        city = tk.Label(self.info1, text=user_card.city, font=info1_font)
        city.grid(row=0, column=0, sticky='w')
        age = tk.Label(self.info1, text=get_age_text(user_card.age), font=info1_font_bold)
        age.grid(row=0, column=2, sticky='e')

        hd_type = tk.Label(self.info1, text=user_card.hd_type, font=info1_font)
        hd_type.grid(row=1, column=0, sticky='w')
        profile = tk.Label(self.info1, text=user_card.profile, font=info1_font_bold)
        profile.grid(row=1, column=1)
        zodiac = tk.Label(self.info1, text=user_card.zodiac, font=info1_font)
        zodiac.grid(row=1, column=2, sticky='e')

        self.info2 = tk.Frame(self)
        self.info2.pack(fill=tk.X, pady=10)
        authority = tk.Label(self.info2, text=user_card.authority, font=info1_font)
        authority.grid(row=0, column=0, sticky='w')
        definition = tk.Label(self.info2, text=user_card.definition, font=info1_font)
        definition.grid(row=1, column=0, sticky='w')
        cross = tk.Label(self.info2, text=user_card.cross, font=info1_font)
        cross.grid(row=2, column=0, sticky='w')

        self.info3 = tk.Frame(self)
        self.info3.pack(fill=tk.X, pady=5)
        self.info3.columnconfigure(0, weight=1)
        self.info3.columnconfigure(1, weight=1)
        rel_type_text = tk.Label(self.info3, text=user_card.relationshipTypeText, font=info1_font)
        rel_type_text.grid(row=0, column=0, sticky='w')
        rel_type = tk.Label(self.info3, text=user_card.relationshipType, font=info1_font)
        rel_type.grid(row=0, column=1, sticky='e')

        self.info4 = tk.Frame(self)
        self.info4.pack(fill=tk.X)
        info4_font = 'Helvetica 12'
        info4_font_bold = 'Helvetica 12 bold'
        self.info4.columnconfigure(0, weight=1)
        self.info4.columnconfigure(1, weight=1)
        self.info4.columnconfigure(2, weight=1)
        physical_text = tk.Label(self.info4, text='Физ', font=info4_font, fg='#C58080')
        physical_text.grid(row=0, column=0)
        intellectual_text = tk.Label(self.info4, text='Инт', font=info4_font, fg='#80B280')
        intellectual_text.grid(row=0, column=1)
        emotional_text = tk.Label(self.info4, text='Эмо', font=info4_font, fg='#8080C5')
        emotional_text.grid(row=0, column=2)
        physical_number = tk.Label(self.info4, text='%d%%' % user_card.bio_physical,
                                   font=info4_font_bold, fg='#C58080')
        physical_number.grid(row=1, column=0)
        intellectual_number = tk.Label(self.info4, text='%d%%' % user_card.bio_intellectual,
                                       font=info4_font_bold, fg='#80B280')
        intellectual_number.grid(row=1, column=1)
        emotional_number = tk.Label(self.info4, text='%d%%' % user_card.bio_emotional,
                                    font=info4_font_bold, fg='#8080C5')
        emotional_number.grid(row=1, column=2)

    def close(self):
        if self.master.userProfile:
            self.master.userProfile.pack_forget()
            self.master.userProfile.destroy()
