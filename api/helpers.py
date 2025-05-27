# Helpers for db functionality

from .database import FileMetadata


def extract_metadata(file) -> FileMetadata:
    """Extracts metadata from a FileStorage object.
    Currently only uses info from the filename,
    but could also extract data from the file itself"""

    # Split the filename into useful parts (like hostname and time)
    # Would need some sort of better parsing, as right now it
    # Might be broken if filename contains more underscores
    # (json result does not contain the data needed unline html)
    partlist = file.filename.split('-')

    # Should contain at least 3 parts: hostname, benchamark, time
    if len(partlist) < 4:
        print(f"Invalid filename: {file.filename}")
        print(f"Filename parts: {partlist}")
        raise ValueError("Invalid filename format")

    hostname = "-".join(partlist[0:-3])

    time = timeConverter(partlist[-2])
    result = partlist[-1].replace('.json', '')

    # Fine for now, as the remaining fields are added later
    return FileMetadata("", "", hostname, "", time, result, [])


def timeConverter(time_str: str) -> str:
    """Converts a time from compacted iso8601 to uncompacted ."""

    # 15 values for numbers, then at least 1 for timezone (Z or +00:00)
    if len(time_str) <= 15:
        print(f"Invalid time string: {time_str}")
        raise ValueError("Time string must be at least 15 characters long")

    return (f"{time_str[:4]}-{time_str[4:6]}-{time_str[6:8]}T"
            f"{time_str[9:11]}:{time_str[11:13]}:{time_str[13:]}")
