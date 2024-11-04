from artiq.experiment import *
from user import user_id
from common import Scope


class TTLUrukul1(EnvExperiment):
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
        # Note that, although output is disabled, the frequency is set to 25 MHz
        # and DDS is running.
        self.urukul.init()
        self.urukul_channels[0].init()
        self.urukul_channels[0].sw.off()
        self.urukul_channels[0].set_att(0.0)
        self.urukul_channels[0].set(frequency=25*MHz, phase=0.0, amplitude=1.0)
        # Wait for channel to be fully operational
        delay(100 * us)

        # SOLUTION

        # TODO Your code should be here

        # END SOLUTION

        # This commmand downloads the waveform from the scope
        self.scope.store_waveform()
