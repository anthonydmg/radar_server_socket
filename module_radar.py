import time
import serial

class ModuleCommunication:
    """
    Simple class to communicate with the module software
    """
    def __init__(self, port, rtscts):
        self._port = serial.Serial(port, 115200, rtscts=rtscts,
                                   exclusive=True, timeout=2)

    def read_packet_type(self, packet_type):
        """
        Read any packet of packet_type. Any packages received with
        another type is discarded.
        """
        while True:
            header, payload = self._read_packet()
            if header[3] == packet_type:
                break
        return header, payload

    def _read_packet(self):
        header = self._port.read(4)
        length = int.from_bytes(header[1:3], byteorder='little')

        data = self._port.read(length + 1)
        assert data[-1] == 0xCD
        payload = data[:-1]
        return header, payload

    def register_write(self, addr, value):
        """
        Write a register
        """
        data = bytearray()
        data.extend(b'\xcc\x05\x00\xf9')
        data.append(addr)
        data.extend(value.to_bytes(4, byteorder='little', signed=False))
        data.append(0xcd)
        self._port.write(data)
        _header, payload = self.read_packet_type(0xF5)
        assert payload[0] == addr

    def register_read(self, addr):
        """
        Read a register
        """
        data = bytearray()
        data.extend(b'\xcc\x01\x00\xf8')
        data.append(addr)
        data.append(0xcd)
        self._port.write(data)
        _header, payload = self.read_packet_type(0xF6)
        assert payload[0] == addr
        return int.from_bytes(payload[1:5], byteorder='little', signed=False)

    def buffer_read(self, offset):
        """
        Read the buffer
        """
        data = bytearray()
        data.extend(b'\xcc\x03\x00\xfa\xe8')
        data.extend(offset.to_bytes(2, byteorder='little', signed=False))
        data.append(0xcd)
        self._port.write(data)

        _header, payload = self.read_packet_type(0xF7)
        assert payload[0] == 0xE8
        return payload[1:]

    def read_stream(self):
        """
        Read a stream of data
        """
        _header, payload = self.read_packet_type(0xFE)
        return payload

    @staticmethod
    def _check_error(status):
        ERROR_MASK = 0xFFFF0000
        if status & ERROR_MASK != 0:
            ModuleError(f"Error in module, status: 0x{status:08X}")

    @staticmethod
    def _check_timeout(start, max_time):
        if (time.monotonic() - start) > max_time:
            raise TimeoutError()

    def _wait_status_set(self, wanted_bits, max_time):
        """
        Wait for wanted_bits bits to be set in status register
        """
        start = time.monotonic()

        while True:
            status = self.register_read(0x6)
            self._check_timeout(start, max_time)
            self._check_error(status)

            if status & wanted_bits == wanted_bits:
                return
            time.sleep(0.1)

    def wait_start(self):
        """
        Poll status register until created and activated
        """
        ACTIVATED_AND_CREATED = 0x3
        self._wait_status_set(ACTIVATED_AND_CREATED, 3)

    def wait_for_data(self, max_time):
        """
        Poll status register until data is ready
        """
        DATA_READY = 0x00000100
        self._wait_status_set(DATA_READY, max_time)


class ModuleDistanceDetector:
    
    def __init__(self):
        self.connect()

    def connect(self):
         # Rasberry Mini Uart PORT
        port = '/dev/ttyS0'
        # XM132 is true
        flowcontrol = True
        self.com = ModuleCommunication(port, flowcontrol)
        # Make sure that module is stopped
        self.com.register_write(0x03, 0)
        # Give some time to stop (status register could be polled too)
        time.sleep(0.5)
        # Clear any errors and status
        self.com.register_write(0x3, 4)
        # Read product ID
        product_identification =  com.register_read(0x10)
        print(f'product_identification=0x{product_identification:08X}')

        version = self.com.buffer_read(0)
        print(f'Software version: {version}')
        # Set Mode read distance
        mode = 'distance'
        self.com.register_write(0x2, 0x200)
        
        # Update rate 1Hz
        self.com.register_write(0x23, 1000)
        
        # Disable UART streaming mode
        self.com.register_write(5, 0)

        # Activate and start
        self.com.register_write(3,3)

    def close(self):
        self.com.register_write(0x03, 0)

    def start(self):
        # Wait for it to start
        self.com.wait_start()
        print('Sensor activated')

        # Read out distance start
        dist_start = com.register_read(0x81)
        print(f'dist_start={dist_start / 1000} m')

        dist_length = com.register_read(0x82)
        print(f'dist_length={dist_length / 1000} m')
        duration = 100
        start = time.monotonic()

        while time.monotonic() - start < duration:
            self.com.register_write(3, 4)
            # Wait for data read
            self.com.wait_for_data(2)
            dist_count = self.com.register_read(0xB0)
            print('                                               ', end='\r')
            print(f'Detected {dist_count} peaks:', end='')
            
            list_distances = []
            for count in range(dist_count):
                dist_distance = self.com.register_read(0xB1 + 2 * count)
                dist_amplitude = self.com.register_read(0xB2 + 2 * count)
                print(f' dist_{count}_distance={dist_distance / 1000} m', end='')
                print(f' dist_{count}_amplitude={dist_amplitude}', end='')
                list_distances.append(dist_distance)
            
            if dist_count > 0:
                num_dist = len(list_distances)
                self.mean_distance = sum(list_distances) / len(num_dist)
            
            print('', end='', flush=True)
            time.sleep(0.3)
        
        self.close()

    def get_last_distance(self):
        if self.mean_distance: 
            return self.mean_distance
        return 0