# simple.py 
#source http://zetcode.com/wxpython/firststeps/
import os
import sys
import numpy
import re
import wx
import Controller as con
import Messages as m                    # enums and print related

basedir = '/home/jeremy/Projects-Active/CM0645/' # home version
#basedir = '/home/izje1/Documents/Projects_Active/CM0645/' # Northumbria verson


class Example(wx.Frame):

    def __init__(self, parent, title, controller):
        super(Example, self).__init__(parent, title=title,size=(800, 600))
        self.con = controller
        self.InitUI()

#See: https://github.com/wxWidgets/wxPython/blob/master/wx/lib/colourdb.py for colour names
#
    def InitUI(self):
        self.CreateMenuBar()        
 
        panel = wx.Panel(self)
        panel.SetFont(wx.Font(12, wx.SWISS, wx.NORMAL, wx.NORMAL))
        panel.SetBackgroundColour('BISQUE')

        vbox = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)

        line1 = wx.StaticLine(panel)
        vbox.Add(line1, 0, wx.EXPAND)

        toolbar1 = wx.Panel(panel, size=(-1, 30))

        back = wx.BitmapButton(toolbar1, bitmap=wx.Bitmap('images/back.png'),
                style=wx.NO_BORDER)
        forward = wx.BitmapButton(toolbar1, bitmap=wx.Bitmap('images/forw.png'),
                style=wx.NO_BORDER)
        refresh = wx.BitmapButton(toolbar1, bitmap=wx.Bitmap('images/refresh.png'),
                style=wx.NO_BORDER)
        stop = wx.BitmapButton(toolbar1, bitmap=wx.Bitmap('images/stop.png'),
                style=wx.NO_BORDER)
        home = wx.BitmapButton(toolbar1, bitmap=wx.Bitmap('images/home.png'),
                style=wx.NO_BORDER)
        address = wx.ComboBox(toolbar1, size=(50, -1))
        go = wx.BitmapButton(toolbar1, bitmap=wx.Bitmap('images/play.png'),
                style=wx.NO_BORDER)
        text = wx.TextCtrl(toolbar1, size=(150, -1))

        hbox1.Add(back)
        hbox1.Add(forward)
        hbox1.Add(refresh)
        hbox1.Add(stop)
        hbox1.Add(home)
        hbox1.Add(address, 1, wx.TOP, 3)
        hbox1.Add(go, 0, wx.TOP | wx.LEFT, 3)
        hbox1.Add(text, 0, wx.TOP | wx.RIGHT, 3)

        toolbar1.SetSizer(hbox1)
        vbox.Add(toolbar1, 0, wx.EXPAND)
        line = wx.StaticLine(panel)
        vbox.Add(line, 0, wx.EXPAND)

        toolbar2 = wx.Panel(panel, size=(-1, 30))
        bookmark1 = wx.BitmapButton(toolbar2, bitmap=wx.Bitmap('images/love.png'),
                style=wx.NO_BORDER)
        bookmark2 = wx.BitmapButton(toolbar2, bitmap=wx.Bitmap('images/book.png'),
                style=wx.NO_BORDER)
        bookmark3 = wx.BitmapButton(toolbar2, bitmap=wx.Bitmap('images/sound.png'),
                style=wx.NO_BORDER)

        hbox2.Add(bookmark1, flag=wx.RIGHT, border=5)
        hbox2.Add(bookmark2, flag=wx.RIGHT, border=5)
        hbox2.Add(bookmark3)

        toolbar2.SetSizer(hbox2)
        vbox.Add(toolbar2, 0, wx.EXPAND)

        line2 = wx.StaticLine(panel)
        vbox.Add(line2, 0, wx.EXPAND)

        self.textpanel = wx.TextCtrl(panel, style=wx.TE_MULTILINE|wx.TE_READONLY)
        vbox.Add(self.textpanel, 0, wx.EXPAND)

        panel.SetSizer(vbox)

        self.CreateStatusBar()

        
#        self.textpanel.SetValue("Projects Active Analyser -- Scolling text")
        self.gprint("Projects Active Analyser -- Scolling text")
#        self.con.setGui(self.textpanel)   # needed for printing
        self.con.setGui(self)   # needed for printing

        self.SetTitle("Projects Active Analyser")
        self.Centre()
        

    def CreateMenuBar(self):
        
        menuBar = wx.MenuBar()
        
        fileMenu = wx.Menu()
        fileMenu.Append(wx.ID_NEW, '&New')
        fileMenu.Append(wx.ID_OPEN, '&Open')
        fileMenu.Append(wx.ID_SAVE, '&Save')
        fileMenu.AppendSeparator()

        imp = wx.Menu()
        imp.Append(wx.ID_ANY, 'Import Cohorts')
        imp.Append(wx.ID_ANY, 'Import Marks')
#        imp.Append(wx.ID_ANY, 'Import mail...')
        imp.AppendSeparator()

        fileMenu.Append(wx.ID_ANY, 'I&mport', imp)
        fileMenu.AppendSeparator()

        qmi = wx.MenuItem(fileMenu, wx.ID_EXIT, '&Quit\tCtrl+W')
        fileMenu.Append(qmi)

        helpMenu= wx.Menu()
        menuAbout= helpMenu.Append(wx.ID_ABOUT, "&About"," Information about Projects")

        content = wx.Menu()
        optionsItem = content.Append(wx.NewId(), 'Set Preferences and Cohorts...', "Show an Options Dialog")
#        content.Append(wx.ID_ANY, 'Set Process...')
#        content.Append(wx.ID_ANY, 'Import mail...')

        settingsMenu = wx.Menu()
        settingsItem = wx.MenuItem(settingsMenu, 100,text = "settings",kind = wx.ITEM_NORMAL)
        settingsMenu.Append(wx.ID_ANY, '&Content', content)
#        runitems = wx.Menu()
#        runitems.Append(wx.ID_ANY, 'Set Sources...')
#        runitems.Append(wx.ID_ANY, 'Set Process...')
        

        dbops = wx.Menu()
        dbrest = wx.MenuItem(dbops, wx.ID_ANY, 'Reset DB')
        dbops.Append(dbrest)
        dbsummary = wx.MenuItem(dbops, wx.ID_ANY, 'Summarise DB')
        dbops.Append(dbsummary)
        dbops.AppendSeparator()

        
        runMenu = wx.Menu()
        getparts = wx.MenuItem(runMenu, wx.ID_ANY, '&Extract Parts (Step 1)')
        runMenu.Append(getparts)
        getmarks = wx.MenuItem(runMenu, wx.ID_ANY, '&Get Marks(Step 2)')
        runMenu.Append(getmarks)
        getstats = wx.MenuItem(runMenu, wx.ID_ANY, '&Text Statistics (Step 3)')
        runMenu.Append(getstats)
        getnltk = wx.MenuItem(runMenu, wx.ID_ANY, '&NLTK, AWL, CSAWL, LFP (Step 4)')
        runMenu.Append(getnltk)
        runMenu.AppendSeparator()
        runMenu.Append(wx.ID_ANY, '&Db', dbops)
        runMenu.AppendSeparator()
        runMenu.Append(wx.ID_ANY, '&Generate BNC')
        runMenu.Append(wx.ID_ANY, '&Check AWL')
        runMenu.Append(wx.ID_ANY, '&Run All')
        
        runItem = wx.MenuItem(runMenu, 100,text = "run",kind = wx.ITEM_NORMAL)
        
        menuBar.Append(fileMenu, '&File')
        menuBar.Append(settingsMenu, '&Settings')
        menuBar.Append(runMenu, '&Run')
        menuBar.Append(helpMenu, "&Help")
        self.SetMenuBar(menuBar)

#bind callbacks to methods
#
        self.Bind(wx.EVT_MENU, self.ExtractParts, getparts) # extract parts
        self.Bind(wx.EVT_MENU, self.getMarks, getmarks) # get marks
        self.Bind(wx.EVT_MENU, self.getStats, getstats) # get text Statistics
        self.Bind(wx.EVT_MENU, self.getNLTK, getnltk) # get NLTK Ops Statistics
        
        self.Bind(wx.EVT_MENU, self.OnQuit, qmi)    #quit menu
        self.Bind(wx.EVT_MENU, self.ResetDB, dbrest) #reset db
        self.Bind(wx.EVT_MENU, self.SummariseDB, dbsummary) #summarisze db
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout) # about
        self.Bind(wx.EVT_MENU, self.onOptions, optionsItem)
        #self.Bind(wx.EVT_MENU, self.OnQuit, fileItem)

        self.SetSize((800, 600))
        self.SetTitle('Projects Active')
        self.Centre()

    

    def ResetDB(self, e):
        dlg = wx.MessageDialog(self, "Really Reset DB?","Confirm Reset", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.con.InitializeDB()

    def SummariseDB(self, e):
        self.con.getDB(self.con.dbfile)

#Step 1: Extract Standard Report Parts (From Abstract to References)
#
    def ExtractParts(self, e):
        self.con.Extract_Parts()

#Step 2: 
    def getMarks(self, e):
        self.con.GetData()

#Step 3 getStats
    def getStats(self, e):
        self.con.StatsCohorts()

#Step 4 getNLTK
    def getNLTK(self, e):
        self.con.TagCohorts()

        
    def OnQuit(self, e):
        dlg = wx.MessageDialog(self, "Exit Analysis?","Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()
            
    def onOptions(self, event):
        """"""
        dlg = CohortDialog(self.con)
        dlg.ShowModal()
        dlg.Destroy()

    def gprint(self, text, level=m.Warnings.Standard):
        if isinstance(text, str):
#        oldtext = self.textpanel.GetValue()
#        newtext = oldtext + "\n" + text
            self.textpanel.SetValue(text)
        elif isinstance(text, list):
            [self.gprint(item, level) for item in text]
        else:
            print("Gprint {}".format(text))

    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a Projects Active V0.1", "About Project", wx.OK|wx.ICON_INFORMATION)

########################################################################
class CohortDialog(wx.Dialog):
    """"""

#     #----------------------------------------------------------------------
#     def __init__(self):
#         """Constructor"""
#         wx.Dialog.__init__(self, None, title="Options")

#         radio1 = wx.RadioButton( self, -1, " Radio1 ", style = wx.RB_GROUP )
#         radio2 = wx.RadioButton( self, -1, " Radio2 " )
#         radio3 = wx.RadioButton( self, -1, " Radio3 " )

#         sizer = wx.BoxSizer(wx.VERTICAL)
#         sizer.Add(radio1, 0, wx.ALL, 5)
#         sizer.Add(radio2, 0, wx.ALL, 5)
#         sizer.Add(radio3, 0, wx.ALL, 5)

#         for i in range(3):
#             chk = wx.CheckBox(self, label="Checkbox #%s" % (i+1))
#             sizer.Add(chk, 0, wx.ALL, 5)
#         self.SetSizer(sizer)

#         self.Bind(wx.EVT_CHECKBOX,self.onChecked)

    def __init__(self, controller):
        wx.Dialog.__init__(self, None, title="Options")

        self.InitUI()
        self.SetSize((350, 300))
        self.SetTitle("Select Preferences")
        self.con = controller


    def InitUI(self):

        pnl = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        sb = wx.StaticBox(pnl, label='Message Level')
        sbs = wx.StaticBoxSizer(sb, orient=wx.VERTICAL)
        self.rb1 = wx.RadioButton(pnl, label='Verbose Output',style=wx.RB_GROUP)
        self.rb2 = wx.RadioButton(pnl, label='Standard Output')
        self.rb3 = wx.RadioButton(pnl, label='Essential Output Only')

        sbs.Add(self.rb1)
        sbs.Add(self.rb2)
        sbs.Add(self.rb3)

        self.rb1.Bind(wx.EVT_RADIOBUTTON, self.SetVal)
        self.rb2.Bind(wx.EVT_RADIOBUTTON, self.SetVal)
        self.rb3.Bind(wx.EVT_RADIOBUTTON, self.SetVal)

        sbs.Add(wx.CheckBox(pnl, label="Year 15_16"))
        sbs.Add(wx.CheckBox(pnl, label="Year 16_17"))
        sbs.Add(wx.CheckBox(pnl, label="Year 17_18"))
 #       for i in range(3):
 #               chk = wx.CheckBox(self, label="Checkbox #%s" % (i+1))
 #               sbs.Add(chk, 0, wx.ALL, 5)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
#        hbox1.Add(wx.RadioButton(pnl, label='Custom'))
#        hbox1.Add(wx.TextCtrl(pnl), flag=wx.LEFT, border=5)
#        sbs.Add(hbox1)

        pnl.SetSizer(sbs)

        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        okButton = wx.Button(self, label='Ok')
        closeButton = wx.Button(self, label='Close')
        hbox2.Add(okButton)
        hbox2.Add(closeButton, flag=wx.LEFT, border=5)

        vbox.Add(pnl, proportion=1,
            flag=wx.ALL|wx.EXPAND, border=5)
        vbox.Add(hbox2, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=10)

        self.SetSizer(vbox)
        self.Bind(wx.EVT_CHECKBOX,self.onChecked) 
        okButton.Bind(wx.EVT_BUTTON, self.OnClose)
        closeButton.Bind(wx.EVT_BUTTON, self.OnClose)

    def SetVal(self, e):
        level = 0
        state1 = str(self.rb1.GetValue())
        state2 = str(self.rb2.GetValue())
        state3 = str(self.rb3.GetValue())
        if state1:
            level = m.Warnings.Verbose
        elif state2:
            level = m.Warnings.Standard
        else:
            level = m.Warnings.Important
        self.con.output_level = level
        print("Setval: 1:{} 2:{} 3:{} -- Global:{}".format(state1, state2, state3,self.con.output_level))
        
              
    def onChecked(self, e): 
        cb = e.GetEventObject()
        matchObj = re.search( r'Year (\d\d_\d\d)', cb.GetLabel(), re.M|re.I)
        label  = matchObj.group(1)
        print(cb.GetLabel(),' is clicked',cb.GetValue(), label)
        self.con.addCohort(label)


    def OnClose(self, e):
        self.Destroy()
        

def main(cntrl):
    app = wx.App()
    ex = Example(None, title='Projects Active', controller=cntrl)
    ex.Show()
    app.MainLoop()


if __name__ == '__main__':
    main()
