class HexType:
    def __init__(self, x):
        if isinstance(x, str):
            self.val = int(x, 16)
        elif isinstance(x, int):
            self.val = int(str(x), 16)

    def __str__(self):
        return hex(self.val)
