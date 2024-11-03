from artiq.experiment import *
from user import user_id
from common import Scope
import numpy as np


N_PULSES = 60
PERIOD_US = 1000 * ns
OFFSET = 50 * ns
GATE_US = N_PULSES * PERIOD_US + OFFSET


class TTLEdgeCounterExcersise(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl1 = self.get_device("ttl1")
        self.ttl3 = self.get_device("ttl3")
        self.ttls_out = [self.ttl1, self.ttl3]
        self.ttl_in = self.get_device("ttl5")
        self.ttl_edge_counter = self.get_device("ttl5_counter")

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
        N_PULSES = 60
        PERIOD_US = 1 * us
        OFFSET = 50 * ns
        GATE_US = N_PULSES * PERIOD_US + OFFSET


        with parallel:
            gate_end_mu = self.ttl_edge_counter.gate_both(GATE_US)
            with sequential:
                delay(OFFSET)
                for _ in range(N_PULSES):
                    self.ttls_out[0].pulse(PERIOD_US / 2)
                    delay(PERIOD_US / 2)

        print(self.ttl_edge_counter.fetch_count())



    def run(self):
        self.scope.setup_for_dio()

        print("Running...")
        self.run_rt()
        self.scope.store_waveform()
