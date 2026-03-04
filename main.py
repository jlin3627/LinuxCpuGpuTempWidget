import tkinter as tk
from monitor import get_all_metrics

class CPUTempWidget:
    def __init__(self, root):
        self.root = root
        self.root.title("System Monitor")
        
        # Window configuration
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg='#121212') 

        # Layout settings: 3 rows of data
        self.root.geometry("140x90+100+100")

        self.rows = {}
        for metric in ['CPU Tctl', 'CPU Tccd1', 'GPU']:
            frame = tk.Frame(root, bg='#121212')
            frame.pack(fill='x', padx=10, pady=2)
            
            label = tk.Label(frame, text=metric, font=("Helvetica", 8), 
                             bg='#121212', fg='#888888', width=8, anchor='w')
            label.pack(side='left')
            
            value = tk.Label(frame, text="--°C", font=("Helvetica", 10, "bold"), 
                             bg='#121212', fg='white', width=6, anchor='e')
            value.pack(side='right')
            
            self.rows[metric] = value

        # Draggable
        self.root.bind("<Button-1>", self.start_move)
        self.root.bind("<B1-Motion>", self.do_move)
        self.root.bind("<Button-3>", lambda e: self.root.destroy())

        self.update_all()

    def update_all(self):
        metrics = get_all_metrics()
        for metric, value_label in self.rows.items():
            temp = metrics.get(metric)
            if temp is not None:
                value_label.config(text=f"{temp:.1f}°C")
                # Color coding based on value
                if temp < 55: color = '#00FF41'
                elif temp < 75: color = '#FFCC00'
                else: color = '#FF3B30'
                value_label.config(fg=color)
            else:
                value_label.config(text="N/A", fg='#444444')
        
        self.root.after(2000, self.update_all)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

if __name__ == "__main__":
    root = tk.Tk()
    app = CPUTempWidget(root)
    root.mainloop()
