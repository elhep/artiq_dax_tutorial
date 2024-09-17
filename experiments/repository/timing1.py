from artiq.experiment import *

class Timing1Excercise(EnvExperiment):
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
                max = 10,
                scale=1
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
                max = 10,
                scale=1
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
                max = 10,
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

        # t will be our LOCAL time pointer. For now it points the same point in timeline as SYSTEM pointer
        t = now_mu()

        # Let's drive single pulse. With delay() we change system pointer relative: 
        # software does not care about the exact point in timeline but we know that next event will take place exactly "FirstPulseWidth" microseconds after ttl.set_o(True) command
        self.ttl.set_o(True)
        delay(self.FirstPulseWidth * us)
        self.ttl.set_o(False)

        # Because of delay() function, SYSTEM pointer is DelayValue further. Let's drive another pulse using at_mu:
        at_mu(t + # start with local pointer
              self.core.seconds_to_mu(self.FirstPulseWidth * us) + # add FirstPulseWidth to "catch" system pointer
              self.core.seconds_to_mu(self.DelayToNextPulse * us))  # add Delay value
        # You can try passing a negative value to DelayToNextPulse and see what happens when system tries to control IO in the past.

        self.ttl.pulse(self.SecondPulseWidth * us)

        # Pulse method consists delay() function inside. SYSTEM pointer is now at falling edge of the pulse.

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