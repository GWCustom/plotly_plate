
import re

def generate_row_labels(n_rows):

    """
    Generate row labels for a plate based on the number of rows.
    The labels will be in the format A, B, ..., Z, AA, AB, ..., AZ, BA, ..., ZZ,
    continuing in a similar pattern for the specified number of rows.

    Args:
        n_rows (int): The number of rows for which to generate labels.

    Returns:
        List[str]: A list of row labels.
    """

    labels = []
    i = 0
    while len(labels) < n_rows:
        label = ''
        temp = i
        while True:
            label = chr(ord('A') + temp % 26) + label
            temp = temp // 26 - 1
            if temp < 0:
                break
        labels.append(label)
        i += 1
    return labels


def normalize_well(well):
    """
    This function validates the names of wells, and splits the letter
    and number portions of the well names for downstream processing.
    It supports well names with 1 or 2 letters followed by a number,
    with or without leading zeros.

    Args:
        well (str): The name of the well, e.g. "A1", "B12", F01, AA02, etc.

    Returns:
        (tuple): A tuple containing the row letters and column number.

    Raises:
        ValueError: raised if the well name does not match the expected format
    """

    match = re.match(r"^([A-Z]+)0*(\d+)$", well.strip().upper())
    if not match:
        raise ValueError(f"Invalid well name: {well}")

    row_letters, col_number = match.groups()
    if len(row_letters) > 2:
        raise ValueError(f"Row label too long: '{row_letters}' (max 2 characters allowed)")

    return row_letters, int(col_number)


def pad_or_check(name, lst, n_wells):
    """ 
    Verifies that the length of the provided list is less than or equal to the
    total number of wells, and pads the list with None values if necessary,
    ensuring that the list has exactly `n_wells` elements.

    Args:
        name (str): The name of the list being checked or padded.
        lst (list): The list to check or pad.
        n_wells (int): The total number of wells.

    Returns:
        list: The padded list with None values if necessary.

    Raises:
        ValueError: If the list length exceeds the number of wells.
    """

    if lst is None:
        return [None] * n_wells
    if len(lst) > n_wells:
        raise ValueError(f"{name} length ({len(lst)}) exceeds total wells ({n_wells}).")
    return lst + [None] * (n_wells - len(lst))
