from abc import ABC, abstractmethod
import struct
from ByteHandler import ByteHandler

class Tag(ABC):
    def __init__(self, tag_type=None, name=None, val=None):
        self.tag_type = tag_type
        self.name = name 
        self.val = val
    
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

    def get_header_bytes(self):
        byte_form = b''
        # Get the tag type byte
        byte_form += struct.pack(">B", self.tag_type)
        # Get the length of the name
        byte_form += struct.pack(">H", len(self.name))
        # Get the name bytes
        byte_form += self.name.encode('ascii')
        return byte_form

    @abstractmethod
    def get_payload_bytes(self):
        pass

    # @abstractmethod
    def get_byte_form(self):
        return self.get_header_bytes() + self.get_payload_bytes()

    def __str__(self):
        return f"{self.tag_type}, {self.name}, {self.val}"


class TagEnd(Tag):
    def __init__(self):
        super()
        self.tag_type = 0
    
    def read(self, byte_handler: ByteHandler):
        self.tag_type = byte_handler.read_byte()

    def read_payload(self, byte_handler: ByteHandler):
        pass

    def get_payload_bytes(self):
        return b''

    def get_byte_form(self):
        return struct.pack(">B", 0)


class TagByte(Tag):
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = byte_handler.read_byte()

    def get_payload_bytes(self):
        return struct.pack(">B", self.val)


class TagShort(Tag):
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = byte_handler.read_short()

    def get_payload_bytes(self):
        return struct.pack(">h", self.val)


class TagInt(Tag):
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = byte_handler.read_int()

    def get_payload_bytes(self):
        return struct.pack(">i", self.val)


class TagLong(Tag):
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = byte_handler.read_long()

    def get_playload_bytes(self):
        return struct.pack(">l", self.val)


class TagFloat(Tag):
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = byte_handler.read_float()

    def get_payload_bytes(self):
        return struct.pack(">f", self.val)


class TagDouble(Tag):
    def read(self, byte_handler: ByteHandler):        
        self.tag_type = byte_handler.read_byte()
        self.read_header(byte_handler)
        self.read_payload(byte_handler)

    def read_payload(self, byte_handler: ByteHandler):
        self.val = byte_handler.read_double()

    def get_payload_bytes(self):
        return struct.pack(">d", self.val)


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
            new_tag.read_payload(byte_handler)
            self.val.append(new_tag)

    def get_payload_bytes(self):
        b = b''
        # Write the int size of the byte array
        b += struct.pack(">i", len(self.val))
        # Write size bytes
        for byte in self.val:
            b += struct.pack(">B", byte)
        return b

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

    def get_payload_bytes(self):
        b = b''
        # Write the unsigned short size of the byte array
        b += struct.pack(">H", len(self.val))
        # Write size bytes
        b += self.val.encode('ascii')
        return b


class TagList(Tag):
    def __init__(self, tag_type=None, name=None, val=None, sub_tag_type=None):
        super().__init__(tag_type, name, val)
        self.sub_tag_type = sub_tag_type

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

    def get_payload_bytes(self):
        b = b''
        # Write the tag type for the list items
        b += struct.pack(">B", self.sub_tag_type)
        # Write the int size of the byte array
        b += struct.pack(">i", len(self.val))
        # Write size tags of type sub_tag_type
        for tag in self.val:
            b += tag.get_payload_bytes()
        return b

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

    def get_payload_bytes(self):
        b = b''
        # Write all complete tags we have
        for tag in self.val:
            b += tag.get_byte_form()
        # And last, we'll write the TAG_END
        tag = TagEnd()
        b += tag.get_byte_form()
        return b

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

    def get_payload_bytes(self):
        b = b''
        # Write the int size of the int array
        b += struct.pack(">i", len(self.val))
        # Write size ints
        for i in self.val:
            # b += struct.pack(">i", i)
            b += i.get_payload_bytes()
        return b

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

    def get_payload_bytes(self):
        b = b''
        # Write the int size of the long array
        b += struct.pack(">i", len(self.val))
        # Write size longs
        for l in self.val:
            # b += struct.pack(">l", l)
            b += l.get_payload_bytes()  
        return b

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
