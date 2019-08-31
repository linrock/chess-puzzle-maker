import unittest
from collections import namedtuple

from chess.engine import Cp, Mate

from puzzlemaker.analysis import ambiguous_best_move


class TestAmbiguous(unittest.TestCase):

    def test_not_ambiguous_equality_vs_slight_disadvantage(self):
        self.assertFalse(ambiguous_best_move([
            Cp(3),
            Cp(-131),
            Cp(-200),
        ]))
        self.assertFalse(ambiguous_best_move([
            Cp(3),
            Cp(-170),
            Cp(-371),
        ]))
        self.assertFalse(ambiguous_best_move([
            Cp(0),
            Cp(-282),
            Cp(-293),
        ]))

    def test_not_ambiguous_equality_vs_significant_disadvantage(self):
        self.assertFalse(ambiguous_best_move([
            Cp(0),
            Cp(-825),
            Cp(-1079),
        ]))
        self.assertFalse(ambiguous_best_move([
            Cp(-36),
            Cp(-485),
            Cp(-504),
        ]))
        self.assertFalse(ambiguous_best_move([
            Cp(0),
            Cp(-963),
            Mate(-12),
        ]))

    def test_not_ambiguous_slight_advantage_vs_equality(self):
        self.assertFalse(ambiguous_best_move([
            Cp(-132),
            Cp(-4),
            Cp(45),
        ]))

    def test_not_ambiguous_slight_advantage_vs_slight_disadvantage(self):
        self.assertFalse(ambiguous_best_move([
            Cp(139),
            Cp(-153),
            Cp(-328),
        ]))
        self.assertFalse(ambiguous_best_move([
            Cp(203),
            Cp(-72),
            Cp(-97),
        ]))
        self.assertFalse(ambiguous_best_move([
            Cp(-114),
            Cp(85),
            Cp(89),
        ]))
        self.assertFalse(ambiguous_best_move([
            Cp(-101),
            Cp(103),
            Cp(282),
        ]))
        self.assertFalse(ambiguous_best_move([
            Cp(53),
            Cp(-75),
            Cp(-122),
        ]))

    def test_not_ambiguous_slight_advantage_vs_significant_disadvantage(self):
        self.assertFalse(ambiguous_best_move([
            Cp(146),
            Cp(-405),
        ]))
        self.assertFalse(ambiguous_best_move([
            Cp(149),
            Cp(-458),
            Cp(-543),
        ]))

    def test_not_ambiguous_significant_advantage_vs_slight_advantage(self):
        self.assertFalse(ambiguous_best_move([
            Cp(379),
            Cp(78),
            Cp(77),
        ]))
        self.assertFalse(ambiguous_best_move([
            Cp(365),
            Cp(110),
            Cp(95),
        ]))
        self.assertFalse(ambiguous_best_move([
            Cp(-683),
            Cp(-81),
            Cp(-65),
        ]))

    def test_not_ambiguous_mate_vs_counter_mate(self):
        self.assertFalse(ambiguous_best_move([
            Mate(1),
            Mate(-14),
            Mate(-11),
        ]))
        self.assertFalse(ambiguous_best_move([
            Mate(-2),
            Mate(10),
            Mate(8),
        ]))

    def test_not_ambiguous_mate_vs_moderate_advantage(self):
        self.assertFalse(ambiguous_best_move([
            Mate(1),
            Cp(304),
            Cp(206),
        ]))
        
    def test_ambiguous_slight_advantages(self):
        self.assertTrue(ambiguous_best_move([
            Cp(-74),
            Cp(-116),
            Cp(-154),
        ]))
        self.assertTrue(ambiguous_best_move([
            Cp(-78),
            Cp(-154),
            Cp(-192),
        ]))
        self.assertTrue(ambiguous_best_move([
            Cp(262),
            Cp(191),
            Cp(186),
        ]))
        self.assertTrue(ambiguous_best_move([
            Cp(166),
            Cp(152),
            Cp(146),
        ]))
        self.assertTrue(ambiguous_best_move([
            Cp(72),
            Cp(25),
            Cp(8),
        ]))
        
    def test_ambiguous_significant_advantages(self):
        self.assertTrue(ambiguous_best_move([
            Cp(767),
            Cp(758),
            Cp(177),
        ]))
        self.assertTrue(ambiguous_best_move([
            Cp(552),
            Cp(505),
            Cp(443),
        ]))
        self.assertTrue(ambiguous_best_move([
            Cp(408),
            Cp(224),
            Cp(219),
        ]))
        self.assertTrue(ambiguous_best_move([
            Cp(254),
            Cp(254),
            Cp(240),
        ]))

    def test_ambiguous_mate_vs_significant_advantage(self):
        self.assertTrue(ambiguous_best_move([
            Mate(1),
            Cp(700),
        ]))

    def test_ambiguous_multiple_mates(self):
        self.assertTrue(ambiguous_best_move([
            Mate(1),
            Mate(1),
        ]))


if __name__ == '__main__':
    unittest.main()
