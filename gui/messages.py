import wx

class Messages(wx.Panel):
    def __init__(self, parent, size):
        wx.Panel.__init__(self, parent, size=size)

        self.textbox = wx.TextCtrl(self, style=wx.TE_MULTILINE, size=size)
        self.textbox.SetEditable(False)
        self.textbox.SetBackgroundColour(wx.Colour(255, 255, 255))
        self.header = wx.StaticText(self, label="Messages")
        self.header_font = wx.Font(14, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.header.SetFont(self.header_font)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.sizer.Add(self.header, 0)
        self.sizer.Add(self.textbox, 1, wx.EXPAND)

        self.SetSizerAndFit(self.sizer)

        self.activate()
        
    def activate(self):
        self.active = True
        self.textbox.Enable()
        
    def deactivate(self):
        self.active = False
        self.textbox.Disable()
        
    def add(self, message):
        if self.active:
            self.textbox.AppendText("\n" + message)
            self.textbox.ShowPosition(self.textbox.GetLastPosition())
        
    def clear(self):
        self.textbox.Clear()