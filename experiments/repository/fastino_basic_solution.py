from artiq.experiment import *
from user import user_id
from common import Scope
import numpy

class FastinoBasicExcerciseSolution(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl = self.get_device("ttl1") # As a trigger
        self.fastino = self.get_device("fastino0")

        self.Amplitude = 2 * V

        self.sample_num = 8

        self.scope = Scope(self, user_id)

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
        at_mu(now_mu()-self.core.seconds_to_mu(1.2 * us)) 

        # Calculate and output a sine waveform using numpy.sin
        try:
            for i in range(self.sample_num):
                self.fastino.set_dac(dac=0, voltage=self.Amplitude * numpy.sin(2*numpy.pi*i/self.sample_num*2))
                delay(392 * 1 * ns)

        except RTIOUnderflow:
            # Catch RTIO Underflow to leave system in known state
            print("Rtio underflow, cleaning up")
            self.core.break_realtime()

        finally:
            # Clean up after RTIO Underflow
            self.fastino.set_dac(dac=0, voltage=0.0*V)

            self.scope.store_waveform()

