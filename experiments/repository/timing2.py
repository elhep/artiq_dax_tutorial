from artiq.experiment import *

class Timing2Excercise(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl = self.get_device("ttl0")
        self.setattr_device("scope")
        self.setattr_argument(
            f"Delay", NumberValue(
                default = 1000,
                ndecimals = 0,
                unit = "ns",
                type = "int",
                step = 1,
                min = 10,
                max = 10000,
                scale=1
            )
        )




    @kernel
    def run(self):
        self.setup_scope()
        # Reset our system after previous experiment
        self.core.reset()

        # Set SYSTEM time pointer in future
        self.core.break_realtime()

        for i in range(10000000):
            self.ttl.set_o(True)
            delay(self.Delay * ns)
            self.ttl.set_o(False)
            delay(self.Delay * ns)


    def setup_scope(self):
        self.scope.reset()

        self.scope.set_current_datetime()

        self.scope.set_channel(
            channel=1,
            vertical_scale=2.5,
            vertical_position=3,
            termination_fifty_ohms=False,
            label="DIO SMA 0",
            ac_coupling=False
        )

        # Waveform time will be 10*horizontal scale
        self.scope.set_horizontal_scale(1000*ns)
        self.scope.set_horizontal_position(4000*ns)

        # Slope: RISE/FALL
        # Mode: NORMAL/AUTO
        self.scope.set_trigger(
            channel=1,
            level=2.5,
            slope="RISE",
            mode="NORMAL"
        )
        self.scope.start_acquisition()
        sleep(3)