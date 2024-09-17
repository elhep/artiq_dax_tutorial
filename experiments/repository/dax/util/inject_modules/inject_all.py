from artiq.experiment import *

import repository.dax.util.inject_modules.inject_cw_laser as inject_cw_laser
import repository.dax.util.inject_modules.inject_ablation as inject_ablation
import repository.dax.util.inject_modules.inject_microwave as inject_microwave


class InjectModules(inject_cw_laser.InjectCWLaser, inject_ablation.InjectAblation,
                    inject_microwave.InjectMicrowave):
    """0-Inject Modules"""

    def build(self):
        # Get Devices
        super(InjectModules, self).build()

    def prepare(self):
        super(InjectModules, self).prepare()
        pass

    @host_only
    def run(self):
        self.dax_init()
        self.run_kernel()

        self.inject_ablation()

    @kernel
    def run_kernel(self):
        # Reset the core
        self.core.reset()

        # Pre-delay
        delay(self.pre_delay)

        self.inject_cw_laser()
        # self.inject_flip_mirror()
        self.inject_microwave()

        # Post-wait time
        delay(self.post_delay)
        self.core.wait_until_mu(now_mu())
