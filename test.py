class MyQueue:
    def __init__(self):
        self._queue = []

    def add(self, n):
        self._queue.append(n)

    def get(self):
        return self._queue


mq = MyQueue()
mq2 = MyQueue()
print(mq.get())
mq.add(1)
print(mq2.get())
print(mq.get())
