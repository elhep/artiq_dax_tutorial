from artiq.experiment import *
from user import user_id
from common import Scope
import numpy as np


class FastinoInterpolationExcercise(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl = self.get_device("ttl1") # As a trigger
        self.fastino = self.get_device("fastino0")

        # Lots of arguments, scroll down
        self.setattr_argument(
            f"Function", EnumerationValue(
                ["Sine", "Square", "Sawtooth", "Triangle", "Custom"],
                default="Sawtooth"
            )
        )

        self.setattr_argument(
            f"Amplitude", NumberValue(
                default = 2,
                precision = 3,
                unit = "V",
                type = "float",
                step = 0.5,
                min = 0.1,
                max = 9.99,
                scale=1
            ),
            tooltip="Sample sequence will be normalized to this amplitude."
        )

        self.setattr_argument(
            f"Sample_number", NumberValue(
                default = 16,
                precision = 0,
                unit = "",
                type = "int",
                step = 1,
                min = 2,
                max = 1000,
                scale=1
            ),
            tooltip="Number of samples in the sequence"
        )

        self.setattr_argument(
            f"Enable_interpolation", BooleanValue(default = False)
        )

        self.setattr_argument(
            f"Interpolation_rate", NumberValue(
                default = 8,
                precision = 0,
                unit = "",
                type = "int",
                step = 1,
                min = 1,
                max = 256,
                scale=1
            )
        )

        self.setattr_argument(
            f"Delay_multiplier", NumberValue(
                default = 8,
                precision = 0,
                unit = "",
                type = "int",
                step = 1,
                min = 1,
                max = 256,
                scale=1
            ),
            tooltip="Samples are send every 392 ns times this multiplier."
        )

        self.setattr_argument(
            f"Scope_horizontal_scale", EnumerationValue(
                ["1 us", "2 us", "4 us", "10 us", "20 us", "40 us", "100 us", "200 us", "400 us"],
                default="10 us"
            )
        )

        self.scope = Scope(self, user_id)

    def prepare(self):
        # Sine
        sine = [np.sin(2*np.pi*i/self.Sample_number*2) for i in range(self.Sample_number)]
        # Square
        square = [(i%2) for i in range(self.Sample_number)]
        # Sawtooth
        sawtooth = [(i % (self.Sample_number//2)) for i in range(self.Sample_number)]
        # Triangle
        triangle = [(abs((i % (self.Sample_number//2))-self.Sample_number/4)) for i in range(self.Sample_number)]
        # or just directly declare samples:
        custom = [0.0, 0.5, 0.0, 0.5, 0.0, -0.5, 0.0, -0.5, 0.0]
        samples = {"Sine": sine, "Square": square, "Sawtooth": sawtooth, "Triangle": triangle, "Custom": custom}
        self.samples = samples[self.Function]
        # self.samples = [<function> for i in range(self.Sample_number)]

        # Normalize samples
        self.samples = [self.Amplitude * self.samples[i]/max(self.samples) for i in range(len(self.samples))]

        # Argument hackery
        self.Scope_horizontal_scale = int(self.Scope_horizontal_scale[:-3])*us
        if not self.Enable_interpolation:
            self.Interpolation_rate = 1

    @kernel
    def run(self):
        # Prepare oscilloscope
        self.scope.setup_for_fastino(horizontal_scale=self.Scope_horizontal_scale)
        # Reset our system after previous experiment
        self.core.reset()

        # Calculate interpolation parameters
        self.fastino.stage_cic(self.Interpolation_rate)
        delay(100*ns)
        # Apply computed parameters
        self.fastino.apply_cic(1)

        # Set SYSTEM time pointer in future
        self.core.break_realtime()
        # Trigger for the oscilloscope
        self.ttl.pulse(self.Scope_horizontal_scale/20)
        # Rewind timeline - Fastino takes around 1.2 us to output a sample
        at_mu(now_mu()-self.core.seconds_to_mu(1.2*us)) 

        try:
            # Iterate over samples
            for sample in self.samples:
                self.fastino.set_dac(dac=0, voltage=sample)
                # Try to change the multiplier; leave 392*ns unchanged
                # (or don't and see what happens, it may be subtle :) )
                delay(392 * self.Delay_multiplier * ns)

# ---------------------------------------------------------------------

        except RTIOUnderflow:
            # Catch RTIO Underflow to leave system in known state
            print("Rtio underflow, cleaning up")
            self.core.break_realtime()

        finally:
            # Clean up even if RTIO Underflow happens
            self.clean_up()
            # Get scope image
            self.scope.store_waveform()

    @kernel
    def clean_up(self):
        # Delay to allow for the interpolated sequence to settle
        delay(self.Scope_horizontal_scale * 10)
        # Set interpolation rate to 1
        self.fastino.stage_cic(1)
        delay(100*ns)
        self.fastino.apply_cic(1)
        delay(8*ns)
        self.fastino.set_dac(dac=0, voltage=0.0*V)
        