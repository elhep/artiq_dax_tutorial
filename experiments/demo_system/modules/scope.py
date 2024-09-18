from dax.experiment import *

from time import sleep
import numpy as np
import io
from artiq.experiment import *
from PIL import Image
import io


class ScopeModule(DaxModule):
    """
    Module to control textronix scope used in the demo
    """

    def build(self, *, user_id: str) -> None:
        # Get the controller
        self.in_sim = '_dax_sim_config' in self.get_device_db()
        self.user_id = user_id
        if not self.in_sim:
            self.scope = self.get_device("scope")
            self.update_kernel_invariants("scope")

    def init(self):
        self.setup()

    def post_init(self):
        pass

    def setup(self):
        if not self.in_sim:
            # Oscilloscope channels are counted from 1 to 4
            self.scope.reset()

            self.scope.set_current_datetime()

            self.scope.set_channel(
                channel=1,
                vertical_scale=2.5,
                vertical_position=3,
                termination_fifty_ohms=False,
                label="DIO SMA 0",
                ac_coupling=False
            )

            self.scope.set_channel(
                channel=2,
                vertical_scale=1,
                vertical_position=1.0,
                termination_fifty_ohms=True,
                label="Urukul 0",
                ac_coupling=True
            )

            self.scope.set_channel(
                channel=3,
                vertical_scale=1,
                vertical_position=-1.0,
                termination_fifty_ohms=True,
                label="Urukul 1",
                ac_coupling=True
            )

            self.scope.set_channel(
                channel=4,
                vertical_scale=0.5,
                vertical_position=-3.0,
                termination_fifty_ohms=True,
                label="Phaser RF 0",
                ac_coupling=True
            )

            # Waveform time will be 10*horizontal scale
            self.scope.set_horizontal_scale(100*ns)
            self.scope.set_horizontal_position(400*ns)

            # Slope: RISE/FALL
            # Mode: NORMAL/AUTO
            self.scope.set_trigger(
                channel=1,
                level=2.5,
                slope="RISE",
                mode="NORMAL"
            )
            self.scope.start_acquisition()
            sleep(3)
    
    
    def store_waveform(self):
        if not self.in_sim:
            im = Image.open(io.BytesIO(self.scope.get_screen_png()))
            im = np.array(im)
            im = np.rot90(im, 1, (0, 1))
            im = np.flip(im, 1)
            im = np.flip(im, 0)
            self.set_dataset(
                f"scope_{self.user_id}", im, broadcast=True)
