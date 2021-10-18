# import gzip
import struct
from abc import ABC, abstractmethod 

class ByteHandler:
    def __init__(self, bytes: bytearray):
        self.bytes = bytes
        self.cur_byte = 0 

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

    def read_str(self, size):
        s = ""
        for i in range(size):
            s += chr(self.read_byte())
        return s 


class Tag(ABC):
    def __init__(self):
        self.tag_type = None
        self.name = None 
        self.val = None
    
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_header(self, byte_handler: ByteHandler):
        # Read short for the length of the name 
        name_size = byte_handler.read_short()
        name = byte_handler.read_str(name_size)
        self.name = name

    @abstractmethod
    def read_payload(self, byte_handler: ByteHandler):
        pass

    def __str__(self):
        return f"{self.tag_type}, {self.name}, {self.val}"


class TagEnd(Tag):
    def __init__(self):
        super()
        self.tag_type = 0
    
    def read(self, byte_handler: ByteHandler):
        self.tag_type = byte_handler.read_byte()


class TagByte(Tag):
    def read_payload(self, byte_handler: ByteHandler):
        self.val = byte_handler.read_byte()


class TagFloat(Tag):
    def read_payload(self, byte_handler: ByteHandler):
        self.val = byte_handler.read_float()


class TagString(Tag):    
    def read_payload(self, byte_handler: ByteHandler):
        # Read short for the length of the string 
        length = byte_handler.read_short()
        self.val = byte_handler.read_str(length)


def hex_str_to_byte_arr(hex_str):
    byte_arr = bytearray()
    for i in range(0, len(hex_str), 2):
        byte_arr.append(int(hex_str[i:i+2], base=16))
    return byte_arr

def main():
    # b = hex_str_to_byte_arr('080002696400186D696E6563726166743A7370727563655F7361706C696E67')
    b = hex_str_to_byte_arr('050005666c6f6174400ccccd')
    byte_handler = ByteHandler(b)

    # tag_byte = TagByte()
    # tag_byte.read(byte_handler)
    # tag = TagString()
    # tag.read(byte_handler)
    tag = TagFloat()
    tag.read(byte_handler)
    print(tag)

# def main():
#     # Read the minecraft save file 
#     with open('level.dat', 'rb') as file:
#         bytes = file.read()
#     # Look for the start of the inventory list in the data file
#     found_index = bytes.find(b'\x09\x00\x09\x49\x6E\x76\x65\x6E\x74\x6F\x72\x79')
#     bh = ByteHandler(bytes[found_index:])
#     print(bh.read_byte())

if __name__ == '__main__':
    main() 