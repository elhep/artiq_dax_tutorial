from artiq.experiment import *

class DMAExcercise(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")
        self.ttl = self.get_device("ttl0")
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
    def record(self):
        with self.core_dma.record("pulses"):
            for i in range(50):
                self.ttl.set_o(True)
                delay(self.Delay * ns)
                self.ttl.set_o(False)
                delay(self.Delay * ns)

    @kernel
    def run(self):
        # Reset our system after previous experiment
        self.core.reset()

        self.record()
        pulses_handle = self.core_dma.get_handle("pulses")

        # Set SYSTEM time pointer in future
        self.core.break_realtime()

        for i in range(50):
            # execute RTIO operations in the DMA buffer
            # each playback advances the timeline by 50*(X+X) ns
            self.core_dma.playback_handle(pulses_handle)