import tkinter as tk
from monitor import get_all_metrics
from graph import SparklineGraph

# Configuration Constants
REFRESH_MS = 2000
BG_COLOR = '#121212'
FG_COLOR = '#888888'
ACCENT_COLOR = '#00FF41'
WARNING_COLOR = '#FFCC00'
CRITICAL_COLOR = '#FF3B30'
WINDOW_WIDTH = 220
GRAPH_HEIGHT = 28  # Slightly taller for better readability

class SystemMonitorWidget:
    """The main orchestration widget for the system monitor."""
    
    def __init__(self, root: tk.Tk):
        self.root = root
        self._setup_window()
        self._setup_ui()
        
        # Calculate and set the perfect height based on content
        self.root.update_idletasks()
        height = self.root.winfo_reqheight()
        self.root.geometry(f"{WINDOW_WIDTH}x{height}+100+100")
        
        self.update_loop()

    def close_app(self, event=None):
        print(f"Closing app via event: {event}")
        self.root.destroy()

    def _setup_window(self):
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=BG_COLOR)
        # Initial geometry with width only; height is set in __init__
        self.root.geometry(f"{WINDOW_WIDTH}x100")

        # Draggable logic (Left Click)
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)
        
        # Multiple Exit Paths (Global Bindings)
        self.root.bind_all("<Button-3>", self.close_app)          # Simple Right Click
        self.root.bind_all("<Control-Button-3>", self.close_app)  # Ctrl + Right Click
        self.root.bind_all("<q>", self.close_app)                 # 'q' key
        self.root.bind_all("<Escape>", self.close_app)            # 'Escape' key

    def _setup_ui(self):
        # 0. Title Bar / Header with Close Button
        title_bar = tk.Frame(self.root, bg='#1a1a1a', height=24)
        title_bar.pack(fill='x', side='top')
        title_bar.bind("<Button-1>", self.start_move)
        title_bar.bind("<B1-Motion>", self.do_move)
        
        # System Label
        tk.Label(title_bar, text=" SYSTEM MONITOR", font=("Helvetica", 7, "bold"),
                 bg='#1a1a1a', fg='#555555').pack(side='left', padx=5)
        
        # The 'X' Button
        close_btn = tk.Label(title_bar, text="✕", font=("Helvetica", 10, "bold"),
                             bg='#1a1a1a', fg='#888888', cursor="hand2", padx=8)
        close_btn.pack(side='right')
        # Use lambda to avoid event object if not needed, or just pass to close_app
        close_btn.bind("<Button-1>", self.close_app)
        
        # Hover effect for X
        close_btn.bind("<Enter>", lambda e: close_btn.config(fg=CRITICAL_COLOR, bg='#333333'))
        close_btn.bind("<Leave>", lambda e: close_btn.config(fg='#888888', bg='#1a1a1a'))

        self.metric_controls = {}
        
        # Updated metric list to include GPU Power and RAM Usage
        metrics = [
            ('CPU Tctl', '°C'), 
            ('CPU Tccd1', '°C'), 
            ('GPU', '°C'), 
            ('GPU Power', 'W'),
            ('GPU VRAM', '%'),
            ('RAM Usage', '%')
        ]
        
        for name, unit in metrics:
            section = tk.Frame(self.root, bg=BG_COLOR)
            section.pack(fill='x', padx=10, pady=(5, 2))
            
            # 1. Header Row (Label + Value)
            header = tk.Frame(section, bg=BG_COLOR)
            header.pack(fill='x')
            header.bind("<Button-1>", self.start_move)
            header.bind("<B1-Motion>", self.do_move)
            
            lbl_name = tk.Label(header, text=name, font=("Helvetica", 9), 
                                bg=BG_COLOR, fg=FG_COLOR, anchor='w')
            lbl_name.pack(side='left')
            lbl_name.bind("<Button-1>", self.start_move)
            lbl_name.bind("<B1-Motion>", self.do_move)
            
            val_lbl = tk.Label(header, text=f"--{unit}", font=("Helvetica", 11, "bold"), 
                               bg=BG_COLOR, fg='white', anchor='e')
            val_lbl.pack(side='right')
            val_lbl.bind("<Button-1>", self.start_move)
            val_lbl.bind("<B1-Motion>", self.do_move)

            # Define scales per unit for better visualization
            m_min, m_max = 30, 85
            if unit == '%': m_min, m_max = 0, 100
            elif unit == 'W': m_min, m_max = 0, 150

            # 2. Sparkline for this specific metric
            graph = SparklineGraph(section, bg='#1a1a1a', height=GRAPH_HEIGHT,
                                   min_scale=m_min, max_scale=m_max)
            graph.pack(fill='x', pady=(2, 4))
            graph.bind("<Button-1>", self.start_move)
            graph.bind("<B1-Motion>", self.do_move)
            
            # Store references and unit info
            self.metric_controls[name] = {
                'label': val_lbl,
                'graph': graph,
                'unit': unit
            }

    def _get_color(self, value: float, name: str) -> str:
        unit = self.metric_controls[name]['unit']
        # Temperature thresholds
        if '°C' in unit:
            if value < 55: return ACCENT_COLOR
            if value < 75: return WARNING_COLOR
            return CRITICAL_COLOR
        # RAM usage thresholds
        elif '%' in unit:
            if value < 70: return ACCENT_COLOR
            if value < 85: return WARNING_COLOR
            return CRITICAL_COLOR
        # Power thresholds (example: green < 100W, amber < 250W, red > 250W)
        else:
            if value < 100: return ACCENT_COLOR
            if value < 250: return WARNING_COLOR
            return CRITICAL_COLOR

    def update_loop(self):
        """Main update loop routing data to individual graphs."""
        metrics = get_all_metrics()
        
        for name, value in metrics.items():
            controls = self.metric_controls.get(name)
            if not controls: continue
            
            lbl = controls['label']
            graph = controls['graph']
            unit = controls['unit']
            
            if value is not None:
                # Handle dictionary values for RAM Usage
                if isinstance(value, dict):
                    percent = value['percent']
                    used = value['used']
                    total = value['total']
                    color = self._get_color(percent, name)
                    lbl.config(text=f"{used:.1f}/{total:.0f}G ({percent:.0f}%)", fg=color)
                    graph.add_point(percent)
                else:
                    color = self._get_color(value, name)
                    lbl.config(text=f"{value:.1f}{unit}", fg=color)
                    graph.add_point(value)
                
                # Update graph visuals
                graph.line_color = color
                graph.fill_color = color
            else:
                lbl.config(text=f"N/A", fg='#444444')

        self.root.after(REFRESH_MS, self.update_loop)

    def start_move(self, event): self.x, self.y = event.x, event.y
    def do_move(self, event):
        x = self.root.winfo_x() + (event.x - self.x)
        y = self.root.winfo_y() + (event.y - self.y)
        self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SystemMonitorWidget(root)
    root.mainloop()
