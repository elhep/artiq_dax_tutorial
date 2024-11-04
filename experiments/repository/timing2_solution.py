from artiq.experiment import *
from user import user_id
from common import Scope


class Timing2Solution(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl1")
        self.setattr_device("ttl3")
        self.scope = Scope(self, user_id)

    @kernel
    def run(self):
        # Prepare oscilloscope for experiment
        self.scope.setup_for_dio(horizontal_scale=1*us)

        # Reset our system after previous experiment
        self.core.reset()

        # Set software (now) counter in the future
        self.core.break_realtime()
        
        # SOLUTION

        # We need to store the current counter value for later use
        t = now_mu()

        # This advances the counter by 3 us
        self.ttl1.pulse(3*us)

        # Let's move counter to the value corresponding to the start of
        # the second pulse.
        at_mu(t + self.core.seconds_to_mu(2*us))
        self.ttl3.pulse(4*us)

        # END SOLUTION

        # This commmand downloads the waveform from the scope
        self.scope.store_waveform()
