import gzip
import struct
from abc import ABC, abstractmethod 

class ByteHandler:
    def __init__(self, bytes: bytearray):
        self.bytes = bytes
        self.cur_byte = 0 

    def peek_byte(self):
        return self.bytes[self.cur_byte]

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
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = byte_handler.read_byte()

class TagShort(Tag):
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = byte_handler.read_short()


class TagInt(Tag):
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = byte_handler.read_int()


class TagLong(Tag):
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = byte_handler.read_long()


class TagFloat(Tag):
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = byte_handler.read_float()


class TagDouble(Tag):
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = byte_handler.read_double()


class TagByteArray(Tag):
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        arr_size = byte_handler.read_int()
        self.val = []
        for i in range(arr_size):
            # These tags will only store the payloads
            new_tag = TagByte()
            new_tag.read_payload()
            self.val.append(new_tag)

    def __str__(self):
        s = f"Byte Array '{self.name}': {self.val}"
        return s 


class TagString(Tag):    
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        # Read short for the length of the string 
        length = byte_handler.read_short()
        self.val = byte_handler.read_str(length)


class TagList(Tag):
    def __init__(self):
        super().__init__()
        self.sub_tag_type = None

    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = []
        self.sub_tag_type = byte_handler.read_byte()
        list_size = byte_handler.read_int()
        TagType = id_to_tag(self.sub_tag_type)
        for i in range(list_size):
            tag = TagType()
            tag.read_payload(byte_handler)
            self.val.append(tag)

    def __str__(self):
        # TODO: Shouldn't print self.name if it is just going to be null
        s = f"List '{self.name}' of types {self.sub_tag_type}"
        for i, subtag in enumerate(self.val):
            s += f"\n{i}: {subtag.__str__()}"
        return s


class TagCompound(Tag):
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = []
        while True:
            tagid = byte_handler.peek_byte()
            # If reached TAG_END
            if tagid == 0:
                byte_handler.read_byte()
                break

            TagType = id_to_tag(tagid)
            tag = TagType()
            tag.read(byte_handler)
            self.val.append(tag)

    def __str__(self):
        s = f"Compound '{self.name}'"
        for i, subtag in enumerate(self.val):
            s += f"\n{i}: {subtag.__str__()}"
        return s


class TagIntArray(Tag):
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = []
        size = byte_handler.read_int()
        for i in range(size):
            tag = TagInt()
            tag.read_payload(byte_handler)
            self.val.append(tag)
    
    def __str__(self):
        s = f"Int Array '{self.name}': {self.val}"
        return s 


class TagLongArray(Tag):
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = []
        size = byte_handler.read_int()
        for i in range(size):
            tag = TagLong()
            tag.read_payload()
            self.val.append(tag)

    def __str__(self):
        s = f"Long Array '{self.name}': {self.val}"
        return s 


def id_to_tag(id):
    if id == 0:
        return TagEnd
    elif id == 1:
        return TagByte
    elif id == 2:
        return TagShort 
    elif id == 3:
        return TagInt
    elif id == 4:
        return TagLong 
    elif id == 5:
        return TagFloat  
    elif id == 6:
        return TagDouble 
    elif id == 7:
        return TagByteArray
    elif id == 8:
        return TagString 
    elif id == 9:
        return TagList
    elif id == 10:
        return TagCompound
    elif id == 11:
        return TagIntArray
    elif id == 12:
        return TagLongArray

def hex_str_to_byte_arr(hex_str):
    byte_arr = bytearray()
    for i in range(0, len(hex_str), 2):
        byte_arr.append(int(hex_str[i:i+2], base=16))
    return byte_arr

def inventory_bytes_from_save(level_file):
    with open(level_file, 'rb') as file:
        bytes = file.read()
    found_index = bytes.find(b'\x09\x00\x09\x49\x6E\x76\x65\x6E\x74\x6F\x72\x79')
    return bytes[found_index:]

# def main():
    # b = hex_str_to_byte_arr('080002696400186D696E6563726166743A7370727563655F7361706C696E67')
    # b = hex_str_to_byte_arr('050005666c6f6174400ccccd')
    # byte_handler = ByteHandler(b)

    # tag = TagFloat()
    # tag.read(byte_handler)
    # print(tag)

def main():
    # Read the minecraft save file 
    # with open('level.dat', 'rb') as file:
    #     bytes = file.read()
    with gzip.open('level2.dat', 'rb') as file:
        bytes = file.read()
    # Look for the start of the inventory list in the data file
    found_index = bytes.find(b'\x09\x00\x09\x49\x6E\x76\x65\x6E\x74\x6F\x72\x79')
    bh = ByteHandler(bytes[found_index:])
    # print(bh.read_byte())

    invtag = TagList()
    invtag.read(bh)
    print(invtag)


if __name__ == '__main__':
    main() 