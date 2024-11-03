from artiq.experiment import *
from user import user_id
from common import Scope
import numpy

class FastinoBasicExcercise(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl = self.get_device("ttl1") # As a trigger
        self.fastino = self.get_device("fastino0")
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

        # Use these parameters
        Amplitude = 2 * V
        sample_num = 12

        try:
            for i in range(sample_num):
                self.fastino.set_dac(dac=0, voltage= 0.0 ) # <-- your function here, instead of 0.0
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
            delay(40*us)
            self.fastino.set_dac(dac=0, voltage=0.0*V)
            # Get scope image
            self.scope.store_waveform()

