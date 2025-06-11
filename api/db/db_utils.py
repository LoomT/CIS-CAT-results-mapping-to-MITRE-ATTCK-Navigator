# Helpers for db functionality

try:
    from db.models import Metadata
    from db.db_methods import get_benchmark, get_result, get_hostname
except ImportError:
    from .models import Metadata
    from .db_methods import get_benchmark, get_result, get_hostname

from datetime import datetime


# TODO: Needs to be tested
def extract_metadata(filename: str) -> Metadata:
    """
    Parse filename and return a Metadata instance.
    Expected format: HOSTNAME-BENCHMARK-TIMESTAMP-RESULT.json
    Example: LAP-TOP-Benchmark_2-20250605T132738Z-NonPassing.json
    """

    partlist = filename.split('-')

    # Should contain at least 4 parts: hostname, benchamark, time, result
    # TODO: metadata should be included in arguments body
    if len(partlist) < 4:
        print(f"Invalid filename: {partlist}")
        return Metadata(filename=filename)

    hostname_str = "-".join(partlist[0:-3])
    try:
        hostname = get_hostname(hostname_str)
    except ValueError:
        hostname = None

    time_str = partlist[-2]
    try:
        time_created = time_converter(time_str)
    except ValueError:
        time_created = None

    benchmark_str = partlist[-3]
    try:
        benchmark = get_benchmark(benchmark_str)
    except Exception as e:
        print(f"Error fetching benchmark: {e}")
        benchmark = None

    result_str = partlist[-1].replace('.json', '')
    try:
        result = get_result(result_str)
    except Exception as e:
        print(f"Error fetching result: {e}")
        result = None

    # Fine for now, as the remaining fields are added later
    return Metadata(
        filename=filename,
        hostname=hostname,
        benchmark=benchmark,
        time_created=time_created,
        result=result)


# TODO: Needs to be tested
# Could use dateutil library instead
def time_converter(time_str: str) -> datetime:
    """Converts a time from compacted iso8601 to datetime object"""

    try:
        return datetime.strptime(time_str, "%Y%m%dT%H%M%SZ")
    except ValueError as e:
        raise ValueError(f"Invalid time format: {time_str}") from e
