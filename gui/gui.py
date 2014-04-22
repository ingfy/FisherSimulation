import wx
import os
from wx.lib import intctrl
from wx.lib.splitter import MultiSplitterWindow
import worldmap
import Queue
import graphs
from FisherSimulation import do
from FisherSimulation import simulation
from FisherSimulation import util
from BufferedCanvas import BufferedCanvas
import time
import threading

DEFAULT_CONFIG_FILENAME = "config/config.js"

class PhaseResultEvent(wx.PyEvent):
    def __init__(self, result):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_RESULT_ID)
        self.result = result

class WorkerThread(threading.Thread):
    def __init__(self, simulation, notify):
        threading.Thread.__init__(self)
        
        self._simulation = simulation
        self._notify = notify
        
        self.start()
        
    def run(self):
        result = self._simulation.step()
        wx.PostEvent(self._notify, PhaseResultEvent(result))

# Button definitions
ID_START = wx.NewId()
ID_STEP = wx.NewId()
ID_RUN = wx.NewId()
ID_STOP = wx.NewId()

# Define simulation finished event
EVT_RESULT_ID = wx.NewId()

def EVT_RESULT(win, func):
    win.Connect(-1, -1, EVT_RESULT_ID, func)
        
class Controls(wx.Panel):
    def __init__(self, parent, size, listener):
        wx.Panel.__init__(self, parent, size=size)
        
        self.listener = listener

        ## Config input
        wx.StaticText(self, -1, "Config:", pos=(0, 0))
        self.configFilename = wx.FilePickerCtrl(self, 
            path=os.path.abspath(DEFAULT_CONFIG_FILENAME), pos=(60, 0), 
            size=(200, -1))
        
        ##  Start button
        self.startButton = wx.Button(self, id=ID_START, pos=(0, 30), 
            label="&Initialize")
        self.Bind(wx.EVT_BUTTON, self.listener.OnStart, self.startButton)
        
        ## Run rounds, steps inputs
        self.rounds_input = intctrl.IntCtrl(self, pos=(10, 60), size=(20, -1),
            value=0, min=0)
        self.steps_input = intctrl.IntCtrl(self, pos=(40, 60), size=(20, -1),
            value=1, min=0)
        
        ## Run button
        self.runButton = wx.Button(self, id=ID_RUN, pos=(100, 60), 
            label = "&Run")
        self.Bind(wx.EVT_BUTTON, self.OnRun, self.runButton)
        
        ##  Stop button
        self.stopButton = wx.Button(self, id=ID_STOP, pos=(0, 120), 
            label="S&top")
        self.Bind(wx.EVT_BUTTON, self.listener.OnStop, self.stopButton)
        
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
        
        self.phase_name_font = wx.Font(font_size, wx.DECORATIVE, wx.NORMAL, 
            wx.BOLD)
        
        self.phases = {
            Info.round[i]: wx.StaticText(self, 
                                label=Info.phase_names[Info.round[i]],
                                pos=(phases_x, phases_y + line_height * i))
                for i in xrange(len(Info.round))
        }
        
        for label in Info.phase_names:
            self.phases[label].SetFont(self.phase_name_font)       

        self.set_current_phase(Info.round[0])
        
    def set_current_phase(self, name):
        for label in self.phases:
            color = "red" if name == label else "black"
            self.phases[label].SetForegroundColour(color)
            self.phases[label].Refresh()
            

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

class Window(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title)
        
        # Splitters and Panels
        self.controls_map_splitter = wx.SplitterWindow(self)
        self.controls_map_splitter.SetMinimumPaneSize(300)
        
        controls_panel = wx.Panel(self.controls_map_splitter)
        map_panel = wx.Panel(self.controls_map_splitter)
        
        self.graphs_messages_splitter = wx.SplitterWindow(controls_panel)
        self.graphs_messages_splitter.SetMinimumPaneSize(50)        
        
        graphs_panel = wx.Panel(self.graphs_messages_splitter)
        messages_panel = wx.Panel(self.graphs_messages_splitter)        
        
        # World graphic
        self._graphics = worldmap.WorldMap(map_panel)
        self.graphics_sizer = wx.BoxSizer(wx.VERTICAL)
        self.graphics_sizer.Add(self._graphics, 1, wx.EXPAND)
        map_panel.SetSizerAndFit(self.graphics_sizer)
        
        # Controls panel
        self.controls = Controls(controls_panel, (300, 250), self)
        
        # Info panel
        self.info = Info(controls_panel, (300, 250))
        
        # Graph canvas
        self.graphs = graphs.Graphs(graphs_panel, (300, 300))
                
        # Messages panel
        self.messages = Messages(messages_panel, (600, 200))
        
        self.interface_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.controls_info_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.controls_info_sizer.Add(self.info, 0, wx.EXPAND)
        self.controls_info_sizer.Add(self.controls, 1, wx.EXPAND)
        
        self.messages_sizer = wx.BoxSizer(wx.VERTICAL)
        self.messages_sizer.Add(self.messages, 1, wx.EXPAND)
        messages_panel.SetSizer(self.messages_sizer)
        
        self.graphs_sizer = wx.BoxSizer(wx.VERTICAL)
        self.graphs_sizer.Add(self.graphs, 1, wx.EXPAND)
        graphs_panel.SetSizer(self.graphs_sizer)
        
        self.interface_sizer.Add(self.controls_info_sizer, 0, wx.EXPAND)
        self.interface_sizer.Add(self.graphs_messages_splitter, 1, wx.EXPAND)
        
        controls_panel.SetSizerAndFit(self.interface_sizer)
        
        self.graphs_messages_splitter.SplitHorizontally(messages_panel, 
            graphs_panel)
            
        self.controls_map_splitter.SplitVertically(controls_panel, map_panel)
        
        #self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        #self.sizer.Add(self.interface_sizer, 0, wx.EXPAND)
        #self.sizer.Add(self.graphics_sizer, 1, wx.EXPAND)       
        
                
        # Layout sizers
        #self.SetSizerAndFit(self.sizer)
        
        # Set up event handler for any worker thread results
        EVT_RESULT(self, self.OnResult)
        
        # Set up close event so timer is properly stopped
        wx.EVT_CLOSE(self, self.OnClose)        
        
        self.reset_gui()
        self.Show()
    
    def reset_gui(self):
        self.controls.reset_buttons()
        self.messages.clear()
        self.graphs.reset_data()
        
    # Event Methods
    def OnStart(self, event):
        self.controls.set_buttons_ready()
        
        self._simulation = simulation.Simulation()
        
        self._simulation.setup_config(self.controls.get_config_filename())
        self.simulation_info = self._simulation.initialize()
        
        if not self.simulation_info.interface_config.print_messages:
            self.messages.deactivate()

        self._graphics.num_max_complaints = \
            self.simulation_info.num_max_complaints
        
        self.rounds = 0
        self.steps = 0
        
        self.next_phase = "COASTPLAN"
        self.prev_phase = None
        
        self.worker = None
        
    def run(self, rounds, steps):
        assert rounds >= 0, "Rounds has to be a positive integer."
        assert steps >= 0, "Steps has to be a positive integer."
        assert steps > 0 or rounds > 0, "Rounds or steps needs to be positive."
        self.controls.set_status(rounds, steps)
        self.controls.set_buttons_processing()
        self.rounds = rounds
        self.steps = steps
        if self.worker is None:
            self.prev_phase = self.next_phase
            self.info.set_current_phase(self.next_phase)
            self.worker = WorkerThread(self._simulation, self)
        
    def OnResult(self, event):
        self.worker = None
        self.simulation_info.map.grid = util.update_map(
            self.simulation_info.map.grid, event.result.map.grid
        )
        self.next_phase = event.result.next_phase

        handle_statistics(self.graphs, event.result.round, event.result.data)
        self._graphics.set_map(self.simulation_info.map)
        if event.result.phase == "HEARING":
            self._graphics.add_votes(event.result.complaints)
        self._graphics.update()
        
        for m in event.result.messages:
            self.messages.add(str(m))
        
        newr = self.prev_phase == "LEARNING" and self.next_phase == "COASTPLAN"
        if newr:
            self._graphics.reset_votes()
        if newr and self.rounds > 0:
            self.rounds -= 1
        elif self.rounds == 0:
            self.steps -= 1

        if self.rounds > 0 or self.steps > 0:            
            self.run(self.rounds, self.steps)
        else:
            self.controls.set_buttons_ready()
        
    def OnStop(self, event):
        self.reset_gui()
        self._simulation = None
        self.simulation_info = None
        
            
    def OnClose(self, event):
        self.Destroy()
        
def handle_statistics(graphs, round, data):
    if "statistics" in data:
        for label in data["statistics"]:
            mode = data["statistics"][label].get("mode", "add")
            value = data["statistics"][label].get("value")
            graphs.add_data_point(label, round, value, mode)
    graphs.update()

def create_and_run():    
    app = wx.App(redirect=False)
    Window(None, "Fisherman Simulation")
    app.MainLoop()
    
def main():
    create_and_run()
    return 0
    
if __name__ == "__main__":    
    exit(main())