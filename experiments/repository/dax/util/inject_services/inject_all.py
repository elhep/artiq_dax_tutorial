from artiq.experiment import *

import repository.dax.util.inject_services.inject_cooling as inject_cooling


class InjectServices(inject_cooling.InjectCooling):
    """0-Inject Services"""

    def build(self):
        # Get Devices
        super(InjectServices, self).build()

    def prepare(self):
        super(InjectServices, self).prepare()
        pass

    @kernel
    def run(self):
        # Reset the core
        self.core.reset()

        # Pre-delay
        delay(self.pre_delay)

        self.inject_cooling()

        # Post-wait time
        delay(self.post_delay)
        self.core.wait_until_mu(now_mu())
