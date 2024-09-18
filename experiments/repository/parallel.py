from artiq.experiment import *
from user import user_id
from common import Scope

class ParallelExcercise(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl = self.get_device("ttl0")
        self.urukul = self.get_device("urukul0_cpld")
        self.urukul_channels = [self.get_device(f"urukul0_ch{i}") for  i in range(2)]
        self.scope = Scope(self, user_id)



    @kernel
    def run(self):
        self.scope.setup()
        # Reset our system after previous experiment
        self.core.reset()
    
        # Set SYSTEM time pointer in future
        self.core.break_realtime()

        self.urukul.init()
        for ch in self.urukul_channels:
            ch.init()
            ch.sw.off()
            ch.set_att(0.0)
            ch.set(frequency=25*MHz)
            
        delay(10 * ms)
        with parallel:
            self.ttl.on()
            self.urukul_channels[0].sw.on()
            self.urukul_channels[1].sw.on()
            with sequential:
                delay(200 * ns)
                self.urukul_channels[1].sw.off()
                # delay(200 * ns)
                # delay(200 * ns)
                self.urukul_channels[0].sw.off()
            
        delay(100 * us)
        self.ttl.off()
        self.scope.store_waveform()
