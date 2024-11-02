from artiq.experiment import *
from user import user_id
from common import Scope
import numpy as np


class Dio3Excersise(EnvExperiment):
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

        self.times = [np.int64(0) for i in range(7)]
        self.received1 = 0
        self.received2 = 0


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

        ttl_slack_ns = 80
        dt = 2 * us

        
        window_duration_us = 10 * us

        # lets assume we are now at time t0
        t0 = now_mu()

        # open gate window for <window_duration_us> 
        # this moves the time cursor to the end of the gate window...
        gate_end_mu = self.ttl_in.gate_rising(window_duration_us)   # cursor at t1 = t0 + window_duration_us
        self.times[0] = now_mu() - t0

        # ... so to use one of the DIO outputs as visualisation of the gate
        # we need to move it back to the beginning of the window 
        delay(-window_duration_us)  # cursor t2 back at t0
        self.times[1] = now_mu() - t0
        self.ttls_out[1].pulse(window_duration_us)  # cursor at t3 = t0 + window_duration_us
        self.times[2] = now_mu() - t0
        delay(-window_duration_us)  # cursor t4 back at t0
        self.times[3] = now_mu() - t0

        # just for visualisation
        delay(1 * us) # cursor at t5 = t0 + 1 us
        self.times[4] = now_mu() - t0
        N_ITER = 5
        for i in range(N_ITER):
            # each loop iteration moves the cursor by 2*dt
            self.ttls_out[0].pulse(dt)
            delay(dt)
        
        self.times[5] = now_mu() - t0

        # so at the and of the loop the cursor is at t0 + 1 us + N_ITER * 2 * dt
        # which is: t0 + 1 us + 5 * 2 * 2 us = t0 + 21 us

        t_middle = t0 + self.core.seconds_to_mu(6 * us) # at this position we should see 2 rising edges
        self.received1 = self.ttl_in.count(t_middle)

        self.times[6] = now_mu() - t0
        self.received2 = self.ttl_in.count(gate_end_mu)


    def run(self):
        self.scope.setup()
        self.i2c_switch0.set(7) # EEM0
        
        print(self.dio_switch.get())

        print("Running...")
        self.run_rt()

        print(self.received1, self.received2)

        dt = [self.core.mu_to_seconds(t) * 1e6 for t in self.times]
        print(dt)
