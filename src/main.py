import init
from utils import PortScanner, SerialPortHandler
from utils import ProtocolHandler

available_ports = PortScanner.port_list()
print(available_ports)

actual_port = input('>:')

serial = SerialPortHandler(init.logger, actual_port)
serial.open_serial_connection()


try:
    while True:
        try:
            data = serial.read_data()
            protocol = ProtocolHandler(data)
            bin_arr = protocol.process()
            values = list(map(ProtocolHandler.parse_elem, bin_arr))
            numbers = list(map(ProtocolHandler.parse_num, bin_arr))
            print(list(zip(numbers, values)))
        except:
            continue
    serial.close_serial_connection()
except Exception as e:
    print(str(e))
    serial.close_serial_connection()

