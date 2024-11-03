from artiq.experiment import *
from user import user_id
from common import Scope


class TTLOverflowExcersise(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl1 = self.get_device("ttl1")
        self.ttl3 = self.get_device("ttl3")
        self.ttls_out = [self.ttl1, self.ttl3]
        self.ttl_in = self.get_device("ttl5")

        self.scope = Scope(self, user_id)

    @kernel
    def init(self):
        self.core.reset()
        self.core.break_realtime()

        self.ttl_in.input()        
        delay(1 * us)
        for ttl in self.ttls_out:
            ttl.output()
            delay(1 * us)

    @kernel
    def run_rt(self):
        PERIOD_US = 1 * us
        N_SAMPLES = 66

        self.init()

        t0 = now_mu()

        self.ttls_out[0].on()
        at_mu(t0 + self.core.seconds_to_mu(80 * us))
        self.ttls_out[0].off()
        at_mu(t0 + self.core.seconds_to_mu(100 * ns))

        ###
        levels = [0 for n in range(N_SAMPLES)]
        for _ in range(N_SAMPLES):
            self.ttl_in.sample_input()
            delay(PERIOD_US)
        
        self.core.wait_until_mu(now_mu())
        for i in range(N_SAMPLES):
            levels[i] = self.ttl_in.sample_get()
        ###
        print(levels)            

    def run(self):
        self.scope.setup()        
        self.run_rt()
        self.scope.store_waveform()
