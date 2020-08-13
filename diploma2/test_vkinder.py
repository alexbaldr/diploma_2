import unittest
from vkinder import USER
import json


class TestVK(unittest.TestCase):

    def setUp(self):
        self.USER = USER()
        print(self.shortDescription())

    def tearDown(self):
        print(self.shortDescription())

    def test_raise(self):
        "Check error"
        users = {"тут может быть записанна любая хрень"}   
        self.assertRaises(TypeError, self.USER.main() is not users)

    def test_isEmpty_list(self):
        "Checking the list is not empty and contane min 10 parts"
        self.assertTrue(len(self.USER.get_10th_users_list()))
        self.assertGreaterEqual(len(self.USER.get_10th_users_list()), 10)

    def test_file_is_full(self):
        "Json is not empty"  
        with open('vkinder_users.json') as fo:
            data = json.load(fo)
        self.assertIsNotNone(data)
   
    # def test_authorization(self):

if __name__ == '__main__':

    unittest.main()