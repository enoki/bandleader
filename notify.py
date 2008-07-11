import louie

class Signal(object):
    def __init__(self):
        self.signal = louie.Signal()

    def connect(self, receiver):
        louie.connect(receiver, self.signal)

    def __call__(self, *args, **kwargs):
        louie.send(self.signal, self, *args, **kwargs)
