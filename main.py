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
WINDOW_WIDTH = 160
GRAPH_HEIGHT = 22  # Slightly slimmer to fit 4 pairs comfortably

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

    def _setup_window(self):
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=BG_COLOR)
        # Initial geometry with width only; height is set in __init__
        self.root.geometry(f"{WINDOW_WIDTH}x100")

        # Draggable logic
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)
        self.root.bind("<Button-3>", lambda e: self.root.destroy())

    def _setup_ui(self):
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
            section.pack(fill='x', padx=10, pady=(4, 1))
            
            # 1. Header Row (Label + Value)
            header = tk.Frame(section, bg=BG_COLOR)
            header.pack(fill='x')
            
            tk.Label(header, text=name, font=("Helvetica", 8), 
                     bg=BG_COLOR, fg=FG_COLOR, anchor='w').pack(side='left')
            
            val_lbl = tk.Label(header, text=f"--{unit}", font=("Helvetica", 10, "bold"), 
                               bg=BG_COLOR, fg='white', anchor='e')
            val_lbl.pack(side='right')

            # 2. Sparkline for this specific metric
            graph = SparklineGraph(section, bg='#1a1a1a', height=GRAPH_HEIGHT)
            graph.pack(fill='x', pady=(2, 4))
            
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
