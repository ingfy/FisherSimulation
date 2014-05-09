import wx

class Info(wx.Panel):
    phase_names = {
        "COASTPLAN":    "Coastal Planning",
        "HEARING":      "Hearing",
        "GOVDECISION":  "Government Decision",
        "FISHING1":     "Fishing and Working (1)",
        "BUILDING":     "Building of Aquaculture",
        "FISHING2":     "Fishing and Working (2)",
        "LEARNING":     "Learning Phase"
    }

    round = [
        "COASTPLAN", "HEARING", "GOVDECISION", "FISHING1", "BUILDING",
        "FISHING2", "LEARNING"
    ]

    def __init__(self, parent, size):
        wx.Panel.__init__(self, parent, size=size)

        padding = 10

        phases_x = padding
        phases_y = padding

        w, h = size
        phases_w = w - padding * 2
        phases_h = h - padding * 2

        between = 2

        line_height = phases_h / len(Info.round) - between
        font_size = min(18, line_height / 2)

        self.phase_name_font = wx.Font(
            font_size,
            wx.DECORATIVE,
            wx.NORMAL,
            wx.BOLD
        )

        self.phases = {
            Info.round[i]:
                wx.StaticText(
                    self,
                    label=Info.phase_names[Info.round[i]],
                    pos=(phases_x, phases_y + line_height * i)
                ) for i in xrange(len(Info.round))
        }
        
        for label in Info.phase_names:
            self.phases[label].SetFont(self.phase_name_font)

        self.set_current_phase(Info.round[0])

    def set_current_phase(self, name):
        for label in self.phases:
            color = "red" if name == label else "black"
            self.phases[label].SetForegroundColour(color)
            self.phases[label].Refresh()