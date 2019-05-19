import unittest
from collections import namedtuple

from chess.uci import Score

from modules.candidate_moves import ambiguous


class TestAmbiguous(unittest.TestCase):

    def test_not_ambiguous_equality_vs_slight_disadvantage(self):
        self.assertFalse(ambiguous([
            Score(3, None),
            Score(-131, None),
            Score(-200, None),
        ]))
        self.assertFalse(ambiguous([
            Score(3, None),
            Score(-170, None),
            Score(-371, None),
        ]))
        self.assertFalse(ambiguous([
            Score(0, None),
            Score(-282, None),
            Score(-293, None),
        ]))

    def test_not_ambiguous_equality_vs_significant_disadvantage(self):
        self.assertFalse(ambiguous([
            Score(0, None),
            Score(-825, None),
            Score(-1079, None),
        ]))
        self.assertFalse(ambiguous([
            Score(-36, None),
            Score(-485, None),
            Score(-504, None),
        ]))
        self.assertFalse(ambiguous([
            Score(0, None),
            Score(-963, None),
            Score(None, -12),
        ]))

    def test_not_ambiguous_slight_advantage_vs_equality(self):
        self.assertFalse(ambiguous([
            Score(-132, None),
            Score(-4, None),
            Score(45, None),
        ]))

    def test_not_ambiguous_slight_advantage_vs_slight_disadvantage(self):
        self.assertFalse(ambiguous([
            Score(139, None),
            Score(-153, None),
            Score(-328, None),
        ]))
        self.assertFalse(ambiguous([
            Score(203, None),
            Score(-72, None),
            Score(-97, None),
        ]))

    def test_not_ambiguous_slight_advantage_vs_significant_disadvantage(self):
        self.assertFalse(ambiguous([
            Score(146, None),
            Score(-405, None),
        ]))
        self.assertFalse(ambiguous([
            Score(149, None),
            Score(-458, None),
            Score(-543, None),
        ]))

    def test_not_ambiguous_significant_advantage_vs_slight_advantage(self):
        self.assertFalse(ambiguous([
            Score(379, None),
            Score(78, None),
            Score(77, None),
        ]))
        self.assertFalse(ambiguous([
            Score(365, None),
            Score(110, None),
            Score(95, None),
        ]))
        self.assertFalse(ambiguous([
            Score(-683, None),
            Score(-81, None),
            Score(-65, None),
        ]))

    def test_not_ambiguous_mate_vs_counter_mate(self):
        self.assertFalse(ambiguous([
            Score(None, 1),
            Score(None, -14),
            Score(None, -11),
        ]))
        self.assertFalse(ambiguous([
            Score(None, -2),
            Score(None, 10),
            Score(None, 8),
        ]))

    def test_not_ambiguous_mate_vs_moderate_advantage(self):
        self.assertFalse(ambiguous([
            Score(None, 1),
            Score(304, None),
            Score(206, None),
        ]))
        
    def test_ambiguous_slight_advantages(self):
        self.assertTrue(ambiguous([
            Score(-74, None),
            Score(-116, None),
            Score(-154, None),
        ]))
        self.assertTrue(ambiguous([
            Score(-78, None),
            Score(-154, None),
            Score(-192, None),
        ]))
        self.assertTrue(ambiguous([
            Score(262, None),
            Score(191, None),
            Score(186, None),
        ]))
        self.assertTrue(ambiguous([
            Score(166, None),
            Score(152, None),
            Score(146, None),
        ]))
        self.assertTrue(ambiguous([
            Score(72, None),
            Score(25, None),
            Score(8, None),
        ]))
        
    def test_ambiguous_significant_advantages(self):
        self.assertTrue(ambiguous([
            Score(767, None),
            Score(758, None),
            Score(177, None),
        ]))
        self.assertTrue(ambiguous([
            Score(552, None),
            Score(505, None),
            Score(443, None),
        ]))
        self.assertTrue(ambiguous([
            Score(408, None),
            Score(224, None),
            Score(219, None),
        ]))
        self.assertTrue(ambiguous([
            Score(254, None),
            Score(254, None),
            Score(240, None),
        ]))

    def test_ambiguous_mate_vs_significant_advantage(self):
        self.assertTrue(ambiguous([
            Score(None, 1),
            Score(700, None),
        ]))

    def test_ambiguous_multiple_mates(self):
        self.assertTrue(ambiguous([
            Score(None, 1),
            Score(None, 1),
        ]))

if __name__ == '__main__':
    unittest.main()
