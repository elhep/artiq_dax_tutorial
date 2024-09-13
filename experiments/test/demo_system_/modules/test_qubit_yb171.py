import random

import dax.sim.test_case

from test.system import DemoTestSystem


class Yb171TestCase(dax.sim.test_case.PeekTestCase):

    def setUp(self) -> None:
        self.sys = self.construct_env(DemoTestSystem, device_db="device_db_sim.py")
        self.sys.dax_init()

    def test_set_num_ions(self):
        self.assertEqual(self.sys.qubit_yb171.num_ions, 0)
        for _ in range(10):
            test_val = random.randrange(25)
            self.sys.qubit_yb171.set_num_ions(test_val)
            self.assertEqual(self.sys.qubit_yb171.num_ions, test_val)
