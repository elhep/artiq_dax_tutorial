from artiq.experiment import *
from user import user_id
from common import Scope
import numpy as np


class FastinoInterpolationExcerciseSolution(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl = self.get_device("ttl1") # As a trigger
        self.fastino = self.get_device("fastino0")

        self.Amplitude = 2 * V
        self.sample_num = 16
        self.interpolation_rate = 8

        self.scope = Scope(self, user_id)

    def prepare(self):
        # Other functions to do: square, sawtooth, triangle
        # Sine
        # self.samples = [np.sin(2*np.pi*i/self.sample_num*2) for i in range(self.sample_num)]
        # Square
        # self.samples = [(i%2) for i in range(self.sample_num)]
        # Sawtooth
        self.samples = [(i % (self.sample_num//2)) for i in range(self.sample_num)]
        # Triangle
        # self.samples = [(abs((i % (self.sample_num//2))-self.sample_num/4)) for i in range(self.sample_num)]
        # self.samples = [<function> for i in range(self.sample_num)]
        # or just directly declare samples:
        # self.samples = [0.0, 0.5, 0.0, 0.5, 0.0, -0.5, 0.0, -0.5, 0.0]

        # Normalize samples
        self.samples = [self.Amplitude * self.samples[i]/max(self.samples) for i in range(len(self.samples))]

    @kernel
    def run(self):
        # Prepare oscilloscope
        self.scope.setup_for_fastino()
        # Reset our system after previous experiment
        self.core.reset()

        # Calculate interpolation parameters
        self.fastino.stage_cic(self.interpolation_rate)
        delay(100*ns)
        # Apply computed parameters
        self.fastino.apply_cic(1)

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
                # Try to adjust the multiplier (leave 392 ns unchanged)
                delay(392 * 8 * ns)

        except RTIOUnderflow:
            # Catch RTIO Underflow to leave system in known state
            print("Rtio underflow, cleaning up")
            self.core.break_realtime()
            raise

        finally:
            # Clean up even if RTIO Underflow happens
            self.clean_up()
            
            self.scope.store_waveform()

    @kernel
    def clean_up(self):
        # Delay to allow for the interpolated sequence to finish
        delay(self.interpolation_rate * us)
        # Mark the end of the experiment with ttl
        self.ttl.pulse(50*ns)
        # Set interpolation rate to 1
        self.fastino.stage_cic(1)
        delay(100*ns)
        self.fastino.apply_cic(1)
        delay(8*ns)
        # delay(392 * 2 * ns)
        # delay(392 * ns)
        self.fastino.set_dac(dac=0, voltage=0.0*V)
        