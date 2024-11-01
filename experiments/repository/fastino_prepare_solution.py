from artiq.experiment import *
from user import user_id
from common import Scope
import numpy as np

class FastinoPrepareExcerciseSolution(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl = self.get_device("ttl1") # As a trigger
        self.fastino = self.get_device("fastino0")

        self.Amplitude = 2 * V
        self.sample_num = 200

        self.scope = Scope(self, user_id)

    def prepare(self):
        # Other functions to do: square, sawtooth, triangle
        self.samples = [np.sin(2*np.pi*i/self.sample_num*2) for i in range(self.sample_num)]
        # self.samples = [(i%2) for i in range(self.sample_num)]
        # self.samples = [(i % (self.sample_num//2)) for i in range(self.sample_num)]
        # self.samples = [(abs((i % (self.sample_num//2))-self.sample_num/4)) for i in range(self.sample_num)]
        # self.samples = [<function> for i in range(self.sample_num)]
        # or just directly declare samples:
        # self.samples = [0.0, 0.5, 0.0, 0.5, 0.0, -0.5, 0.0, -0.5, 0.0]

        # Normalize samples
        self.samples = [self.Amplitude * self.samples[i]/max(self.samples) for i in range(len(self.samples))]
        # Add 0 V sample to the end of the sequence to ensure proper start of the next experiment
        self.samples = self.samples + [0.0]

    @kernel
    def run(self):
        # Prepare oscilloscope
        self.scope.setup_for_fastino()
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
                delay(392 * 1 * ns)

        except RTIOUnderflow:
            # Catch RTIO Underflow to leave system in known state
            print("Rtio underflow, cleaning up")
            self.core.break_realtime()

        finally:
            # Clean up even if RTIO Underflow happens
            self.fastino.set_dac(dac=0, voltage=0.0*V)

            self.scope.store_waveform()

