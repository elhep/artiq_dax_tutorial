from artiq.experiment import *
from user import user_id
from common import Scope


class Dio2Excersise(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttls_out = [
            self.get_device("ttl1"),
            self.get_device("ttl3"),
        ]
        self.ttl_in = self.get_device("ttl5")
        self.setattr_device("i2c_switch0")
        self.setattr_device("dio_switch")

        self.scope = Scope(self, user_id)

        self.received = 0


    @kernel
    def init(self):
        self.core.reset()
        self.core.break_realtime()

        self.ttl_in.input()        
        delay(1 * us)
        for ttl in self.ttls_out:
            ttl.output()
            delay(1 * us)


    @kernel
    def run_rt(self):
        self.init()
        N_ITER = 5
        window_duration = 10 * us
        dt = 2 * us


        with parallel:
            # open measuring gate
            self.ttl_in.gate_falling(window_duration)
            self.ttls_out[1].pulse(window_duration)
            
            with sequential:
                delay(1*us)
                for _ in range(N_ITER):
                    self.ttls_out[0].pulse(dt)
                    delay(dt)

        self.received = self.ttl_in.count(now_mu())


    def run(self):
        self.scope.setup()
        self.i2c_switch0.set(7) # EEM0
        
        print(self.dio_switch.get())

        print("Running...")
        self.run_rt()

        print(self.received)

