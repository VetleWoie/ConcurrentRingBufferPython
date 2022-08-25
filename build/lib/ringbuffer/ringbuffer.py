import threading

class RingbufferException(Exception):
    pass

class RingbufferEmptyException(RingbufferException):
    pass

class Ringbuffer():
    def __init__(self, size, blockonfull=False, blockonempty=False) -> None:
        #Hacky way of initializing an array to a fixed size
        self.buffer = [None] * size #TODO: Should be done better
        self.head = -1
        self.tail = -1
        self.size = size
        self.count = 0
        self.lock = threading.Lock()
        self.empty = None
        self.full = None
        if blockonfull:
            self.full = threading.Condition(self.lock)
        if blockonempty:
            self.empty = threading.Condition(self.lock)
        
    
    def put(self, elem):
        #Aquire lock
        self.lock.acquire()
        if self.count == self.size and self.full is not None:
            self.full.wait()

        #Move head
        self.head = (self.head + 1) % self.size
        self.buffer[self.head] = elem
        self.count += 1 if self.count < self.size else 0
        if self.empty is not None:
            self.empty.notify_all()
        self.lock.release()

    def get(self):
        #Aquire lock
        self.lock.acquire()
        #Check if empty
        if self.count == 0:
            if self.empty is not None:
                self.empty.wait()
            else:
                raise RingbufferEmptyException
        self.tail = (self.tail + 1) % self.size
        self.count -= 1

        if self.full is not None:
            self.full.notify_all()
        self.lock.release()
        return self.buffer[self.tail]
    
    def __str__(self) -> str:
        out = ""
        for elem in self.buffer:
            out += str(elem)+"-"
        out += f"head: {self.head} tail: {self.tail}"
        return out

    def hello():
        print("hello world")


        