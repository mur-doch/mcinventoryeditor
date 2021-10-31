import tkinter as tk
from tkinter.filedialog import askopenfilename
from tkinter.constants import DISABLED, BOTH
from pathlib import Path

from Item import Item
from InventoryHandler import InventoryHandler


class ItemSpriteHandler:
    def __init__(self):
        self.spritesheet = tk.PhotoImage(file="items-28.png")

        self.sprite_width = 32
        self.sprite_height = 32
        self.spritesheet_width = 27
        self.spritesheet_height = 27

        # Load images
        self.images = []
        for row in range(self.spritesheet_height):
            for col in range(self.spritesheet_width):
                l = col * self.sprite_width
                t = row * self.sprite_height
                self.images.append(
                    self.subimage(
                        l, t, l + self.sprite_width, t + self.sprite_height
                    )
                )

        # Load the dictionary that will map from the minecraft id string to
        # the index in the images list
        self.mcid_to_index = {}
        file = open('Scraping/mcid_to_index.csv', 'r')
        for line in file:
            mcid, raw_index = line.split(',')
            self.mcid_to_index[mcid] = int(raw_index)

    def subimage(self, l, t, r, b):
        new_image = tk.PhotoImage()
        new_image.tk.call(
            new_image, 
            'copy', 
            self.spritesheet, 
            '-from', 
            l, t, r, b, 
            '-to', 
            0, 0
        )
        return new_image

    def get_image(self, minecraft_id: str) -> tk.PhotoImage:
        return self.images[self.mcid_to_index[minecraft_id]]


class ModifyItemPopupWindow:
    def __init__(self, master, item_slot, item, on_save):
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

        self.on_save = on_save

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

        if self.on_save is not None:
            self.on_save()

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
        self.popup_window = None
        
        # New item object that will store the item data associated with the
        # slot
        self.item = Item(slot=slot_num)

        # Won't have any image by default
        self.image_label = tk.Label(self, bg="#a6a6a6")
        # self.image_label.grid(column=0, row=0)
        self.image_label.pack(expand=True, fill=BOTH)
        # This stops the frame from shrinking with the label
        # Very weird, but it makes them have a constant size
        self.pack_propagate(0)

        self.image_label.bind('<Button-1>', self.handle_click)

        self.count_label = tk.Label(self, bg="#a6a6a6", text="", borderwidth=1, relief='solid')
        self.count_label.place(relx=1.0, rely=1.0, x=-2, y=-2,anchor="se")
        self.count_label.place_forget()
    
    def handle_click(self, event):
        self.popup_window = ModifyItemPopupWindow(
            None, 
            self, 
            self.item, 
            # self.on_save
            self.update_display
        )

    # def set_image(self, img: tk.PhotoImage):
    #     self.image_label.configure(image=img)
    def update_display(self):
        global itemSpriteHandler
        if self.item.is_valid():
            self.image_label.configure(image=itemSpriteHandler.get_image(self.item.id))
            self.count_label.configure(text=str(self.item.count))
            self.count_label.place(relx=1.0, rely=1.0, x=-2, y=-2,anchor="se")
        else:
            self.image_label.configure(image=None)
            self.count_label.configure(text="")
            self.count_label.place_forget()


    def set_item(self, item: Item):
        self.item = item
        # if self.item.id != None:
        #     self.set_image(self.item.id)
        # else:
        #     # TODO: This might give error
        #     self.set_image(None)

    def on_save(self):
        self.set_image(itemSpriteHandler.get_image(self.item.id))


class App(tk.Frame):
    def __init__(self, master):
        # inits frame
        super().__init__(master)
        # self.pack()
        # self.grid(columnspan=9, rowspan=8, ipadx=10, ipady=10)
        self.grid()

        # Add all of the item slots
        self.itemslots = {}

        self.itemSpriteHandler = ItemSpriteHandler()

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

        # VARIABLES
        # TODO: Should be put at the top
        self.inventoryHandler = None
        self.save_path = None
        self.load_path = None

        self.var_save_path = tk.StringVar(self, '', name='Save Path')
        self.var_load_path = tk.StringVar(self, '', name='Load Path')

        self.input_frame = tk.Frame(self)
        self.input_frame.grid(row=0, rowspan=3, column=5, columnspan=3)

        # Create the save and load file location inputs
        self.text_save_location = tk.Entry(
            self.input_frame, 
            textvariable=self.var_save_path)
        self.text_save_location.pack(fill=BOTH, expand=True)
        self.button_save_location = tk.Button(
            self.input_frame, 
            text="Set Save Location", 
            command=self.get_save_location)
        self.button_save_location.pack(fill=BOTH, expand=True)

        self.text_load_location = tk.Entry(
            self.input_frame, 
            textvariable=self.var_load_path)
        self.text_load_location.pack(fill=BOTH, expand=True)
        self.button_load_location = tk.Button(
            self.input_frame, 
            text="Set Load Location", 
            command=self.get_load_location)
        self.button_load_location.pack(fill=BOTH, expand=True)

        # Create the save and load buttons
        self.button_save = tk.Button(
            self.input_frame, 
            text="Save to file", 
            command=self.save)
        # self.button_save.grid(row = 1, column=5, columnspan=3, sticky='nsew')
        self.button_save.pack(fill=BOTH, expand=True)

        self.button_load = tk.Button(
            self.input_frame, 
            text="Load from file", 
            command=self.load)
        # self.button_load.grid(row = 2, column=5, columnspan=3, sticky='nsew')
        self.button_load.pack(fill=BOTH, expand=True)

    def save(self):
        file_to_save = self.var_save_path.get()
        save_path = Path(file_to_save)
        if not save_path.exists() or not save_path.is_file():
            print("The save path must be an existing file.")

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

        self.inventoryHandler.write_items(items, save_path)

    def load(self):
        # TODO: Since this is modifying the item slots, we should probably 
        # empty them all first (so we don't get remaining data from a 
        # previously loaded file).
        for itemslot in self.itemslots:
            self.itemslots[itemslot].item = Item(itemslot)

        file_to_load = self.var_load_path.get()
        load_path = Path(file_to_load)
        if not load_path.exists() or not load_path.is_file():
            print("The load path must be an existing file.")
            return

        print("Loading...")
        self.inventoryHandler = InventoryHandler(load_path)
        invItems = self.inventoryHandler.get_items()
        for item in invItems:
            # self.itemslots[item.slot].item = item
            self.itemslots[item.slot].set_item(item)
            # self.itemslots[item.slot].set_image(
            #     self.itemSpriteHandler.get_image(item.id)
            # )
            self.itemslots[item.slot].update_display()
            print(item)

    def get_save_location(self):
        self.save_path = Path(askopenfilename())
        self.text_save_location.delete(0, tk.END)
        self.text_save_location.insert(0, str(self.save_path.absolute()))

    def get_load_location(self):
        self.load_path = Path(askopenfilename())
        self.text_load_location.delete(0, tk.END)
        self.text_load_location.insert(0, str(self.load_path.absolute()))

root = tk.Tk()
root.title("MC Inventory Editor")
root.minsize(800, 600)
# root.configure(background="#c6c6c6")
# root.maxsize(800, 600)
# TODO: This should probably not be a global
itemSpriteHandler = ItemSpriteHandler()
app = App(root)
app.mainloop()