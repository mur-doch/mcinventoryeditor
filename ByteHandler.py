import struct

class ByteHandler:
    def __init__(self, bytes: bytearray):
        self.bytes = bytes
        self.cur_byte = 0 

    def peek_byte(self):
        return self.bytes[self.cur_byte]

    def seek(self, num_bytes: int):
        # TODO: Should probably be some kind of check for how far we're going
        self.cur_byte += num_bytes

    def read_byte(self):
        b = self.bytes[self.cur_byte]
        self.cur_byte += 1
        return b

    def read_short(self):
        b1 = self.read_byte()
        b2 = self.read_byte()
        return (b1 << 8) + b2

    def read_int(self):
        b1 = self.read_byte()
        b2 = self.read_byte()
        b3 = self.read_byte()
        b4 = self.read_byte()
        return (b1 << 24) + (b2 << 16) + (b3 << 8) + b4

    def read_long(self):
        l = 0
        for i in range(8):
            b = self.read_byte()
            l += (b << (8 - i - 1))
        return l

    def read_float(self):
        f = struct.unpack('>f', self.bytes[self.cur_byte:self.cur_byte + 4])[0]
        self.cur_byte += 4
        return f

    def read_double(self):
        f = struct.unpack('>d', self.bytes[self.cur_byte:self.cur_byte + 8])[0]
        self.cur_byte += 8
        return f

    def read_str(self, size):
        s = ""
        for i in range(size):
            s += chr(self.read_byte())
        return s 
