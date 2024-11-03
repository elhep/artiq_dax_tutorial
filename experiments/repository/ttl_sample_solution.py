from artiq.experiment import *
from user import user_id
from common import Scope


class TTLSampleExcersise(EnvExperiment):
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
        N_SAMPLES = 8
        
        self.init()

        t0 = now_mu()
        for i in range(N_SAMPLES):
            self.ttls_out[0].pulse(PERIOD_US / 2)
            delay(PERIOD_US / 2)
        at_mu(t0)       
        delay(PERIOD_US / 4) # to land in the middle of the state

        ###
        levels = [0 for n in range(2*N_SAMPLES)]
        for i in range(2*N_SAMPLES):
            self.ttl_in.sample_input()
            delay(PERIOD_US / 2)
        
        self.core.wait_until_mu(now_mu())
        for i in range(2 * N_SAMPLES):
            levels[i] = self.ttl_in.sample_get()


    def run(self):
        self.scope.setup_for_dio()
        
        print("Running...")
        self.run_rt()
        print(self.levels)
        self.scope.store_waveform()
