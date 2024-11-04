from artiq.experiment import *
from user import user_id
from common import Scope
import numpy as np

N_PULSES = 8
PERIOD_US = 1 * us


class TTLGatedTimestampExcersise(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl1 = self.get_device("ttl1")
        self.ttl3 = self.get_device("ttl3")
        self.ttls_out = [self.ttl1, self.ttl3]
        self.ttl5 = self.get_device("ttl5")

        self.scope = Scope(self, user_id)


    def prepare(self):
        self.t0 = np.int64(0)
        self.timestamps = [np.int64(0) for i in range(N_PULSES)]       

    @kernel
    def init(self):
        self.core.reset()
        self.core.break_realtime()

        self.ttl5.input()        
        delay(1 * us)
        for ttl in self.ttls_out:
            ttl.output()
            delay(1 * us)


    @kernel
    def run_rt(self):        
        self.scope.setup_for_dio()

        # Reset our system after previous experiment, set SYSTEM time marker 
        # in the future and ensure that our TTL channels are configured as inputs
        # and outputs       
        self.init()

        # t0 will be our LOCAL time marker. For now it points the same point in
        # timeline as SYSTEM: now marker
        self.t0 = now_mu()

        # The loop below generates a 'square' wave on TTL1 output channel.
        # Genrated wave has period of PERIOD_US (1 us) and lasts for
        # N_SAMPLES * PERIOD_US (8 us)
        for _ in range(N_PULSES):
            self.ttl1.pulse(PERIOD_US / 2)
            delay(PERIOD_US / 2)

        # Set system time pointer back to t0
        at_mu(self.t0)
        # ----------------------------------------------------------------------
        '''
        TODO: Place your code here

        Write experiment that registers input events (both rising and falling edge)
        of signal fed from self.ttl1 to self.ttl5.
        Make use of <TTL_INPUT>.gate_both() and <TTL_INPUT>.timestamp_mu() and place
        received events in self.timestamps list
        
        '''
        # ----------------------------------------------------------------------
        self.scope.store_waveform()


    def run(self):
        self.run_rt()
        
        time_values_us = []
        for tstmp in self.timestamps:
            if tstmp != -1: # if tstmp == -1, there was a timeout before an input event was received.
                t = self.core.mu_to_seconds(tstmp - self.t0)*1e6
                time_values_us.append(t)

        print("timestamp-t0 [us]: ", " ".join([f"{tstmp:.2f}" for tstmp in time_values_us]))
