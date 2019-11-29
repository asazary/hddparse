import tkinter as tk
import tkinter.ttk as ttk
from hddp_interface.UserProfileArea import UserProfileArea


import netFuncs
from SimpleCards import SimpleUserCards
from hddp_interface import statuspanel, loginpanel, simplesearchpanel, SimpleCardsFileControlPanel, testPanel, \
                           CardsArea, UserCardsFileControlPanel, UserCardsControlPanel
from UserCards import UserCards


class Application(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.nf = netFuncs.NetTools(app=self)
        self.simpleCards = SimpleUserCards()
        self.userCards = UserCards(self)

        #self.window = tk.Tk()
        self.title('HDD parser')
        # self.window.geometry('{}x{}'.format(400, 400))
        self.MAX_HEIGHT = int(self.winfo_screenheight() * 0.8)
        self.MAX_WIDTH = int(self.winfo_screenwidth() * 0.8)
        self.geometry('')
        self.maxsize(height=self.MAX_HEIGHT, width=self.MAX_WIDTH)

        self.progressVar = tk.IntVar(self)
        self.progressVar.set(0)
        self.statusVar = tk.StringVar(self)
        self.statusVar.set('...')

        self.mainFrame = tk.Frame(self)
        self.mainFrame.pack(side=tk.LEFT)
        self.userProfileFrame = tk.Frame(self)
        self.userProfileFrame.pack(side=tk.RIGHT, ipadx=10, ipady=20, padx=10, pady=10, fill=tk.BOTH, expand=1)

        self.tabPanel = ttk.Notebook(self.mainFrame)

        self.loginPanel = loginpanel.LoginPanel(self.mainFrame, self)
        self.simpleSearchPanel = simplesearchpanel.SimpleSearchPanel(self.mainFrame, self)
        self.simpleCardsFileControlPanel = SimpleCardsFileControlPanel.SimpleCardsControlPanel(self.mainFrame, self)
        self.userCardsFileControlPanel = UserCardsFileControlPanel.SimpleCardsControlPanel(self.mainFrame, self)
        self.userCardsControlPanel = UserCardsControlPanel.UserCardsControlPanel(self.mainFrame, self)
        self.testPanel = testPanel.TestPanel(self.mainFrame, self)

        self.statusPanel = statuspanel.StatusPanel(self.mainFrame, self)
        # self.statusPanel.grid(row=7, ipadx=7, ipady=5, sticky='nsew')
        self.statusPanel.pack(side=tk.BOTTOM, ipadx=7, ipady=5, fill=tk.X)
        self.statusPanel.init_status_variables(self.statusVar, self.progressVar, self.statusPanel.stopFlagVar)

        # self.tabPanel.grid(row=0, ipadx=5, ipady=5, sticky='nsew')
        self.tabPanel.pack(side=tk.TOP, ipadx=5, ipady=5, fill=tk.X)

        self.tabPanel.add(self.loginPanel, text='login')
        self.tabPanel.add(self.simpleSearchPanel, text='simple search')
        self.tabPanel.add(self.simpleCardsFileControlPanel, text='simple cards IO')
        self.tabPanel.add(self.userCardsFileControlPanel, text='user cards IO')
        self.tabPanel.add(self.userCardsControlPanel, text='cards control')
        self.tabPanel.add(self.testPanel, text='test')

        self.cardsArea = CardsArea.CardsArea(self.mainFrame, self)
        # self.cardsArea.grid(row=2, ipadx=5, ipady=5, padx=2, pady=2, sticky='nsew')
        self.cardsArea.pack(ipadx=5, ipady=5, padx=2, pady=2, fill=tk.BOTH, expand=1)
        # ---------------------------------

        self.userProfileArea = UserProfileArea(self.userProfileFrame, self, bg='#f0f0ff')
        self.userProfileArea.pack(fill=tk.BOTH, expand=1)
