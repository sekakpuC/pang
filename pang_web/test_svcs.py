from random import randint
from unittest import TestCase

from pang_web_main import svcs


class Test(TestCase):
    def test_get_top_ten(self):
        row_count = svcs.add_score_to_db("tom",randint(1000,9999))
        self.assertEqual(1,row_count)