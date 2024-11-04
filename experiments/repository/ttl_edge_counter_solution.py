from artiq.experiment import *
from user import user_id
from common import Scope
import numpy as np


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
    def run(self):
        N_PULSES = 60
        PERIOD_US = 1 * us
        self.scope.setup_for_dio()

        # Reset our system after previous experiment, set SYSTEM time marker 
        # in the future and ensure that our TTL channels are configured as inputs
        # and outputs       
        self.init()

        # ----------------------------------------------------------------------
        # Make use of 'parallel' and 'sequential' blocks. Open gate window of TTL
        # Edge Counter for N_PULSES*PERIOD_US (this advances timer pointer) and
        # in parallel with it generate square-like signal on ttl1 output.
        with parallel:
            self.ttl_edge_counter.gate_both(N_PULSES*PERIOD_US)
            with sequential:
                for _ in range(N_PULSES):
                    self.ttl1.pulse(PERIOD_US / 2)
                    delay(PERIOD_US / 2)

        # Fetch counted events. Note that gateware EdgeCounter allows to capture
        # much bigger amounts of input events than simple TTL input without causing
        # RTIOOverflow.
        print(self.ttl_edge_counter.fetch_count())
        # ----------------------------------------------------------------------
        self.scope.store_waveform()
