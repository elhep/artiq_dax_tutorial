from artiq.experiment import *

class TimingExcercise(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.ttl = self.get_device("ttl0")
        self.setattr_device("scope")
        self.setattr_argument(
            f"FirstPulseWidth", NumberValue(
                default = 1,
                ndecimals = 0,
                unit = "us",
                type = "int",
                step = 1,
                min = 1,
                max = 10
            )
        )
        self.setattr_argument(
            f"DelayToNextPulse", NumberValue(
                default = 1,
                ndecimals = 0,
                unit = "us",
                type = "int",
                step = 1,
                min = 1,
                max = 10
            )
        )
        self.setattr_argument(
            f"SecondPulseWidth", NumberValue(
                default = 1,
                ndecimals = 0,
                unit = "us",
                type = "int",
                step = 1,
                min = 1,
                max = 10
            )
        )
        self.urukul = self.get_device("urukul0_cpld")
        self.urukul_channels = [self.get_device(f"urukul0_ch{i}") fo  i in range(2)]



    @kernel
    def run(self):
        self.setup_scope()
        # Reset our system after previous experiment
        self.core.reset()

        # Set SYSTEM time pointer in future
        self.core.break_realtime()

        self.urukul.init()
        for ch in self.urukul_channels:
            ch.init()
            ch.sw.off()
            ch.set_att(10.0)
            ch.set(frequency=10*MHz)

        with parallel:
            with sequential:
                self.urukul_channels[1].sw.on()
                delay(1 * us)
                self.urukul_channels[1].sw_off()
                delay(1 * us)
                self.urukul_channels[0].sw.on()
                delay(1 * us)
                self.urukul_channels[0].sw.off()
            self.ttl.pulse(2 * us)
            
            
    

        with open(f"parallel.png", "wb") as f:
            f.write(self.scope.get_screen_png())



    def setup_scope(self):
        # Oscilloscope channels are counted from 1 to 4
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

        self.scope.set_channel(
            channel=2,
            vertical_scale=1,
            vertical_position=1.0,
            termination_fifty_ohms=True,
            label="Urukul 0",
            ac_coupling=True
        )

        self.scope.set_channel(
            channel=3,
            vertical_scale=1,
            vertical_position=-1.0,
            termination_fifty_ohms=True,
            label="Urukul 1",
            ac_coupling=True
        )

        # Waveform time will be 10*horizontal scale
        self.scope.set_horizontal_scale(100*ns)
        self.scope.set_horizontal_position(400*ns)

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