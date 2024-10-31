from artiq.experiment import *


class Test(EnvExperiment):
    kernel_invariants = {'urukul_channels'}
    def build(self):
        self.setattr_device("core")
        
        self.setattr_device("ttl1")
        self.setattr_device("ttl3")
        self.setattr_device("ttl5") # Input
        self.setattr_device("urukul0_cpld")
        self.setattr_device("urukul0_ch0")
        self.urukul_channels = [
            self.urukul0_ch0
        ]
        self.setattr_device("fastino0")

    @kernel
    def loop_procedure(self):
        for i in range(100):
            t = 100 * us
            with parallel:
                self.ttl1.pulse(t)
                self.ttl3.pulse(t)
                # Due to switching 10 MHz signal output on oscilloscope may vary
                self.urukul0_ch0.sw.pulse(t)
                with sequential:
                    self.fastino0.set_dac(dac=0, voltage=3*V)
                    delay(t)
                    self.fastino0.set_dac(dac=0, voltage=0*V)
            delay(t)

    @kernel
    def run(self):
        self.core.break_realtime()
        
        while True:
            self.loop_procedure()
