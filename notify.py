import louie

class Signal(object):
    def __init__(self):
        self.signal = louie.Signal()

    def connect(self, receiver, **kwargs):
        louie.connect(receiver, self.signal, **kwargs)

    def connect_lambda(self, receiver, **kwargs):
        louie.connect(receiver, self.signal, weak=False, **kwargs)

    def __call__(self, *args, **kwargs):
        return louie.send(self.signal, self, *args, **kwargs)
