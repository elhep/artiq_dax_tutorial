from artiq.experiment import *
from user import user_id
from common import Scope

N_STATES = 10
DELAY_NS = 8

class Dio1Excersise(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttls_out = [
            self.get_device("ttl1"),
            self.get_device("ttl3"),
        ]
        self.ttl_in = self.get_device("ttl5")
        self.setattr_device("i2c_switch0")
        self.setattr_device("dio_switch")

        self.states = [False for i in range(N_STATES)]

        self.scope = Scope(self, user_id)


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

        self.ttls_out[0].on()
        self.ttls_out[1].on()
        for i in range(N_STATES):
            self.ttl_in.sample_input()
            delay(DELAY_NS * ns)

        delay(100*ns)
        self.ttls_out[0].off()
        self.ttls_out[1].off()

        for i in range(N_STATES):
            self.states[i] = self.ttl_in.sample_get()
    

    def run(self):
        self.scope.setup()
        self.i2c_switch0.set(7) # EEM0
        
        print(self.dio_switch.get())

        print("Running...")
        self.run_rt()

        times = [i * DELAY_NS for i in range(N_STATES)]

        print("States: ", list(zip(self.states, times)))
