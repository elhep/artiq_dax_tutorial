from dax.experiment import *


class ScopeModule(DaxModule):
    """
    Module to control textronix scope used in the demo
    """


    def build(self) -> None:
        # Get the controller
        self.in_sim = '_dax_sim_config' in self.get_device_db()

        if not self.in_sim:
            self._scope = self.get_device("scope")
            self.update_kernel_invariants("_scope")

    @host_only
    def init(self) -> None:
        """Initialize the scope"""
        self.reset()
        self.configure_channels()
        self.set_h_scale()
        self.set_trigger()
        pass

    @host_only
    def post_init(self) -> None:
        pass

    """Module functionality"""

    @host_only
    def reset(self) -> None:
        """Reset the scope"""
        if not self.in_sim:
            self._scope.reset()
            self._scope.set_current_datetime()

    @host_only
    def configure_channels(self) -> None:
        if not self.in_sim:
            self._scope.set_channel(
                channel=1,
                vertical_scale=2.5,
                vertical_position=3,
                termination_fifty_ohms=False,
                label="DIO SMA 0",
                ac_coupling=False
            )

            self._scope.set_channel(
                channel=2,
                vertical_scale=1,
                vertical_position=1.0,
                termination_fifty_ohms=True,
                label="Urukul 0",
                ac_coupling=True
            )

            self._scope.set_channel(
                channel=3,
                vertical_scale=1,
                vertical_position=-1.0,
                termination_fifty_ohms=True,
                label="Urukul 1",
                ac_coupling=True
            )

            self._scope.set_channel(
                channel=4,
                vertical_scale=0.5,
                vertical_position=-3.0,
                termination_fifty_ohms=True,
                label="Phaser RF 0",
                ac_coupling=True
            )

    @host_only
    def set_h_scale(self) -> None:
        # Waveform time will be 10*horizontal scale
        if not self.in_sim:
            self._scope.set_horizontal_scale(100 * ns)
            self._scope.set_horizontal_position(400 * ns)

    @host_only
    def set_trigger(self) -> None:
        if not self.in_sim:
            # Slope: RISE/FALL
            # Mode: NORMAL/AUTO
            self._scope.set_trigger(
                channel=1,
                level=2.5,
                slope="RISE",
                mode="NORMAL"
            )

    @host_only
    def start(self) -> None:
        if not self.in_sim:
            self._scope.start_acquisition()
            sleep(3)

    @host_only
    def get_image(self, filename = "scope.png") -> None:
        if not self.in_sim:
            with open(filename, "wb") as f:
                f.write(self._scope.get_screen_png())
