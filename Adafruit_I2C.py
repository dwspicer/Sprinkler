__author__ = 'Dave Spicer'
import re
import smbus

# ===========================================================================
# I2C Class
# ===========================================================================

class Adafruit_I2C(object):
    def getPiRevision():
        try:
            with open('/proc/cpuinfo', 'r') as infile:
                for line in infile:
                    match = re.match('Revision\s+:\s+.*(\w{4})$', line)
                    if match and match.group(1) in ['0000', '0002', '0003']:
                        return 1
                    elif match:
                        return 2
                return 0
        except:
            return 0
    def getPiI2CBusNumber():
        return 1 if Adafruit_I2C.getPiRevision() > 1 else 0
    def __init__(self, address, busnum=-1, debug=False):
        self.address = address
        self.bus = smbus.SMBus(busnum if busnum >= 0 else Adafruit_I2C.getPiI2CBusNumber())
        self.debug = debug
    def reverseByteOrder(self, data):
        byteCount = len(hex(data)[2:].replace('L','')[::2])
        val       = 0
        for i in range(byteCount):
            val    = (val << 8) | (data & 0xff)
            data >>= 8
        return val
    def errMsg(self):
        print ("Error accessing 0x%02X: Check your I2C address") % self.address
        return -1
    def write8(self, reg, value):
        try:
            self.bus.write_byte_data(self.address, reg, value)
            if self.debug:
                print ("I2C: Wrote 0x%02X to register 0x%02X") % (value, reg)
        except IOError:
            return self.errMsg()
    def write16(self, reg, value):
        try:
            self.bus.write_word_data(self.address, reg, value)
            if self.debug:
                print ("I2C: Wrote 0x%02X to register pair 0x%02X,0x%02X") % (value, reg, reg+1)
        except IOError:
            return self.errMsg()
    def writeRaw8(self, value):
        try:
            self.bus.write_byte(self.address, value)
            if self.debug:
                print ("I2C: Wrote 0x%02X") % value
        except IOError:
            return self.errMsg()
    def writeList(self, reg, list):
        try:
            if self.debug:
                print ("I2C: Writing list to register 0x%02X:") % reg
                print (list)
            self.bus.write_i2c_block_data(self.address, reg, list)
        except IOError:
            return self.errMsg()
    def readList(self, reg, length):
        try:
            results = self.bus.read_i2c_block_data(self.address, reg, length)
            if self.debug:
                print ("I2C: Device 0x%02X returned the following from reg 0x%02X") % (self.address, reg)
                print (results)
            return results
        except IOError:
            return self.errMsg()
    def readU8(self, reg):
        try:
            result = self.bus.read_byte_data(self.address, reg)
            if self.debug:
                print ("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X") % (self.address, result & 0xFF, reg)
            return result
        except IOError:
            return self.errMsg()
    def readS8(self, reg):
        try:
            result = self.bus.read_byte_data(self.address, reg)
            if result > 127: result -= 256
            if self.debug:
                print ("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X") % (self.address, result & 0xFF, reg)
            return result
        except IOError:
            return self.errMsg()
    def readU16(self, reg, little_endian=True):
        try:
            result = self.bus.read_word_data(self.address,reg)
            if not little_endian:
                result = ((result << 8) & 0xFF00) + (result >> 8)
            if (self.debug):
                print ("I2C: Device 0x%02X returned 0x%04X from reg 0x%02X") % (self.address, result & 0xFFFF, reg)
            return result
        except IOError:
            return self.errMsg()
    def readS16(self, reg, little_endian=True):
        try:
            result = self.readU16(reg,little_endian)
            if result > 32767: result -= 65536
            return result
        except IOError:
            return self.errMsg()
if __name__ == '__main__':
    try:
        bus = Adafruit_I2C(address=0)
        print ("Default I2C buss is accessible")
    except:
        print("Error accessing default I2C bus")