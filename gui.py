import tkinter as tk
from tkinter.constants import DISABLED
from pathlib import Path

from Item import Item
from InventoryHandler import InventoryHandler

class ModifyItemPopupWindow:
    def __init__(self, master, item_slot, item):
        #self.master = master
        window = tk.Toplevel(master)
        self.window = window

        # Variables we'll use 
        self.var_slot = tk.IntVar(window, 0, name='Slot')
        self.var_count = tk.IntVar(window, 0, name='Count')
        self.var_id = tk.StringVar(window, '', name='ID')
        # This would be for adding the further item information
        # self.var_additional = tk.StringVar

        # TODO: Feel like there should be a cleaner way of doing this
        # Try to load the variables from the item_slot's item obj
        self.var_slot.set(item.slot)
        if item.count is not None:
            self.var_count.set(item.count)
        if item.id is not None:
            self.var_id.set(item.id)

        # Create the GUI representation for each of the variables
        slotLabel = tk.Label(window, text="Slot: ")
        slotLabel.pack(fill='x', padx=50, pady=5)
        slotEntry = tk.Entry(window, state=DISABLED, 
                            textvariable=self.var_slot)
        slotEntry.pack(fill='x', padx=50, pady=5)

        countLabel = tk.Label(window, text="Count: ")
        countLabel.pack(fill='x', padx=50, pady=5)
        countEntry = tk.Entry(window, textvariable=self.var_count)
        countEntry.pack(fill='x', padx=50, pady=5)

        idLabel = tk.Label(window, text="ID: ")
        idLabel.pack(fill='x', padx=50, pady=5)
        idEntry = tk.Entry(window, textvariable=self.var_id)
        idEntry.pack(fill='x', padx=50, pady=5)

        button_save = tk.Button(window, text="Save", command=self.save)
        button_save.pack(fill='x')

        button_close = tk.Button(window, text="Close", command=self.close)
        button_close.pack(fill='x')

        self.item_slot = item_slot
        self.item = item

    def save(self):
        print("Saving...")
        print("Item data:")
        print(f"Slot: {self.var_slot.get()}")
        print(f"Count: {self.var_count.get()}")
        print(f"ID: {self.var_id.get()}")

        # Save the variable data to item
        # self.item.slot = self.var_slot.get()
        self.item.count = self.var_count.get()
        self.item.id = self.var_id.get()

    def close(self):
        print("Closing...")
        self.item_slot.popup_window = None
        self.window.destroy()


class ItemSlot(tk.Frame):
    def __init__(self, master, row, column, slot_num):
        super().__init__(master, 
                        # bg="#898c87", 
                        bg="#a6a6a6",
                        width=64, 
                        height=64)
        self.grid(column=column, row=row, padx=5, pady=5)
        self.bind('<Button-1>', self.handle_click)
        self.popup_window = None
        
        # New item object that will store the item data associated with the
        # slot
        self.item = Item(slot=slot_num)
    
    def handle_click(self, event):
        self.popup_window = ModifyItemPopupWindow(None, self, self.item)


class App(tk.Frame):
    def __init__(self, master):
        # inits frame
        super().__init__(master)
        # self.pack()
        # self.grid(columnspan=9, rowspan=8, ipadx=10, ipady=10)
        self.grid()

        # Add all of the item slots
        self.itemslots = {}

        # Add the armour slots
        slot_num = 103
        for r in range(0, 4):
            self.itemslots[slot_num] = ItemSlot(self, r, 0, slot_num)
            slot_num -= 1
        
        # Add the shield slot
        self.itemslots[slot_num] = ItemSlot(self, 3, 4, -106)

        # Now the 3 main inventory rows
        startr = 4
        slot_num = 9
        for r in range(0, 3):
            for c in range(0, 9):
                self.itemslots[slot_num] = ItemSlot(self, r + startr, c, slot_num)
                slot_num += 1
        
        # The equip row
        startr = 7
        slot_num = 0
        for c in range(0, 9):
            self.itemslots[slot_num] = ItemSlot(self, startr, c, slot_num)
            slot_num += 1

        button_save = tk.Button(self, text="Save", command=self.save)
        button_save.grid(row = 0, column=5, columnspan=3, sticky='nsew')

        button_load = tk.Button(self, text="Load", command=self.load)
        button_load.grid(row = 1, column=5, columnspan=3, sticky='nsew')

    def save(self):
        # TODO: Right now we're just assuming that inventoryHandler has 
        # already been created
        if self.inventoryHandler is None:
            print("Cannot save: an inventory file has not been loaded yet.")
            return

        print("Saving...")
        items = []
        for itemslot in self.itemslots:
            item = self.itemslots[itemslot].item
            if item.is_valid():
                items.append(item)
                print(item)
        # Write items
        # save_items(items)
        # TODO: Hardcoded save path
        self.inventoryHandler.write_items(items, Path('.') / 'newlevel.dat')

    def load(self):
        print("Loading...")
        # TODO: REMOVE THIS IS JUST FOR TESTING
        # TODO: Since this is modifying the item slots, we should probably 
        # empty them all first (so we don't get remaining data from a 
        # previously loaded file).
        # invItems = get_items()
        # for item in invItems:
        #     self.itemslots[item.slot].item = item
        #     print(item)
        self.inventoryHandler = InventoryHandler(Path('.') / 'level4.dat')
        invItems = self.inventoryHandler.get_items()
        for item in invItems:
            self.itemslots[item.slot].item = item
            print(item)


root = tk.Tk()
root.title("MC Inventory Editor")
root.minsize(800, 600)
# root.configure(background="#c6c6c6")
# root.maxsize(800, 600)
app = App(root)
app.mainloop()