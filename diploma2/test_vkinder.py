import unittest
from vkinder import USER


class TestVK(unittest.TestCase):
    def setUp(self):
        self.USER = USER()

    def tearDown(self):
        return None

    # @classmethod
    # def setUpClass(cls):
    #     print("setUpClass")
    #     print("==========")

    # @classmethod
    # def tearDownClass(cls):
    #     print(" tearDownClass")
    #     print("==========")

    # def setUp(self):
    #     print(self.shortDescription())

    # def tearDown(self):
    #     print(self.shortDescription())

    def test_raise(self):
        self.assertRaises(TypeError, self.USER.main)

    # def right_response(self):
    #     self.assertIs(self.USER)



if __name__ == '__main__':

    unittest.main()