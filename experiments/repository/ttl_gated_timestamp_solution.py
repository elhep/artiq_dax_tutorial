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
        
        # Open gate window for the time of incoming signals.
        # Be aware that this method advances local time pointer by the duration
        # of the open gate. It does, however, return the time pointer at the end
        # of the gate window. It allows us to know when to stop counting input events.
        gate_end_mu = self.ttl5.gate_both(N_PULSES*PERIOD_US)
        
        i = 0
        
        # <TTL_INPUT>.timestamp_mu(time_in_mu) returns the timestamp of the next
        # input event, or -1 if the hardware timestamp counter reaches the given
        # value (here: gate_end_mu) before an event is received.
        while i < len(self.timestamps):
            self.timestamps[i] = self.ttl5.timestamp_mu(gate_end_mu)
            i = i + 1
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
