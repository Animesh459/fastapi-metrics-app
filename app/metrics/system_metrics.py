import psutil
import time
import gc
from prometheus_client import Gauge, Counter, REGISTRY

# CPU Metrics
# Renamed to clarify it's system-wide CPU utilization, as psutil.cpu_percent() without a process object is system-wide.
# If you intend to track only this process's CPU, use psutil.Process().cpu_percent().
system_cpu_utilization_gauge = Gauge('system_cpu_utilization_percent', 'System CPU utilization percentage')
process_cpu_seconds_total = Gauge('process_cpu_seconds_total', 'Total CPU time spent by the process in seconds.')

# Memory Metrics
process_resident_memory_bytes = Gauge('process_resident_memory_bytes', 'Physical memory currently used by the process in bytes.')
process_virtual_memory_bytes = Gauge('process_virtual_memory_bytes', 'Virtual memory allocated by the process in bytes.')

# Thread Count
process_threads = Gauge('process_threads', 'Total number of threads in the process.')

# Additional System Metrics
process_start_time_seconds = Gauge('process_start_time_seconds', 'Process start time as a Unix timestamp.')
process_uptime_seconds = Gauge('process_uptime_seconds', 'Process uptime in seconds.')
process_open_fds = Gauge('process_open_fds', 'Number of open file descriptors by the process.')

# Garbage Collection Statistics
# Changed to Gauge because gc.get_count() provides cumulative values.
# A Counter should only ever increase by a fixed amount or a delta for new events.
# For cumulative counts that can fluctuate (e.g., due to GC cycles), Gauge is more appropriate.
python_gc_collections_total = Gauge('python_gc_collections_total', 'Total number of garbage collections across all generations.')


def update_system_metrics():
    proc = psutil.Process() # Get process object once for efficiency

    # CPU Metrics
    system_cpu_utilization_gauge.set(psutil.cpu_percent(interval=None)) # System-wide CPU
    cpu_times = proc.cpu_times()
    total_cpu_time = cpu_times.user + cpu_times.system
    process_cpu_seconds_total.set(total_cpu_time)

    # Memory Metrics
    memory_info = proc.memory_info()
    process_resident_memory_bytes.set(memory_info.rss)
    process_virtual_memory_bytes.set(memory_info.vms)

    # Thread Count
    process_threads.set(proc.num_threads())

    # Process Start Time and Uptime
    start_time = proc.create_time()
    process_start_time_seconds.set(start_time)
    process_uptime_seconds.set(time.time() - start_time)

    # File Descriptor Usage
    try:
        process_open_fds.set(proc.num_fds())
    except psutil.AccessDenied:
        # This can happen on some systems or with limited permissions.
        # Log this error if necessary, but avoid crashing the metric collection.
        pass
    except Exception as e:
        # Catch other potential errors during num_fds() call
        print(f"Error getting file descriptors: {e}")


    # Garbage Collection Statistics
    # gc.get_count() returns a tuple (count0, count1, count2) for generations.
    # Summing them provides a total count of objects collected across all generations.
    gc_counts_sum = sum(gc.get_count())
    python_gc_collections_total.set(gc_counts_sum)

