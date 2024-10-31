from artiq.experiment import *
from time import sleep


class Test(EnvExperiment):
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
    def init(self):
        self.core.reset()

        self.ttl5.input()

        self.urukul0_cpld.init()
        for urukul_ch in self.urukul_channels:
            urukul_ch.init()
            urukul_ch.sw.off()
            urukul_ch.set_att(31.5)

        self.fastino0.init()

    @kernel
    def run(self):
        self.init()

        # First setup Urukuls
        self.urukul0_ch0.set(frequency=10*MHz)
        self.urukul0_ch0.set_att(10.0)
        # self.urukul0_ch0.sw.on()

        self.fastino0.set_dac(dac=0, voltage=0*V)