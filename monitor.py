import psutil
import subprocess
from typing import Dict, Optional

# Constants for sensor names
CPU_TCTL = 'CPU Tctl'
CPU_TCCD1 = 'CPU Tccd1'
GPU_TEMP = 'GPU'
GPU_POWER = 'GPU Power'
RAM_USAGE = 'RAM Usage'

def get_all_metrics() -> Dict[str, Optional[float]]:
    """
    Fetches system temperatures, power metrics, and RAM usage.
    """
    metrics = {CPU_TCTL: None, CPU_TCCD1: None, GPU_TEMP: None, GPU_POWER: None, RAM_USAGE: None}
    
    try:
        temps = psutil.sensors_temperatures()
        
        # RAM usage percentage
        metrics[RAM_USAGE] = psutil.virtual_memory().percent
        
        # CPU Metrics (AMD k10temp)
        if 'k10temp' in temps:
            for entry in temps['k10temp']:
                if entry.label == 'Tctl':
                    metrics[CPU_TCTL] = entry.current
                elif entry.label == 'Tccd1':
                    metrics[CPU_TCCD1] = entry.current
        
        # GPU Metrics (Temp and Power)
        gpu_data = _get_gpu_info()
        metrics[GPU_TEMP] = gpu_data.get('temp')
        metrics[GPU_POWER] = gpu_data.get('power')

    except Exception:
        pass
        
    return metrics

def _get_gpu_info() -> Dict[str, Optional[float]]:
    """Helper to find GPU info via nvidia-smi."""
    info = {'temp': None, 'power': None}
    try:
        # Querying both temperature and power draw
        res = subprocess.run(
            ['nvidia-smi', '--query-gpu=temperature.gpu,power.draw', '--format=csv,noheader,nounits'], 
            capture_output=True, text=True, check=True, timeout=1
        )
        parts = res.stdout.strip().split(',')
        if len(parts) >= 2:
            info['temp'] = float(parts[0].strip())
            info['power'] = float(parts[1].strip())
    except (subprocess.SubprocessError, FileNotFoundError, ValueError):
        # Fallback for temperature ONLY if nvidia-smi (dedicated tool) fails.
        # We search specifically for dedicated driver labels first.
        temps = psutil.sensors_temperatures()
        for name in ['nvidia', 'amdgpu', 'nouveau']:
            if name in temps and temps[name]:
                info['temp'] = temps[name][0].current
                break
    return info
