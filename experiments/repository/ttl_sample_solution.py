from artiq.experiment import *
from user import user_id
from common import Scope


class TTLSampleExcersiseSolution(EnvExperiment):
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
        N_SAMPLES = 8       
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
        for _ in range(N_SAMPLES):
            self.ttl1.pulse(PERIOD_US / 2) 
            delay(PERIOD_US / 2)
        
        # Set system time pointer back to t0
        at_mu(t0)

        # ----------------------------------------------------------------------
        # Since we want to sample each state (both on and off) we need to sample
        # signal twice during one period. 
        levels = [0 for n in range(2*N_SAMPLES)]
        
        # Delaying local time pointer so it is aligned with the middle point
        # of the first upper or lower input state.
        delay(PERIOD_US / 4)
        for i in range(2*N_SAMPLES):
            self.ttl5.sample_input() # instructs ARTIQ to sample input at the exact cursor position
            delay(PERIOD_US / 2)


        # Now retrieve sampled values and place them in a list
        for i in range(2 * N_SAMPLES):
            levels[i] = self.ttl5.sample_get()

        print(levels)
        # ----------------------------------------------------------------------
        self.scope.store_waveform()

