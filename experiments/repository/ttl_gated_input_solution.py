from artiq.experiment import *
from user import user_id
from common import Scope


class TTLGatedInputExcersise(EnvExperiment):
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
        self.init()
        t0 = now_mu()

        N_PULSES = 8
        PERIOD_US = 1 * us
        GATE_US = N_PULSES * PERIOD_US

        self.ttls_out[1].on()
        gate_end_mu = self.ttl_in.gate_both(GATE_US)
        self.ttls_out[1].off()

        at_mu(t0)
        for _ in range(N_PULSES):
            self.ttls_out[0].pulse(PERIOD_US / 2)
            delay(PERIOD_US / 2)

        self.core.wait_until_mu(now_mu())        
        received = self.ttl_in.count(gate_end_mu)
        
        print(received)


    def run(self):
        self.scope.setup_for_dio()
        self.run_rt()
        self.scope.store_waveform()
