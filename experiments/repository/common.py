import io
import numpy as np

from artiq.experiment import *
from PIL import Image


class Scope:

    def __init__(self, experiment: EnvExperiment, user_id, scope="scope"):
        self.experiment = experiment
        self.user_id = user_id
        self.scope = experiment.get_device(scope)

    def setup_for_all(self, reset=False, sleep_time=3.0, horizontal_scale=1*us):
        self.scope.setup(
            channel_configs=[
                {
                    "channel": 1,
                    "vertical_scale": 2.5,
                    "vertical_position": 3,
                    "termination_fifty_ohms": False,
                    "label": "DIO SMA 1",
                    "ac_coupling": False
                },
                {
                    "channel": 2,
                    "vertical_scale": 2.5,
                    "vertical_position": 1.0,
                    "termination_fifty_ohms": False,
                    "label": "DIO SMA 3",
                    "ac_coupling": False
                },
                {
                    "channel": 3,
                    "vertical_scale": 1,
                    "vertical_position": -1.0,
                    "termination_fifty_ohms": True,
                    "label": "Urukul 0",
                    "ac_coupling": True
                },
                {
                    "channel": 4,
                    "vertical_scale": 0.5,
                    "vertical_position": -3.0,
                    "termination_fifty_ohms": False,
                    "label": "Fastino 0",
                    "ac_coupling": False
                }
            ],
            horizontal_scale=horizontal_scale,
            horizontal_position=4*horizontal_scale,
            trigger_config={
                "channel": 1,
                "level": 2.5,
                "slope": "RISE",
                "mode": "NORMAL"
            },
            queue=True,
            reset=reset
        )
        self.scope.run_queue(sleep_time=sleep_time)

    def setup_for_dio(self, reset=False, sleep_time=3.0, horizontal_scale=1*us):
        self.scope.setup(
            channel_configs=[
                {
                    "channel": 1,
                    "vertical_scale": 2.5,
                    "vertical_position": 1.0,
                    "termination_fifty_ohms": False,
                    "label": "DIO SMA 1",
                    "ac_coupling": False
                },
                {
                    "channel": 2,
                    "vertical_scale": 2.5,
                    "vertical_position": -3,
                    "termination_fifty_ohms": False,
                    "label": "DIO SMA 3",
                    "ac_coupling": False
                },
                {
                    "channel": 3,
                    "enabled": False
                },
                {
                    "channel": 4,
                    "enabled": False
                }
            ],
            horizontal_scale=horizontal_scale,
            horizontal_position=4*horizontal_scale,
            trigger_config={
                "channel": 1,
                "level": 2.5,
                "slope": "RISE",
                "mode": "NORMAL"
            },
            queue=True,
            reset=reset
        )
        self.scope.run_queue(sleep_time=sleep_time)

    def setup_for_urukul(self, reset=False, sleep_time=3.0, horizontal_scale=1*us):
        self.scope.setup(
            channel_configs=[
                {
                    "channel": 1,
                    "enabled": False
                },
                {
                    "channel": 2,
                    "vertical_scale": 2.5,
                    "vertical_position": 1.0,
                    "termination_fifty_ohms": False,
                    "label": "DIO SMA 3",
                    "ac_coupling": False
                },
                {
                    "channel": 3,
                    "vertical_scale": 0.5,
                    "vertical_position": -2.0,
                    "termination_fifty_ohms": True,
                    "label": "Urukul 0",
                    "ac_coupling": True
                },
                {
                    "channel": 4,
                    "enabled": False
                }
            ],
            horizontal_scale=horizontal_scale,
            horizontal_position=4*horizontal_scale,
            trigger_config={
                "channel": 2,
                "level": 2.5,
                "slope": "RISE",
                "mode": "NORMAL"
            },
            queue=True,
            reset=reset
        )
        self.scope.run_queue(sleep_time=sleep_time)

    def setup_for_fastino(self, reset=False, sleep_time=3.0, horizontal_scale=4*us):
        self.scope.setup(
            channel_configs=[
                {
                    "channel": 1,
                    "vertical_scale": 2.5,
                    "vertical_position": 3,
                    "termination_fifty_ohms": False,
                    "label": "DIO SMA 1",
                    "ac_coupling": False
                },
                {
                    "channel": 2,
                    "enabled": False
                },
                {
                    "channel": 3,
                    "enabled": False
                },
                {
                    "channel": 4,
                    "vertical_scale": 0.5,
                    "vertical_position": 0.0,
                    "termination_fifty_ohms": False,
                    "label": "Fastino 0",
                    "ac_coupling": False
                }
            ],
            horizontal_scale=horizontal_scale,
            horizontal_position=4*horizontal_scale,
            trigger_config={
                "channel": 1,
                "level": 2.5,
                "slope": "RISE",
                "mode": "NORMAL"
            },
            queue=True,
            reset=reset
        )
        self.scope.run_queue(sleep_time=sleep_time)

    def store_waveform(self):
        im = Image.open(io.BytesIO(self.scope.get_screen_png()))
        im = np.array(im)
        im = np.rot90(im, 1, (0, 1))
        im = np.flip(im, 1)
        im = np.flip(im, 0)
        self.experiment.set_dataset(
            f"scope_{self.user_id}", im, broadcast=True)
