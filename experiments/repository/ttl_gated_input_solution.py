from artiq.experiment import *
from user import user_id
from common import Scope


class TTLGatedInputExcersiseSolution(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl1 = self.get_device("ttl1")
        self.ttl3 = self.get_device("ttl3")
        self.ttls_out = [self.ttl1, self.ttl3]
        self.ttl5 = self.get_device("ttl5")

        self.scope = Scope(self, user_id)


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
    def run(self):
        PERIOD_US = 1 * us
        N_PULSES = 8
        self.scope.setup_for_dio()
        
        # Reset our system after previous experiment, set SYSTEM time marker 
        # in the future and ensure that our TTL channels are configured as inputs
        # and outputs       
        self.init()

        # t0 will be our LOCAL time marker. For now it points the same point in
        # timeline as SYSTEM: now marker
        t0 = now_mu()

        # The loop below generates a 'square' wave on TTL1 output channel.
        # Genrated wave has period of PERIOD_US (1 us) and lasts for
        # N_SAMPLES * PERIOD_US (8 us)
        for _ in range(N_PULSES):
            self.ttl1.pulse(PERIOD_US / 2)
            delay(PERIOD_US / 2)

        # Set system time pointer back to t0
        at_mu(t0)
        # ----------------------------------------------------------------------
        # Use self.ttl3 as an indicator of when the gate for input events is open
        self.ttl3.on()

        # Open gate window for the time of incoming signals.
        # Be aware that this method advances local time pointer by the duration
        # of the open gate. It does, however, return the time pointer at the end
        # of the gate window. It allows us to know when to stop counting input events.
        gate_end_mu = self.ttl5.gate_both(PERIOD_US * N_PULSES)
        self.ttl3.off()

        # Make that the wall clock catches up with the place our local time pointer
        # is placed.
        self.core.wait_until_mu(now_mu())

        # Count events gathered on the input self.ttl5 channel up until the timestamp
        # indicated by the "gate_both" method.
        received = self.ttl5.count(gate_end_mu)
        
        print(received)
        # ----------------------------------------------------------------------
        self.scope.store_waveform()
