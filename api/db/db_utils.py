# Helpers for db functionality

try:
    from db.models import Metadata
    from db.db_methods import get_benchmark, get_result, get_hostname
except ImportError:
    from .models import Metadata
    from .db_methods import get_benchmark, get_result, get_hostname

from datetime import datetime


# TODO: Needs to be tested
def extract_metadata(filename: str, bench_type: str) -> Metadata:
    """
    Extracts metadata from a given filename.

    This function analyzes the input filename and
    extracts various metadata elements,
    including hostname, benchmark type, time of creation, and result status.
    The structure of the filename is expected to contain
    certain delimiters and specific formatting.

    Expected format: HOSTNAME-BENCHMARK-TIMESTAMP-RESULT.json
    Example: LAP-TOP-Benchmark_2-20250605T132738Z-NonPassing.json

    :param filename: Input filename to extract metadata from.
    :param bench_type: Type of benchmark expected in the filename structure.
    :return: An instance of `Metadata` containing details such as hostname,
    benchmark, time_created, and result extracted from the filename.
    :raises ValueError: If the filename structure does not match
    what is expected.
    """

    hostname_and_rest = filename.removesuffix('.json').split(f'-{bench_type}-')
    if len(hostname_and_rest) != 2:
        raise ValueError(f"Invalid filename format: {filename}")

    hostname_str = hostname_and_rest[0]
    try:
        hostname = get_hostname(hostname_str)
    except ValueError:
        hostname = None

    time_and_result = hostname_and_rest[1].split('-')
    if len(time_and_result) != 1 and len(time_and_result) != 2:
        raise ValueError(f"Invalid filename format: {filename}")

    time_str = time_and_result[0]
    try:
        time_created = time_converter(time_str)
    except ValueError:
        time_created = None

    benchmark_str = bench_type
    try:
        benchmark = get_benchmark(benchmark_str)
    except Exception as e:
        print(f"Error fetching benchmark: {e}")
        benchmark = None

    if len(time_and_result) == 2:
        result_str = time_and_result[1]
    else:
        result_str = "Passing"
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
