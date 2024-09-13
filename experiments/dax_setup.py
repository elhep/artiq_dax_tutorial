from demo_system.system import *

class DaxSetup(DemoSystem, Experiment):
    """DaxSetup"""

    def __init__(self, managers, *args, **kwargs):
        # Capture the managers before passing them to super
        self._managers = managers
        super(DaxSetup, self).__init__(managers, *args, **kwargs)

    def build(self):
        # Call super
        super(DaxSetup, self).build()

    def run(self):
        # Set Mon PMT Enabled Key
        self.set_dataset_sys(self.MON_PMT_ENABLED_KEY, True)

        # Initialize Dax
        self.dax_init()

if __name__ == '__main__':
    from artiq.frontend.artiq_run import run

    run()