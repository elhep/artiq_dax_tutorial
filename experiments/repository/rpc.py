from artiq.experiment import *

def input_ttl_state() -> TBool:
    return input("Enter desired TTL state: ") == "1"

class TimingExcercise(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl = self.get_device("ttl0")

    @kernel
    def run(self):
        # Reset our system after previous experiment
        self.core.reset()

        s = input_ttl_state()

        self.core.break_realtime()
        self.ttl.set_o(s)