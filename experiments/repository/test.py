from artiq.experiment import *
from time import sleep


class Test(EnvExperiment):
    def build(self):
        self.setattr_device("core")
        self.setattr_device("core_dma")

        self.setattr_device("ttl0")
        self.setattr_device("urukul0_cpld")
        self.setattr_device("urukul0_ch0")
        self.setattr_device("urukul0_ch1")
        self.urukul_channels = [
            self.urukul0_ch0,
            self.urukul0_ch1
        ]
        self.setattr_device("phaser0")

        self.setattr_device("scope")

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

        self.scope.set_channel(
            channel=4,
            vertical_scale=0.5,
            vertical_position=-3.0,
            termination_fifty_ohms=True,
            label="Phaser RF 0",
            ac_coupling=True
        )

        # Waveform time will be 10*horizontal scale
        self.scope.set_horizontal_scale(100 * ns)
        self.scope.set_horizontal_position(400 * ns)

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

    @kernel
    def init(self):
        self.core.reset()

        self.urukul0_cpld.init()
        for urukul_ch in self.urukul_channels:
            urukul_ch.init()
            urukul_ch.sw.off()
            urukul_ch.set_att(31.5)

    @kernel
    def set_phaser_frequencies(self, phaser, duc, osc):
        self.core.break_realtime()
        phaser.init()
        delay(1 * ms)
        phaser.channel[0].set_duc_frequency(duc)
        phaser.channel[0].set_duc_cfg()
        phaser.channel[0].set_att(6 * dB)
        phaser.channel[1].set_duc_frequency(-duc)
        phaser.channel[1].set_duc_cfg()
        phaser.channel[1].set_att(6 * dB)
        phaser.duc_stb()
        delay(1 * ms)
        for i in range(len(osc)):
            phaser.channel[0].oscillator[i].set_frequency(osc[i])
            phaser.channel[0].oscillator[i].set_amplitude_phase(.2)
            phaser.channel[1].oscillator[i].set_frequency(-osc[i])
            phaser.channel[1].oscillator[i].set_amplitude_phase(.2)
            delay(1 * ms)

    @kernel
    def run_rt(self):
        self.init()

        # First setup Urukuls
        self.urukul0_ch0.set(frequency=10 * MHz)
        self.urukul0_ch0.set_att(10.0)
        self.urukul0_ch0.sw.on()

        self.urukul0_ch1.set(frequency=20 * MHz)
        self.urukul0_ch1.set_att(10.0)
        self.urukul0_ch1.sw.on()

        # Now setup Phaser
        duc = (1) * 10 * MHz
        osc = [1 * MHz]
        self.set_phaser_frequencies(self.phaser0, duc, osc)

        delay(1 * ms)

        # Starting TTL sequence will trigger the scope
        for i in range(100):
            self.ttl0.pulse(100 * ns)
            delay(100 * ns)

    def run(self):
        # Prepare a test waveform consisting of:
        # CH0: bunch of impulses of 100ns width with 100ns spacing
        # CH1: sine wave at 10MHz
        # CH2: sine wave at 20MHz
        # CH3: ?

        self.setup_scope()
        # sleep(5)
        self.run_rt()

        with open(f"test.png", "wb") as f:
            f.write(self.scope.get_screen_png())
