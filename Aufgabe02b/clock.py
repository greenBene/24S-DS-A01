import re
from threading import Lock

class ClockException(Exception):
    pass

class VectorClock():
    number_of_participants:int
    id:int
    local_time = list()
    lock = Lock()

    def __init__(self, number_of_participants:int, id:int) -> None:
        with self.lock:
            self.number_of_participants = number_of_participants
            self.id = id
            self.local_time = [0 for _ in range(number_of_participants)]

    def tick(self):
        with self.lock:
            self.local_time[self.id]+=1

    
    def before(self, other_time:str):
        with self.lock:
            other_time = self.deserialize(other_time)

            before = True 
            for i in range(len(self.local_time)):
                if before:
                    before = self.local_time[i] <= other_time[i]
            return before

    def after(self, other_time:str):
        with self.lock:
            other_time = self.deserialize(other_time)

            after = True 
            for i in range(len(self.local_time)):
                if after:
                    after = self.local_time[i] >= other_time[i]
            return after


    
    def update(self, other_time:str):
        with self.lock:
            other_time = self.deserialize(other_time)
            
            if len(other_time) != len(self.local_time):
                raise ClockException("Received invalid timestamp")
            
            for i in range(len(self.local_time)):
                self.local_time[i] = max(self.local_time[i], other_time[i])


    def serialize(self) -> str:
        with self.lock:
            s = '['
            for i in self.local_time:
                s += f'{i},'
            s += ']'
        return s
    
    
    def deserialize(self, s:str) -> list:
        if re.match(r'^\[(\d+,)*\]$', s) == None:
            raise ClockException('Invalid VectorClock serialization')
        
        s = s[1:-1]
        values = s.split(",")
        time = [int(x) for x in values if len(x) > 0]
        return time