class info():
    def __init__(self): 
        self.label: str = '' 
        self.bbox: list[int] = [] 
        self.staff: int = None 
        self.pitch: int = 0
        self.sharp: bool = False 
        self.flat: bool = False
        self.natural: bool = False 
        self.duration: int = None 
        self.measure: int = None 
        
