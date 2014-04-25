import wx
import os
from wx.lib import intctrl

DEFAULT_CONFIG_FILENAME = "config/config.js"

# Button definitions
ID_START = wx.NewId()
ID_STEP = wx.NewId()
ID_RUN = wx.NewId()
ID_STOP = wx.NewId()

class Controls(wx.Panel):
    def __init__(self, parent, size, listener):
        wx.Panel.__init__(self, parent, size=size)
        
        self.listener = listener
        
        ## Header
        self.header = wx.StaticText(self, -1, "Controls")
        headerFont = wx.Font(16, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.header.SetFont(headerFont)

        ## Config input
        configFileText = wx.StaticText(self, -1, "Config:")
        self.configFilename = wx.FilePickerCtrl(self, 
            path=os.path.abspath(DEFAULT_CONFIG_FILENAME), size=(200, -1))
        configFileSizer = wx.BoxSizer(wx.HORIZONTAL)
        
        configFileSizer.Add(configFileText)             # label
        configFileSizer.Add((20, -1), proportion=1)   # spacing
        configFileSizer.Add(self.configFilename)
        
        ##  Start button
        self.startButton = wx.Button(self, id=ID_START, label="&Initialize")
        self.Bind(wx.EVT_BUTTON, self.listener.OnStart, self.startButton)
        
        ## Run rounds, steps inputs
        rounds_label = wx.StaticText(self, -1, "Rounds: ")
        self.rounds_input = intctrl.IntCtrl(self, size=(40, -1), value=0, min=0)
        steps_label = wx.StaticText(self, -1, "Steps: ")
        self.steps_input = intctrl.IntCtrl(self, size=(40, -1), value=1, min=0)
        
        ## Run button
        self.runButton = wx.Button(self, id=ID_RUN, label = "&Run")
        self.Bind(wx.EVT_BUTTON, self.OnRun, self.runButton)
        
        runConfigSizer = wx.BoxSizer(wx.HORIZONTAL)
        runConfigSizer.Add(rounds_label)
        runConfigSizer.Add(self.rounds_input)
        runConfigSizer.Add((10, -1))        # padding
        runConfigSizer.Add(steps_label)
        runConfigSizer.Add(self.steps_input)
        runConfigSizer.Add((20, -1), proportion=1)    # padding
        runConfigSizer.Add(self.runButton)
        
        ##  Stop button
        self.stopButton = wx.Button(self, id=ID_STOP, label="S&top")
        self.Bind(wx.EVT_BUTTON, self.listener.OnStop, self.stopButton)
        
        # Sizer
        
        controlsSizer = wx.BoxSizer(wx.VERTICAL)
        controlsSizer.Add(self.header)
        controlsSizer.Add(configFileSizer)
        controlsSizer.Add(self.startButton)
        controlsSizer.Add(runConfigSizer)
        controlsSizer.Add(self.stopButton)
        
        self.SetSizerAndFit(controlsSizer)
        
        self.reset_buttons()
        
    def get_config_filename(self):
        return self.configFilename.GetPath()
        
    def set_status(self, rounds, steps):
        self.rounds_input.SetValue(rounds)
        self.steps_input.SetValue(steps)
        
    def OnRun(self, event):
        rounds = self.rounds_input.GetValue()
        steps = self.steps_input.GetValue()
        self.listener.run(rounds, steps)
        
    # Helper methods
    def set_buttons_processing(self):
        self.startButton.Disable()
        self.runButton.Disable()
        self.stopButton.Enable()
        self.rounds_input.Disable()
        self.steps_input.Disable()

    def set_buttons_ready(self):
        self.rounds_input.Enable()
        self.steps_input.Enable()
        self.startButton.Disable()
        self.runButton.Enable()
        self.stopButton.Enable()
        self.set_status(0, 1)
    
    def reset_buttons(self):
        self.stopButton.Disable()
        self.runButton.Disable()
        self.startButton.Enable()
        self.rounds_input.Disable()
        self.steps_input.Disable()
