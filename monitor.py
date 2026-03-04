import psutil
import os

import subprocess

def get_all_metrics():
    """
    Returns a dictionary of { 'CPU Tctl': temp, 'CPU Tccd1': temp, 'GPU': temp }
    """
    metrics = {'CPU Tctl': None, 'CPU Tccd1': None, 'GPU': None}
    try:
        temps = psutil.sensors_temperatures()
        
        # AMD CPU (k10temp)
        if 'k10temp' in temps:
            for entry in temps['k10temp']:
                if entry.label == 'Tctl':
                    metrics['CPU Tctl'] = entry.current
                elif entry.label == 'Tccd1':
                    metrics['CPU Tccd1'] = entry.current
        
        # NVIDIA GPU
        try:
            # First try nvidia-smi (most reliable for NVIDIA)
            res = subprocess.run(['nvidia-smi', '--query-gpu=temperature.gpu', '--format=csv,noheader,nounits'], 
                               capture_output=True, text=True, check=True)
            metrics['GPU'] = float(res.stdout.strip())
        except (subprocess.SubprocessError, FileNotFoundError, ValueError):
            # Fallback to psutil (might show up as 'amdgpu' or 'nvidia' on some systems)
            for name in ['amdgpu', 'nvidia', 'nouveau']:
                if name in temps and temps[name]:
                    metrics['GPU'] = temps[name][0].current
                    break

    except Exception:
        pass
    return metrics

if __name__ == "__main__":
    temp = get_cpu_temp()
    if temp is not None:
        print(f"Current CPU Temp: {temp:.1f}°C")
    else:
        print("Could not retrieve CPU temperature.")
