from artiq.experiment import *
from user import user_id
from common import Scope


class Timing3ExcerciseSolution(EnvExperiment):
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

        self.ttl1.pulse(1*us)
        print(now_mu())
        delay(1*us)
        self.ttl3.pulse(1*us)

        # END SOLUTION

        # This commmand downloads the waveform from the scope
        self.scope.store_waveform()
