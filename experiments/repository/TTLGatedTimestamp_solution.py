from artiq.experiment import *
from user import user_id
from common import Scope
import numpy as np

N_PULSES = 8
PERIOD_US = 1 * us
GATE_US = N_PULSES * PERIOD_US


class TTLGatedTimestampExcersise(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl1 = self.get_device("ttl1")
        self.ttl3 = self.get_device("ttl3")
        self.ttls_out = [self.ttl1, self.ttl3]
        self.ttl_in = self.get_device("ttl5")

        self.scope = Scope(self, user_id)

        self.timestamps = [np.int64(0) for i in range(N_PULSES * 2)]
        self.t0 = np.int64(0)


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

        self.t0 = now_mu()

        for i in range(N_PULSES):
            self.ttls_out[0].pulse(PERIOD_US / 2)
            delay(PERIOD_US / 2)

        at_mu(self.t0)
        ###
        
        gate_end_mu = self.ttl_in.gate_both(GATE_US)

        i = 0
        while True:
            result = self.ttl_in.timestamp_mu(gate_end_mu)
            if result == -1:
                break
            self.timestamps[i] = result
            i = i + 1


    def run(self):
        self.scope.setup()
        
        print("Running...")
        self.run_rt()
        
        self.scope.store_waveform()

        time_values_us = []
        for tstmp in self.timestamps:
            if tstmp != 0:
                t = self.core.mu_to_seconds(tstmp - self.t0)*1e6
                time_values_us.append(t)

        for tstmp in time_values_us:
            print(f"delta[us]: {tstmp:.3f}")