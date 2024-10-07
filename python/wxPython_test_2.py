#!/usr/bin/env python

import wx
import wx.xrc
import wx.grid

import gettext
_ = gettext.gettext

###########################################################################
## Class MyFrame1
###########################################################################

class MyFrame1 ( wx.Frame ):

    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = wx.EmptyString, pos = wx.DefaultPosition, size = wx.Size( 640,480 ), style = wx.DEFAULT_FRAME_STYLE|wx.TAB_TRAVERSAL )

        self.SetSizeHints( wx.DefaultSize, wx.DefaultSize )

        self.m_statusBar1 = self.CreateStatusBar( 1, wx.STB_SIZEGRIP, wx.ID_ANY )
        bSizer1 = wx.BoxSizer( wx.VERTICAL )

        self.m_grid1 = wx.grid.Grid( self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, 0 )

        # Grid
        self.m_grid1.CreateGrid( 5, 5 )
        self.m_grid1.EnableEditing( True )
        self.m_grid1.EnableGridLines( True )
        self.m_grid1.EnableDragGridSize( False )
        self.m_grid1.SetMargins( 0, 0 )

        # Columns
        self.m_grid1.EnableDragColMove( False )
        self.m_grid1.EnableDragColSize( True )
        self.m_grid1.SetColLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

        # Rows
        self.m_grid1.EnableDragRowSize( True )
        self.m_grid1.SetRowLabelAlignment( wx.ALIGN_CENTER, wx.ALIGN_CENTER )

        # Label Appearance

        # Cell Defaults
        self.m_grid1.SetDefaultCellAlignment( wx.ALIGN_LEFT, wx.ALIGN_TOP )
        bSizer1.Add( self.m_grid1, 0, wx.ALL, 5 )

        self.SetSizer( bSizer1 )
        self.Layout()
        self.m_menubar1 = wx.MenuBar( 0 )

        self.file = wx.Menu()
        self.menuNew = wx.MenuItem( self.file, wx.ID_NEW, _(u"&New"), wx.EmptyString, wx.ITEM_NORMAL )
        self.file.Append( self.menuNew )
        self.menuOpen = wx.MenuItem( self.file, wx.ID_OPEN, _(u"&Open"), wx.EmptyString, wx.ITEM_NORMAL )
        self.file.Append( self.menuOpen )
        self.menuClose = wx.MenuItem( self.file, wx.ID_CLOSE, _(u"&Close"), wx.EmptyString, wx.ITEM_NORMAL )
        self.file.Append( self.menuClose )
        self.menuExit = wx.MenuItem( self.file, wx.ID_EXIT, _(u"&Exit"), wx.EmptyString, wx.ITEM_NORMAL )
        self.file.Append( self.menuExit )
        self.m_menubar1.Append( self.file, _(u"&File") )

        self.edit = wx.Menu()
        self.menuCopy = wx.MenuItem( self.edit, wx.ID_COPY, _(u"&Copy"), wx.EmptyString, wx.ITEM_NORMAL )
        self.edit.Append( self.menuCopy )
        self.menuCut = wx.MenuItem( self.edit, wx.ID_CUT, _(u"C&ut"), wx.EmptyString, wx.ITEM_NORMAL )
        self.edit.Append( self.menuCut )
        self.menuPaste = wx.MenuItem( self.edit, wx.ID_PASTE, _(u"&Paste"), wx.EmptyString, wx.ITEM_NORMAL )
        self.edit.Append( self.menuPaste )
        self.menuDelete = wx.MenuItem( self.edit, wx.ID_DELETE, _(u"&Delete"), wx.EmptyString, wx.ITEM_NORMAL )
        self.edit.Append( self.menuDelete )
        self.m_menubar1.Append( self.edit, _(u"&Edit") )

        #self.view = wx.Menu()
        #self.m_menubar1.Append( self.view, _(u"&View") )

        self.help = wx.Menu()
        self.menuAbout = wx.MenuItem( self.help, wx.ID_ABOUT, _(u"&About"), wx.EmptyString, wx.ITEM_NORMAL )
        self.help.Append( self.menuAbout )
        self.m_menubar1.Append( self.help, _(u"&Help") )

        self.SetMenuBar( self.m_menubar1 )
        self.Bind(wx.EVT_MENU, self.menuHndl)

#        self.text = wx.TextCtrl(self, -1, style = wx.EXPAND|wx.TE_MULTILINE)

        self.Centre( wx.BOTH )

        ### TH ###
        b = wx.Button(self, label = 'Close', pos = (300,240)) 
        b.Bind(wx.EVT_BUTTON, self.btnclk) 
        self.Bind(wx.EVT_BUTTON, self.OnButtonClicked)
        self.Show(True)

    def __del__( self ):
        pass

    def btnclk(self,e): 
       print("Button received click event. propagated to Panel class")
       e.Skip()
    def menuHndl(self,e): 
       id = e.GetId()
       if id == wx.ID_NEW:
          print("Menu: New")
       elif id == wx.ID_OPEN:
          print("Menu: Open")
       elif id == wx.ID_EXIT:
          print("Menu: Exit")
          wx.CallAfter(self.Close)
       else:
          print("Menu: other ...")
       e.Skip()
    def OnButtonClicked(self, e): 
       print('click event received by frame class')
       e.Skip()
       wx.CallAfter(self.Close)

app = wx.App() 
MyFrame1(None)
app.MainLoop()
