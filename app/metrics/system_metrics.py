# app/metrics/system_metrics.py
import psutil
from prometheus_client import Gauge, REGISTRY # Ensure REGISTRY is imported or defined as needed

cpu_utilization_gauge = Gauge('process_cpu_utilization_percent', 'Process CPU utilization percentage')
process_threads = Gauge('process_threads', 'Total number of threads in the process.')

def update_system_metrics():
    cpu_utilization_gauge.set(psutil.cpu_percent(interval=None))
    process_threads.set(psutil.Process().num_threads())