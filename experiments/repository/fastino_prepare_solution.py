from artiq.experiment import *
from user import user_id
from common import Scope
import numpy

class FastinoPrepareExcerciseSolution(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl = self.get_device("ttl1") # As a trigger
        self.fastino = self.get_device("fastino0")

        self.setattr_argument(
            f"Scope_horizontal_scale", EnumerationValue(
                ["1 us", "2 us", "4 us", "10 us", "20 us", "40 us", "100 us", "200 us", "400 us"],
                default="10 us"
            )
        )

        self.scope = Scope(self, user_id)

    def prepare(self):
        # Use these parameters
        self.Amplitude = 2 * V
        self.sample_num = 200

        # Other functions to do: square, sawtooth, triangle
        # Sine
        self.samples = [numpy.sin(2*numpy.pi*i/self.sample_num*2) for i in range(self.sample_num)]
        # Square
        # self.samples = [(i%2) for i in range(self.sample_num)]
        # Sawtooth
        # self.samples = [(i % (self.sample_num//2)) for i in range(self.sample_num)]
        # Triangle
        # self.samples = [(abs((i % (self.sample_num//2))-self.sample_num/4)) for i in range(self.sample_num)]
        # self.samples = [<function> for i in range(self.sample_num)]
        # or just directly declare samples:
        # self.samples = [0.0, 0.5, 0.0, 0.5, 0.0, -0.5, 0.0, -0.5, 0.0]

        # Normalize samples
        self.samples = [self.Amplitude * self.samples[i]/max(self.samples) for i in range(len(self.samples))]

        # Argument hackery
        self.Scope_horizontal_scale = int(self.Scope_horizontal_scale[:-3])*us

    @kernel
    def run(self):
        # Prepare oscilloscope
        self.scope.setup_for_fastino(horizontal_scale=self.Scope_horizontal_scale)
        # Reset our system after previous experiment
        self.core.reset()

        # Set SYSTEM time pointer in future
        self.core.break_realtime()
        # Trigger for the oscilloscope
        self.ttl.pulse(50*ns)
        # Rewind timeline - Fastino takes around 1.2 us to output a sample
        at_mu(now_mu()-self.core.seconds_to_mu(1.2*us)) 

        try:
            # Iterate over samples
            for sample in self.samples:
                self.fastino.set_dac(dac=0, voltage=sample)
                # Try to change the multiplier; leave 392*ns unchanged
                # (or don't and see what happens, it may be subtle :) )
                delay(392*ns * 1)

# ---------------------------------------------------------------------

        except RTIOUnderflow:
            # Catch RTIO Underflow to leave system in known state
            print("Rtio underflow, cleaning up")
            self.core.break_realtime()

        finally:
            # Clean up even if RTIO Underflow happens
            delay(self.Scope_horizontal_scale * 10)
            self.fastino.set_dac(dac=0, voltage=0.0*V)
            # Get scope image
            self.scope.store_waveform()

