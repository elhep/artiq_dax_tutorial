from artiq.experiment import *

class TimingExcercise(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl = self.get_device("ttl0")

    @kernel
    def run(self):
        # Reset our system after previous experminet
        self.core.reset()


        self.core.break_realtime()

        # t will be our LOCAL time pointer
        t = now_mu()


        self.ttl.set_o(True)
        delay(self.DelayValue * us)
        self.ttl.set_o(False)

        #