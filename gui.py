import wx
import gui.worldmap as worldmap
import simulation.do as do
import simulation.simulation as simulation
import simulation.util as util
import time

class Backend():
    def __init__(self):
        self._simulation = simulation.Simulation()
        self.simulation_info = None
        
    def get_map(self):
        return self.simulation_info.map

    def start(self, config_filename=None):
        # TODO: Move to configuration screen
        self._simulation.setup_config(filename=config_filename)
        self.simulation_info = self._simulation.initialize()
        self.next_phase = "COASTPLAN"
        
    def step(self):
        result = self._simulation.step()
        self.simulation_info.map.grid = util.update_map(
            self.simulation_info.map.grid, result.map.grid
        )
        self.next_phase = result.next_phase
        return result
        
    def abort(self):
        pass

# Button definitions
ID_START = wx.NewId()
ID_STEP = wx.NewId()
ID_STOP = wx.NewId()

# Define simulation finished event
EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    win.Connect(-1, -1, EVT_RESULT_ID, func)
    
class ResultEvent(wx.PyEvent):
    def __init__(self, data):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.data = data
        
class Controls(wx.Panel):
    def __init__(self, parent, size):
        wx.Panel.__init__(self, parent, size=size)

        ##  Start button
        self.startButton = wx.Button(self, id=ID_START, label="&Start")
        self.Bind(wx.EVT_BUTTON, self.GetParent().OnStart, self.startButton)
        
        ##  Step button
        self.stepButton = wx.Button(self, id=ID_STEP, pos=(0, 30), 
            label="St&ep")
        self.Bind(wx.EVT_BUTTON, self.GetParent().OnStep, self.stepButton)
        
        ##  Stop button
        self.stopButton = wx.Button(self, id=ID_STOP, pos=(0, 60), 
            label="S&top")
        self.Bind(wx.EVT_BUTTON, self.GetParent().OnStop, self.stopButton)

    # Helper methods
    def set_buttons_running(self):
        self.startButton.Disable()
        self.stepButton.Enable()
        self.stopButton.Enable()
    
    def reset_buttons(self):
        self.stopButton.Disable()
        self.stepButton.Disable()
        self.startButton.Enable()    
        
        
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

    def __init__(self, parent, size):
        wx.Panel.__init__(self, parent, size=size)
        
        self.phase_name = wx.StaticText(self, 
            label=Info.phase_names["COASTPLAN"])            
        self.phase_name_font = wx.Font(18, wx.DECORATIVE, wx.NORMAL, wx.BOLD)
        self.phase_name.SetFont(self.phase_name_font)
        
        
    def set_current_phase(self, name):
        self.phase_name.SetLabel(Info.phase_names.get(name, name))
        
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
        
    def add(self, message):
        self.textbox.AppendText("\n" + message)
        self.textbox.ShowPosition(self.textbox.GetLastPosition())
        
    def clear(self):
        self.textbox.Clear()
    
class Window(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        
        # World graphic
        self._graphics = worldmap.WorldMap(self)
        self.graphics_sizer = wx.BoxSizer(wx.VERTICAL)
        self.graphics_sizer.Add(self._graphics, 1, wx.EXPAND)
        
        # Controls panel
        self.controls = Controls(self, (300, 200))
        
        # Info panel
        self.info = Info(self, (300, 200))
                
        # Messages panel
        self.messages = Messages(self, (600, 400))
        
        self.interface_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.controls_info_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.controls_info_sizer.Add(self.info, 0, wx.EXPAND)
        self.controls_info_sizer.Add(self.controls, 1, wx.EXPAND)
        
        self.messages_sizer = wx.BoxSizer(wx.VERTICAL)
        self.messages_sizer.Add(self.messages)
        
        self.interface_sizer.Add(self.controls_info_sizer, 0, wx.EXPAND)
        self.interface_sizer.Add(self.messages_sizer, 1, wx.EXPAND)
        
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.sizer.Add(self.interface_sizer, 0, wx.EXPAND)
        self.sizer.Add(self.graphics_sizer, 1, wx.EXPAND)       
        
                
        # Layout sizers
        self.SetSizerAndFit(self.sizer)
        
        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.OnResult)
        
        # Set up close event so timer is properly stopped
        wx.EVT_CLOSE(self, self.OnClose)
        
        self._backend = None
        
        self.reset_gui()
        self.Show()
        
    # Helper methods
    def set_buttons_running(self):
        self.controls.set_buttons_running()
    
    def reset_gui(self):
        self.controls.reset_buttons()
        self.messages.clear()    
        
    # Event Methods
    def OnStart(self, event):
        self.set_buttons_running()
        self._backend = Backend()
        self._backend.start()
        self._graphics.start(self._backend)
        
    def OnStep(self, event):
        self.controls.stepButton.Disable()
        self.info.set_current_phase(self._backend.next_phase)
        result = self._backend.step()
        self._graphics.OnUpdate(None)
        for m in result.messages:
            self.messages.add(str(m))
        self.controls.stepButton.Enable()
        
    def OnStop(self, event):
        self._backend.abort()
        self._graphics.stop_timer()
        self.reset_gui()
        
    def OnResult(self, event):
        self.reset_gui()
        if event.data is None:
            print("Simulation aborted")
        else:
            print("Simulation finished")
            
    def OnClose(self, event):
        self._graphics.stop_timer()
        if not self._backend is None:
            self._backend.abort()
        self.Destroy()
        
def create_and_run():    
    app = wx.App(redirect=False)
    Window(None, "Fisherman Simulation")
    app.MainLoop()
    
def main():
    create_and_run()
    return 0
    
if __name__ == "__main__":    
    exit(main())