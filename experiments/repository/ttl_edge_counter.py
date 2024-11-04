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
        '''
        TODO: Place your code here

        Write missing part of the experiment that generates square-like signal
        on self.ttl1 that lasts 8 us and has period of 1 us. This signal is fed
        by wire to self.ttl5. Count both rising and falling edges of using
        self.ttle_edge_counter device. 

        Constructs such as 'with parallel', 'with sequential' might be
        helpful, as well as ttl_edge_counter's methods: 'gate_both()' and 'fetch_count()'.
        '''
        # ----------------------------------------------------------------------
        self.scope.store_waveform()
