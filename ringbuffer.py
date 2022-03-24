import unittest
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


class Test_thread(threading.Thread):
    def run(self):
        """
        Overriding run method to be able to check output
        """
        try:
            if self._target:
                self.output = self._target(*self._args, **self._kwargs)
        finally:
            # Avoid a refcycle if the thread is running a function with
            # an argument that has a member that points to the thread.
            del self._target, self._args, self._kwargs

class test_ringbuffer(unittest.TestCase):
    def setUp(self) -> None:
        self.ringbuffer = Ringbuffer(5)
        self.blocking_ringbuffer = Ringbuffer(5, blockonfull=True, blockonempty=True)
        self.block_empty_thread = Test_thread(target=self.blocking_ringbuffer.get,daemon=True)
        self.block_full_thread = Test_thread(target=self.blocking_ringbuffer.put,
                                                daemon=True,
                                                args=[5])
        return super().setUp()
    
    def test_add_get_5(self) -> None:
        for i in range(5):
            self.ringbuffer.put(i)
        for i in range(5):
            v = self.ringbuffer.get()
            self.assertEqual(i,v)
    
    def test_add_get_10(self) -> None:
        for i in range(10):
            self.ringbuffer.put(i)
        
        for i in range(5,10):
            v=self.ringbuffer.get()
            self.assertEqual(i,v)
    
    def test_assert_empty(self) -> None:
        self.assertRaises(RingbufferException, self.ringbuffer.get)
    
    def test_assert_empty_after_filled(self) -> None:
        for i in range(5):
            self.ringbuffer.put(i)
        for i in range(5):
            self.ringbuffer.get()
        self.assertRaises(RingbufferException, self.ringbuffer.get)
    
    def test_assert_empty_after_doubly_filled(self) -> None:
        for i in range(10):
            self.ringbuffer.put(i)
        for i in range(5,10):
            self.ringbuffer.get()

        self.assertRaises(RingbufferException, self.ringbuffer.get)
    
    def test_str_method(self):
        str(self.ringbuffer)

    def test_block_on_empty(self):
        self.block_empty_thread.start()
        self.assertFalse(self.blocking_ringbuffer.lock.locked())
        self.blocking_ringbuffer.put(1)
        self.block_empty_thread.join()
        self.assertEqual(self.block_empty_thread.output, 1)

    def test_block_on_full(self):
        #Fill ringbuffer
        for i in range(5):
            self.blocking_ringbuffer.put(i)
        self.block_full_thread.start()
        self.assertFalse(self.blocking_ringbuffer.lock.locked())
        value=self.blocking_ringbuffer.get()
        self.assertEqual(value, 0)
        self.block_full_thread.join()
        for i in range(1,6):
            value=self.blocking_ringbuffer.get()
            self.assertEqual(value, i)

if __name__ == "__main__":
    import time
    unittest.main()

        