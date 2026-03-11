import tkinter as tk
import collections
from typing import List, Optional

class SparklineGraph(tk.Canvas):
    """A lightweight sparkline graph component for Tkinter."""
    
    def __init__(self, master, width=150, height=50, max_points=60, 
                 min_scale=30, max_scale=65, **kwargs):
        super().__init__(master, width=width, height=height, 
                         highlightthickness=0, bd=0, **kwargs)
        
        self.max_points = max_points
        self.history = collections.deque(maxlen=max_points)
        
        # UI Config
        self.line_color = '#00FF41'
        self.fill_color = '#00FF41'
        self.min_scale = min_scale
        self.max_scale = max_scale

    def add_point(self, value: Optional[float]):
        """Adds a data point and triggers a redraw."""
        if value is not None:
            self.history.append(value)
            self.draw()

    def draw(self):
        """Redraws the graph based on the current history."""
        self.delete("all")
        if len(self.history) < 2:
            return

        w = self.winfo_width()
        if w <= 1: w = int(self.cget('width'))
        h = self.winfo_height()
        if h <= 1: h = int(self.cget('height'))

        # Calculate scale (Auto-adjusting window)
        cur_min = min(min(self.history), self.min_scale)
        cur_max = max(max(self.history), self.max_scale)
        range_val = cur_max - cur_min
        if range_val == 0: range_val = 1

        points = []
        step = w / (self.max_points - 1)
        
        # Calculate X, Y coordinates
        for i, val in enumerate(self.history):
            x = i * step
            # Higher value = lower Y (0 is top)
            y = h - ((val - cur_min) / range_val * h)
            points.append((x, y))

        # 1. Draw gradient fill (Polygon)
        fill_points = [(0, h)] + points + [(points[-1][0], h)]
        self.create_polygon(fill_points, fill=self.fill_color, 
                            stipple='gray25', outline='')

        # 2. Draw sparkline
        self.create_line(points, fill=self.line_color, width=1.5, smooth=True)
