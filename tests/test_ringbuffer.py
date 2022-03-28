import threading
import unittest
from ringbuffer.ringbuffer import *

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
    unittest.main()