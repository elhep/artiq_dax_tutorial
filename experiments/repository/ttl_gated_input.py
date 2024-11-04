from artiq.experiment import *
from user import user_id
from common import Scope


class TTLGatedInputExcersise(EnvExperiment):
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
        '''
        TODO: Place your code here

        Write experiment that counts events (both rising and falling edge) of signal
        fed from self.ttl1 to self.ttl5.
        Use self.ttl3 as an indicator of when the gate for input events is open.
        Make use of <TTL_INPUT>.count() and <TTL_INPUT>.gate_both().

        Remember to synchronise wall clock with local time pointer by using
        'self.core.wait_until_mu()'.
        '''
        # ----------------------------------------------------------------------
        self.scope.store_waveform()
