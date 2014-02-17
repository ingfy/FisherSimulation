import wx

class WorldMap(wx.Panel):
    size = (400, 400)
    _data = None
    BufferBmp = None
    timer = None

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, size = self.size)
        self.SetBackgroundColour("white")
        
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        
    def start(self, backend):
        self.backend = backend
        self._data = None
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnUpdate)
        self.timer.Start(milliseconds=500, oneShot=False)        
        
    # Event methods    
    def OnUpdate(self, event):        
        self._data = { "map": self.backend.get_map() }
        self.Refresh(eraseBackground=False)
        self.Update()
        
    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        self.DoDraw(dc)
        
    def DoDraw(self, dc):
        if self._data is None: return
        try:
            dc.Clear()            
            map = self._data["map"]
            num_hor, num_ver = (len(map.grid), len(map.grid[0]))
            w, h = self.size
            cell_w, cell_h = (w / num_hor, h / num_hor)
            
            grid_color = wx.Colour(0, 0, 0)
            dc.SetPen(wx.Pen(grid_color, 1))
            
            # Draw grid
            ## Horizontal lines
            for x in xrange(num_hor + 1):
                dc.DrawLine(0, cell_w * x, h, cell_w * x)
            
            ## Vertical lines
            for y in xrange(num_ver + 1):
                dc.DrawLine(cell_h * y, 0, cell_h * y, w) 
            
            
            fish_color = wx.Colour(0, 0, 255)
            fish_pen = wx.Pen(fish_color, 1)
            fish_brush = wx.Brush(fish_color, wx.SOLID)
            
            boat_color = wx.Colour(100, 100, 100)
            boat_pen = wx.Pen(boat_color, 1)
            boat_brush = wx.Brush(boat_color, wx.SOLID)
            
            # Draw entities
            for i in xrange(num_hor):
                for j in xrange(num_ver):
                    x, y = (cell_w * i, cell_h * j)
                    if map.grid[i][j].spawning: 
                        draw_fish_top_left(dc, x, y, cell_w, cell_h, fish_pen, fish_brush)
                    if map.grid[i][j].fisherman:
                        draw_boat_bottom_right(dc, x, y, cell_w, cell_h, boat_pen, boat_brush)
            
            
            return True
            
        except Exception, e:
            print e
            return False
        
    def stop_timer(self):
        if not self.timer is None:
            self.timer.Stop()
            
          
def draw_boat_center(dc, x, y, cell_w, cell_h, p, b):
    dc.SetPen(p)
    dc.SetBrush(b)
    # Draw boat bottom
    dc.DrawArc(x - cell_w / 3, y, x + cell_w / 3, y, x, y)
    # Draw sail
    dc.DrawPolygon([wx.Point(x - cell_w / 4, y - cell_h / 8),
                    wx.Point(x + cell_w / 4, y - cell_h / 8),
                    wx.Point(x,              y - cell_h / 8 - cell_h / 4)])
    # Draw mast
    dc.DrawLine(x, y, x, y - cell_h / 8)
                    
def draw_boat_bottom_right(dc, x, y , cell_w, cell_h, p, b):
    ox = cell_w - cell_w / 3
    oy = cell_h - cell_h / 8 - cell_h / 4
    draw_boat_center(dc, ox + x, oy + y, cell_w, cell_h, p, b)
            
def draw_fish_center(dc, x, y, cell_w, cell_h, p, b):
    dc.SetPen(p)
    dc.SetBrush(b)
    # Draw body
    dc.DrawArc(x - cell_w / 3, y, x + cell_w / 3, y, x, y - cell_h / 6)
    dc.DrawArc(x + cell_w / 3, y, x - cell_w / 3, y, x, y + cell_h / 6)
    ## right tip is located at (x + cell_w / 3, y)
    # Draw tail
    dc.DrawPolygon([wx.Point(x + cell_w / 3 + cell_w / 5, y - cell_h / 5),
                    wx.Point(x + cell_w / 3,              y),
                    wx.Point(x + cell_w / 3 + cell_w / 5, y + cell_h / 5)])
        
def draw_fish_top_left(dc, x, y, cell_w, cell_h, p, b):  # Offset from top left corner
    ox = cell_w / 3
    oy = cell_h / 5
    draw_fish_center(dc, ox + x, oy + y, cell_w, cell_h, p, b)