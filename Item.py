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
