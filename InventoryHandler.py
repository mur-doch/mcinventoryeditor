from pathlib import Path
from ByteHandler import ByteHandler
from Tags import *
from typing import List
from Item import Item
import gzip 


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
