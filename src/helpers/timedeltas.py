from datetime import timedelta


def convert_td(td: timedelta) -> int:
    """
    Convert a timedelta to milliseconds rounded to nearest int
    :param td: timedelta to be converted
    :return: td in milliseconds as integer
    """
    return int(td.total_seconds() * 1000)
