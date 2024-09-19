from artiq.experiment import *
import numpy as np


class PhaserDemoExcercise(EnvExperiment):
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

        self.center_f = 97 * MHz

        freq_slopes = [
            list(np.linspace(2.8 * MHz, 1 * MHz, 100)),
            list(np.linspace(2.9 * MHz, 2 * MHz, 100)),
            [3 * MHz] * 100,
            list(np.linspace(3.1 * MHz, 4 * MHz, 100)),
            list(np.linspace(3.2 * MHz, 5 * MHz, 100)),
        ]

        self.ftw = [
            freq_slopes[osc] + list(reversed(freq_slopes[osc]))
            for osc in range(5)
        ]
        self.length = len(self.ftw[0])
        
        # self.ftw = [1 * MHz, 2 * MHz, 3 * MHz, 4 * MHz, 5 * MHz]
        # self.ftw = [2.8 * MHz, 2.9 * MHz, 3 * MHz, 3.1 * MHz, 3.2 * MHz]
        self.asf = [0.375, 0.10, 0.05, 0.10, 0.375]



        assert sum(self.asf) <= 1.0

    @kernel
    def init(self):
        self.core.reset()
        self.core.break_realtime()

        self.phaser0.init()
        
        self.ttl0.off()

    @kernel
    def run(self):
        self.init()

        phaser = self.phaser0
        
        phaser.channel[0].set_att(0 * dB)
        phaser.channel[0].set_duc_frequency(self.center_f)
        phaser.channel[0].set_duc_phase(0.25)
        phaser.channel[0].set_duc_cfg()

        delay(0.1 * ms)
        phaser.duc_stb()
        delay(0.1 * ms)
        
        while True:
            for i in range(self.length):
                for osc in range(5):
                    phaser.channel[0].oscillator[osc].set_frequency(self.ftw[osc][i])
                    phaser.channel[0].oscillator[osc].set_amplitude_phase(
                        self.asf[osc], phase=0.25)
                    delay(10 * ms)
        # for osc in range(5):
        #     phaser.channel[0].oscillator[osc].set_frequency(self.ftw[osc])
        #     phaser.channel[0].oscillator[osc].set_amplitude_phase(
        #         self.asf[osc], phase=0.25)
        #     delay(0.1 * ms)

        
