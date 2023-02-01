class info():
    def __init__(self): 
        self.label: str = '' 
        self.bbox: list[int] = [] 
        self.staff: int = None 
        self.pitch: str = ''
        self.sharp: bool = False 
        self.flat: bool = False
        self.duration: int = None 
