from demo_system.modules.util.switch import Switch
from demo_system.modules.util.state_controller import BinaryStateController

class TriggerTTLModule(Switch, BinaryStateController):

    def build(self):
        super(TriggerTTLModule, self).build(sw_key='ttl0')
        BinaryStateController.build(self, set_cb=self.set_cb, default_state=False)

    def set_cb(self, state: bool) -> None:
        self.set(state, realtime=True)
