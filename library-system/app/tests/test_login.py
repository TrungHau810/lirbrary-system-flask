import unittest
from app import dao


class TestLogin(unittest.TestCase):

    def test_case_1(self):
        self.assertFalse(dao.auth_user(username="user", password="123"))


if __name__ == '__main__':
    unittest.main()
