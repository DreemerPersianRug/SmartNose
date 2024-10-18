from serial.tools import list_ports

import serial

class SerialPortHandler:
    def __init__(self, logger, port_name, baud_rate=57600):
        """
        Initialize the SerialPortHandler with the given port name and baud rate.

        Args:
            port_name (str): The name of the COM port.
            baud_rate (int): The baud rate for serial communication.
        """
        self.port_name = port_name
        self.baud_rate = baud_rate
        self.serial_connection = None
        self.__logger = logger

    def open_serial_connection(self):
        if self.port_name:
            self.serial_connection = serial.Serial(self.port_name, self.baud_rate, timeout=2)
        else:
            self.__logger.warning('Port name is not specified.')

    def read_data(self):
        if self.serial_connection:
            data = self.serial_connection.read(size=32)
            return data
        else:
            self.__logger.warning('Serial connection is not open.')
        return None

    def close_serial_connection(self):
        if self.serial_connection:
            self.serial_connection.close()

class PortScanner:
    @staticmethod
    def port_list():
        """
        Scans and returns a list of available COM ports.

        Returns:
            list: A list of available COM ports.
        """
        port_list = [p.device for p in list_ports.comports()]
        return port_list