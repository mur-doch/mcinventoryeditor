import gzip
import struct
from abc import ABC, abstractmethod
from typing import List 

class Item:
    slot: int
    count: int
    id: str

    def __init__(self, slot=None, count=None, id=None):
        self.slot = slot
        self.count = count 
        self.id = id 

    def is_valid(self):
        if self.slot is None or self.count is None or self.id is None:
            return False 

        if (0 <= self.slot <= 35 or 100 <= self.slot <= 103 or self.slot == -106) \
            and 0 < self.count <= 255 \
            and self.id != '':
            return True 
        return False


    def __str__(self):
        return f"Slot {self.slot}, Count {self.count}, ID, {self.id}"


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

# def create_item():
#     # We'll start by creating the most basic item:
#     # Compound with Slot, Count, and String
#     new_item = TagCompound(10, None, [])
#     slot_tag = TagByte(1, "Slot", 2)
#     id_tag = TagString(8, "id", 'minecraft:tnt')
#     count_tag = TagByte(1, "Count", 64)
#     new_item.val.append(slot_tag)
#     new_item.val.append(id_tag)
#     new_item.val.append(count_tag)
#     return new_item

# def add_inventory_item(invtag: TagList):
#     new_item = create_item()
#     invtag.val.append(new_item)

# def inventory_to_items(invtag: TagList) -> List[Item]:
#     # Each item will be a TagCompound in invtag.vals
#     # Each item will have 3 tags that we care about
#     # TODO: Should add some form of error handling
#     items = []
#     for compound in invtag.val:
#         item = Item()
#         for tag in compound.val:
#             if tag.name == 'Slot':
#                 item.slot = tag.val
#             elif tag.name == 'id':
#                 item.id = tag.val
#             elif tag.name == 'Count':
#                 item.count = tag.val
#         items.append(item)
#     return items

# # def write_tag():
# #     tag = TagIntArray(11, "int array one", [TagInt(3, "integer1", 10), TagInt(3, "integer2", 100), TagInt(3, "integer3", 1000)])
# #     byte_arr = tag.get_byte_form()
# #     print(byte_arr)
# #     with open('test.bin', 'wb') as f :
# #         f.write(byte_arr)
# #     bh = ByteHandler(byte_arr)
# #     tag = TagIntArray()
# #     tag.read(bh)
# #     print(tag)

# # def main():
#     # b = hex_str_to_byte_arr('080002696400186D696E6563726166743A7370727563655F7361706C696E67')
#     # b = hex_str_to_byte_arr('050005666c6f6174400ccccd')
#     # byte_handler = ByteHandler(b)

#     # tag = TagFloat()
#     # tag.read(byte_handler)
#     # print(tag)

# def save_file_to_byte_handler(savefile):
#     with gzip.open(savefile, 'rb') as file:
#         bytes = file.read()

#     # Look for the start of the inventory list in the data file
#     found_index = bytes.find(b'\x09\x00\x09\x49\x6E\x76\x65\x6E\x74\x6F\x72\x79')
#     return ByteHandler(bytes[found_index:])

# def patch_inventory(orig_file_name: str, 
#                     new_file_name: str, 
#                     invtag: TagList, 
#                     bh: ByteHandler):
#     origfile = gzip.open(orig_file_name, 'rb')
#     newfile = gzip.open(new_file_name, 'wb')
#     bytes = origfile.read()
#     # Look for the start of the inventory list in the data file
#     found_index = bytes.find(b'\x09\x00\x09\x49\x6E\x76\x65\x6E\x74\x6F\x72\x79')

#     # Write all bytes up to the inventory
#     newfile.write(bytes[:found_index])
#     # Write our new inventory
#     newfile.write(invtag.get_byte_form())
#     # Write everything after the inventory
#     newfile.write(bytes[found_index+bh.cur_byte:])
    
#     origfile.close()
#     newfile.close()

# def main():
#     # Read the minecraft save file 
#     # with open('level.dat', 'rb') as file:
#     #     bytes = file.read()
#     # with gzip.open('level2.dat', 'rb') as file:
#         # bytes = file.read()
#     # Look for the start of the inventory list in the data file
#     # found_index = bytes.find(b'\x09\x00\x09\x49\x6E\x76\x65\x6E\x74\x6F\x72\x79')
#     # bh = ByteHandler(bytes[found_index:])
#     # print(bh.read_byte())

#     # invtag = TagList()
#     # invtag.read(bh)
#     # print(invtag)

#     # write_tag()
#     for item in get_items():
#         print(item)

#     savefile = "level4.dat"
#     bh = save_file_to_byte_handler(savefile)
#     invtag = TagList()
#     invtag.read(bh)
#     add_inventory_item(invtag)
#     patch_inventory(savefile, "newlevel.dat", invtag, bh)

# # TODO: REMOVE THIS IS JUST FOR TESTING
# def get_items():
#     savefile = "level4.dat"
#     bh = save_file_to_byte_handler(savefile)
#     invtag = TagList()
#     invtag.read(bh)
#     return inventory_to_items(invtag)

# # TODO: REMOVE -- hacky version of save
# def inventory_insert_item(invtag: TagList, item: Item):
#     slotTag = TagByte(tag_type=1, name='Slot', val=item.slot)
#     idTag = TagString(tag_type=8, name='id', val=item.id)
#     countTag = TagByte(tag_type=1, name='Count', val=item.count)
#     tag = TagCompound(val=[slotTag, idTag, countTag])
#     invtag.val.append(tag)

# def save_items(items: List[Item]):
#     savefile = "level4.dat"
#     bh = save_file_to_byte_handler(savefile)
#     invtag = TagList()
#     invtag.read(bh)
#     invtag.val = []
#     for item in items:
#         inventory_insert_item(invtag, item)
#     # add_inventory_item(invtag)
#     patch_inventory(savefile, "newlevel.dat", invtag, bh)

# def test():
#     items = get_items()
#     save_items(items)

from pathlib import Path 

class InventoryHandler:
    save_file: Path
    inventory_tag_offset: int
    bh: ByteHandler
    invtag: TagList

    def __init__(self, save_file: Path):
        # Read the inventory from save_file
        self.save_file = save_file
        self.read_save_file()

        # Read and parse the inventory from the byte handler
        self.invtag = TagList()
        self.invtag.read(self.bh)

    def get_items(self) -> List[Item]:
        # TODO: Should add some form of error handling
        items = []
        for compound in self.invtag.val:
            item = Item()
            for tag in compound.val:
                if tag.name == 'Slot':
                    item.slot = tag.val
                elif tag.name == 'id':
                    item.id = tag.val
                elif tag.name == 'Count':
                    item.count = tag.val
            items.append(item)
        return items

    def write_items(self, items: List[Item], file_to_write: Path):
        # Creates a new empty inventory tag based on our old one.
        new_invtag = TagList(
            self.invtag.tag_type, 
            self.invtag.name, 
            [], 
            self.invtag.sub_tag_type
        )
        for item in items:
            self.inventory_insert_item(new_invtag, item)
        self.write_save_file(file_to_write, new_invtag)

    def read_save_file(self):
        with gzip.open(self.save_file, 'rb') as file:
            bytes = file.read()

        # Look for the start of the inventory list in the data file
        self.inventory_tag_offset = bytes.find(b'\x09\x00\x09\x49\x6E\x76\x65\x6E\x74\x6F\x72\x79')

        # Create byte handler and have it seek to where the inventory starts
        self.bh = ByteHandler(bytes)
        self.bh.seek(self.inventory_tag_offset)

    def write_save_file(self, new_file_name: str, new_invtag: TagList):
        newfile = gzip.open(new_file_name, 'wb')
        bytes = self.bh.bytes 

        # Write all bytes up to the inventory
        newfile.write(bytes[:self.inventory_tag_offset])
        # Write our new inventory
        newfile.write(new_invtag.get_byte_form())
        # Write everything after the inventory
        # Since we're using the full file in byte_handler now, cur_byte should
        # stop at the actual ending of inventory
        newfile.write(bytes[self.bh.cur_byte:])
        
        newfile.close()

    def inventory_insert_item(self, invtag: TagList, item: Item):
        slotTag = TagByte(tag_type=1, name='Slot', val=item.slot)
        idTag = TagString(tag_type=8, name='id', val=item.id)
        countTag = TagByte(tag_type=1, name='Count', val=item.count)
        tag = TagCompound(val=[slotTag, idTag, countTag])
        invtag.val.append(tag)


if __name__ == '__main__':
    # test()
    # main()
    pass