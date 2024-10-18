from typing import Iterable, Tuple, List
import time
import os

def grouper(iterable: Iterable, n: int) -> List[Tuple]:
    """
    Splits the iterable object into groups of n pieces.

    Args:
        iterable (Iterable): The iterable object to be grouped.
        n (int): The size of each group.

    Returns:
        List[Tuple]: A list of tuples, where each tuple contains n elements from the iterable.

    Example:
        grouper('aabbcc', 2) -> [('a', 'a'), ('b', 'b'), ('c', 'c')]
    """
    args = [iter(iterable)] * n
    return list(zip(*args))

def timestamp() -> int:
    """
    Returns the current Unix timestamp.
    """
    return int(time.time())

def check_file_in_folder(folder_path: str) -> bool:
    """ 
    Check file in dir 
    """
    if os.path.exists(folder_path):
        return True
    return False


