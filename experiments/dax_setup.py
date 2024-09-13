from demo_system.system import *
from dax.util.sub_experiment import SubExperiment

from repository.dax.util.dax.dax_init import DaxInit
from repository.dax.util.dataset_config.system_config import SystemConfig


class DaxSetup(DemoSystem, Experiment):
    """Dax Setup"""

    def __init__(self, managers, *args, **kwargs):
        # Capture the managers before passing them to super
        self._managers = managers
        super(DaxSetup, self).__init__(managers, *args, **kwargs)

    def build(self) -> None:
        try:
            # Build system
            super(DaxSetup, self).build()
        except KeyError:
            # Could not find key and system config might not be available, fallback on defaults
            self.logger.error('No current configuration exists yet, run this utility once to set a configuration')

    def run(self):
        sub_experiment = SubExperiment(self, self._managers)
        sub_experiment.run(SystemConfig, "config")
        sub_experiment.run(DaxInit, "init")
