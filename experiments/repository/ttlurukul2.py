from artiq.experiment import *
from user import user_id
from common import Scope

class TTLUrukul2(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("ttl3")
        self.urukul = self.get_device("urukul0_cpld")
        self.urukul_channels = [
            self.get_device(f"urukul0_ch0")
        ]
        self.scope = Scope(self, user_id)

    @kernel
    def run(self):
        # Prepare oscilloscope for experiment
        self.scope.setup_for_urukul(horizontal_scale=100*ns)

        # Reset our system after previous experiment
        self.core.reset()

        # Set software (now) counter in the future
        self.core.break_realtime()

        # Intialize Urukul and Urukul channels
        self.urukul.init()
        for ch in self.urukul_channels:
            ch.init()
            ch.sw.off()
            ch.set_att(0.0)
            ch.set(frequency=25*MHz)
        delay(10 * ms)

        # SOLUTION

        # TODO Your code should be here

        # END SOLUTION

        # This commmand downloads the waveform from the scope
        self.scope.store_waveform()
