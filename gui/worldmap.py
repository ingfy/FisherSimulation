import wx

class WorldMap(wx.Panel):
    size = (400, 400)

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size = self.size)
        self.SetBackgroundColour("#ffffff")