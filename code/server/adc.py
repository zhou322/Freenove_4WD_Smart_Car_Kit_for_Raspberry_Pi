import smbus
import time


class ADC:
    ADDRESS = 0x48
    smb = smbus.SMBus(1)
    _instance = None

    def __new__(cls):
        # I2C address of the device
        if cls is not cls._instance:
            try:
                for i in range(3):
                    aa = cls.smb.read_byte_data(cls.ADDRESS, 0xf4)
                    if aa < 150:
                        return super(ADC, cls).__new__(AdcPCF8591)
                    else:
                        return super(ADC, cls).__new__(AdcADS7830)
            finally:
                cls.smb.close()
        else:
            return cls._instance

    def __init__(self):
        self.bus = smbus.SMBus(1)

    def recv(self, channel: int) -> float:
        """Load in the file for extracting text."""
        pass

    def destroy(self):
        self.bus.close()


class AdcPCF8591(ADC):
    def __init__(self):
        # I2C address of the device
        super().__init__()
        # PCF8591 Command
        self.PCF8591_CMD = 0x40  # Command

    def analog_read(self, chn):  # PCF8591 read ADC value,chn:0,1,2,3
        value = [0, 0, 0, 0, 0, 0, 0, 0, 0]
        for i in range(9):
            value[i] = self.bus.read_byte_data(self.ADDRESS, self.PCF8591_CMD + chn)
        value = sorted(value)
        return value[4]

    def recv(self, channel):  # PCF8591 write DAC value
        while True:
            value1 = self.analog_read(channel)  # read the ADC value of channel 0,1,2,
            value2 = self.analog_read(channel)
            if value1 == value2:
                break
        voltage = value1 / 256.0 * 3.3  # calculate the voltage value
        voltage = round(voltage, 2)
        return voltage


class AdcADS7830(ADC):
    def __init__(self):
        # Get I2C bus
        super().__init__()
        # ADS7830 Command
        self.ADS7830_CMD = 0x84  # Single-Ended Inputs

    def recv(self, channel):
        """Select the Command data from the given provided value above"""
        command_set = self.ADS7830_CMD | ((((channel << 2) | (channel >> 1)) & 0x07) << 4)
        self.bus.write_byte(self.ADDRESS, command_set)
        while True:
            value1 = self.bus.read_byte(self.ADDRESS)
            value2 = self.bus.read_byte(self.ADDRESS)
            if value1 == value2:
                break
        voltage = value1 / 255.0 * 3.3  # calculate the voltage value
        voltage = round(voltage, 2)
        return voltage


def main():
    print('Program is starting ... ')
    adc = ADC()
    try:
        while True:
            left_idr = adc.recv(0)
            print(left_idr)
            right_idr = adc.recv(1)
            print(right_idr)
            power = adc.recv(2) * 3
            print(power)
            time.sleep(1)
            print('----')
    except KeyboardInterrupt:
        adc.destroy()


# Main program logic follows:
if __name__ == '__main__':
    main()
