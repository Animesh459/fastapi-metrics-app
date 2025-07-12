import psutil
import time
import gc
from prometheus_client import Gauge, Counter, CollectorRegistry, generate_latest

# Create a custom CollectorRegistry for your application's metrics.
# This isolates your metrics from the default global registry and prevents
# "Duplicated timeseries" errors, especially in environments with reloaders.
APP_REGISTRY = CollectorRegistry()

# System-wide CPU Utilization
# Registered with APP_REGISTRY
system_cpu_utilization_gauge = Gauge(
    'system_cpu_utilization_percent',
    'System CPU utilization percentage',
    registry=APP_REGISTRY
)

# Process CPU Metrics
# Registered with APP_REGISTRY
process_cpu_seconds_total = Gauge(
    'process_cpu_seconds_total',
    'Total CPU time spent by the process in seconds.',
    registry=APP_REGISTRY
)

# Process Memory Metrics
# Registered with APP_REGISTRY
process_resident_memory_bytes = Gauge(
    'process_resident_memory_bytes',
    'Physical memory currently used by the process in bytes.',
    registry=APP_REGISTRY
)
process_virtual_memory_bytes = Gauge(
    'process_virtual_memory_bytes',
    'Virtual memory allocated by the process in bytes.',
    registry=APP_REGISTRY
)

# Process Thread Count
# Registered with APP_REGISTRY
process_threads = Gauge(
    'process_threads',
    'Total number of threads in the process.',
    registry=APP_REGISTRY
)

# Process Start Time and Uptime
# Registered with APP_REGISTRY
process_start_time_seconds = Gauge(
    'process_start_time_seconds',
    'Process start time as a Unix timestamp.',
    registry=APP_REGISTRY
)
process_uptime_seconds = Gauge(
    'process_uptime_seconds',
    'Process uptime in seconds.',
    registry=APP_REGISTRY
)

# Process File Descriptor Usage
# Registered with APP_REGISTRY
process_open_fds = Gauge(
    'process_open_fds',
    'Number of open file descriptors by the process.',
    registry=APP_REGISTRY
)

# Garbage Collection Statistics (Python-specific)
# Registered with APP_REGISTRY
python_gc_collections_total = Gauge(
    'python_gc_collections_total',
    'Total number of garbage collections across all generations.',
    registry=APP_REGISTRY
)


def update_system_metrics():
    """
    Updates the Prometheus gauges with current system and process metrics.
    All metrics are explicitly collected using psutil or gc and registered
    with the custom APP_REGISTRY.
    """
    proc = psutil.Process() # Get process object once for efficiency

    # System-wide CPU utilization
    system_cpu_utilization_gauge.set(psutil.cpu_percent(interval=None))

    # Process CPU Metrics
    cpu_times = proc.cpu_times()
    total_cpu_time = cpu_times.user + cpu_times.system
    process_cpu_seconds_total.set(total_cpu_time)

    # Process Memory Metrics
    memory_info = proc.memory_info()
    process_resident_memory_bytes.set(memory_info.rss)
    process_virtual_memory_bytes.set(memory_info.vms)

    # Process Thread Count
    process_threads.set(proc.num_threads())

    # Process Start Time and Uptime
    start_time = proc.create_time()
    process_start_time_seconds.set(start_time)
    process_uptime_seconds.set(time.time() - start_time)

    # Process File Descriptor Usage
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
    gc_counts_sum = sum(gc.get_count())
    python_gc_collections_total.set(gc_counts_sum)

