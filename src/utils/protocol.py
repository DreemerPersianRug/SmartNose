# {Protocol}
# Input:
# 1 byte   2 byte   3 byte   4 byte     1 byte   2 byte   3 byte   4 byte     1 byte   2 byte   3 byte   4 byte     1 byte   2 byte   3 byte   4 byte     1 byte   2 byte   3 byte   4 byte
# 01110100 01110000 10011000 [0001]0000 00000000 00000000 00000000 [0010]0000 00000000 00000000 00000000 [0011]0000 00000000 00000000 00000000 [0100]0000 00000000 00000000 00000000 [0101]0000 ...
#
# 4 byte   3 byte   2 byte   1 byte     4 byte   3 byte   2 byte   1 byte     4 byte   3 byte   2 byte   1 byte     4 byte   3 byte   2 byte   1 byte     4 byte   3 byte   2 byte   1 byte
#            ^
#            ^
#            |
# Task: Invert byte.
# In [] most significant sequance.

from . import auxiliary_modules as am

class ProtocolHandler:
    """
    Class for handling and processing protocol data.
    """

    def __init__(self, byte_data):
        """
        Initialize the ProtocolHandler with the given byte data.

        Args:
            byte_data (bytes): The byte data to be processed.
        """
        self.byte_data = byte_data
        self.hex_str = byte_data.hex()
        self.byte_arr = []
        self.four_byte_arr = []

    def _group_hex(self):
        """
        Groups hexadecimal strings into pairs of two characters.

        Example: 'ff70...c4' -> ['ff', '70', ..., 'c4']

        Returns:
            list: A list of hexadecimal pairs.
        """
        return [''.join(i) for i in am.grouper(self.hex_str, 2)]

    def _rearrange_array(self, group):
        """
        Rearranges the elements of the array according to the index xor 3.

        Example: index: 1 2 3 4 5 6 7 8 ... -> 4 3 2 1 8 7 6 5 ...

        Args:
            group (list): The list of hexadecimal pairs.

        Returns:
            list: The rearranged list of hexadecimal pairs.
        """
        return [group[index ^ 3] for index in range(len(group))]

    def _convert_to_bin(self, byte_arr):
        """
        Converts hexadecimal strings to binary.

        Args:
            byte_arr (list): The list of hexadecimal pairs.

        Returns:
            list: The list of binary strings.
        """
        return [format(int(num, 16), "08b") for num in byte_arr]

    def _group_bin(self, bin_arr):
        """
        Groups binary strings into groups of four elements.

        Args:
            bin_arr (list): The list of binary strings.

        Returns:
            list: The list of grouped binary strings.
        """
        return [''.join(i) for i in am.grouper(bin_arr, 4)]

    def process(self):
        """
        Main method to process the protocol data and get the result.

        Returns:
            list: The processed binary array.
        """
        group = self._group_hex()
        rearranged_arr = self._rearrange_array(group)
        bin_arr = self._convert_to_bin(rearranged_arr)
        self.four_byte_arr = self._group_bin(bin_arr)
        return self.four_byte_arr

    @staticmethod
    def parse_num(input_data):
        """
        Parses the first 4 bits of the string and returns them as a number.
        """
        return int(input_data[:4], base=2)

    @staticmethod
    def parse_elem(input_data):
        """
        Parses the remaining bits of the string and returns them as a number.
        """
        return int(input_data[4:], base=2)