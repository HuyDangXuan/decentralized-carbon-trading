"""Kiểm thử độc lập hệ số cân bằng và bất biến của thí nghiệm B (bổ sung sau review chéo).

Không dựa vào cách cài đặt của strategies.py: phản ứng tối ưu được tìm bằng vét cạn trên lưới,
mỏ neo lý thuyết được tính bằng tích phân số.
"""

import os
import random
import sys
import unittest

_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
if _SIM_DIR not in sys.path:
    sys.path.insert(0, _SIM_DIR)

from generator import generate_valued  # noqa: E402
from metrics import (  # noqa: E402
    buyer_surplus, fill_rate, max_welfare, run_auction, welfare,
)
from model import OrderType, Valued, snap  # noqa: E402
from strategies import ASK, BID, CS_K05, HIGH, LOW, cs_linear_coeffs, linear_price_fn  # noqa: E402

GRID = 2000


def _expected_buyer_payoff(v, b, k, ask):
    """Kỳ vọng thặng dư người mua khi bid b, ask đối tác = g + d*c, c ~ U[0,1]."""
    g, d = ask
    tot = 0.0
    for i in range(GRID):
        c = (i + 0.5) / GRID
        s = g + d * c
        if b >= s:
            tot += v - (k * b + (1 - k) * s)
    return tot / GRID


def _expected_seller_payoff(c, s, k, bid):
    a, b_ = bid
    tot = 0.0
    for i in range(GRID):
        v = (i + 0.5) / GRID
        b = a + b_ * v
        if b >= s:
            tot += (k * b + (1 - k) * s) - c
    return tot / GRID


class TestClosedFormEquilibrium(unittest.TestCase):
    def test_k_half_matches_reference(self):
        got = cs_linear_coeffs(0.5)
        for side in (BID, ASK):
            for x, y in zip(got[side], CS_K05[side]):
                self.assertAlmostEqual(x, y, places=12)

    def test_exact_values_derived_independently(self):
        """Giá trị chính xác do hai người suy ra độc lập (Claude và reviewer Opus 5.5) từ điều kiện bậc nhất.

        Vét cạn trên lưới chỉ phát hiện sai lệch cỡ 0.01, nên các giá trị này khóa chặt hơn.
        """
        expect = {
            0.25: {BID: (0.075, 0.8), ASK: (0.375, 4 / 7)},
            0.75: {BID: (3 / 56, 4 / 7), ASK: (0.125, 0.8)},
        }
        for k, sides in expect.items():
            got = cs_linear_coeffs(k)
            for side, vals in sides.items():
                for x, y in zip(got[side], vals):
                    self.assertAlmostEqual(x, y, places=9, msg=f"k={k} {side}")

    def test_invalid_k_rejected(self):
        for bad in (0.0, 1.0, -0.1, 1.5, float("nan")):
            with self.assertRaises(ValueError, msg=str(bad)):
                cs_linear_coeffs(bad)

    def test_closed_form_is_a_best_response_fixed_point(self):
        """Với đối tác dùng chiến lược tuyến tính cho trước, bid/ask tối ưu vét cạn ≈ công thức."""
        for k in (0.25, 0.5, 0.75):
            co = cs_linear_coeffs(k)
            (a, b), (g, d) = co[BID], co[ASK]
            for v in (0.5, 0.7, 0.95):
                grid = [i / 400 for i in range(401)]
                best = max(grid, key=lambda x: _expected_buyer_payoff(v, x, k, (g, d)))
                self.assertAlmostEqual(best, a + b * v, delta=0.01, msg=f"buyer k={k} v={v}")
            for c in (0.05, 0.25, 0.5):
                grid = [i / 400 for i in range(401)]
                best = max(grid, key=lambda x: _expected_seller_payoff(c, x, k, (a, b)))
                self.assertAlmostEqual(best, g + d * c, delta=0.01, msg=f"seller k={k} c={c}")


def _theory_1v1(k):
    """Tần suất giao dịch và efficiency lý thuyết (tích phân số, có chặn bid<=v, ask>=c)."""
    co = cs_linear_coeffs(k)
    (a, b), (g, d) = co[BID], co[ASK]
    n = 800
    trade = w = wmax = 0.0
    for i in range(n):
        v = (i + 0.5) / n
        bid = min(v, a + b * v)
        for j in range(n):
            c = (j + 0.5) / n
            ask = max(c, g + d * c)
            if bid >= ask:
                trade += 1
                w += v - c
            if v > c:
                wmax += v - c
    return trade / (n * n), w / wmax


class TestOneVsOneAnchors(unittest.TestCase):
    def test_trade_frequency_and_efficiency_match_theory_for_each_k(self):
        for k in (0.25, 0.5, 0.75):
            rng = random.Random(1234)
            fn = linear_price_fn(cs_linear_coeffs(k), 1.0)
            trials, hits, wsum, wmaxsum = 20000, 0, 0.0, 0.0
            for i in range(trials):
                pair = [
                    Valued("B", OrderType.BID, 1, snap(rng.uniform(LOW, HIGH)), 0),
                    Valued("S", OrderType.ASK, 1, snap(rng.uniform(LOW, HIGH)), 1),
                ]
                m = run_auction(pair, k, fn)
                hits += bool(m)
                wsum += welfare(m, pair)
                wmaxsum += max_welfare(pair)
            freq, eff = _theory_1v1(k)
            self.assertAlmostEqual(hits / trials, freq, delta=0.015, msg=f"freq k={k}")
            self.assertAlmostEqual(wsum / wmaxsum, eff, delta=0.02, msg=f"eff k={k}")


class TestB2Invariants(unittest.TestCase):
    def test_truthful_split_is_one_minus_k(self):
        for k in (0.25, 0.5, 0.75):
            for seed in range(3):
                d = generate_valued(100, seed)
                m = run_auction(d, k, linear_price_fn(cs_linear_coeffs(k), 0.0))
                self.assertAlmostEqual(buyer_surplus(m, d) / welfare(m, d), 1 - k, delta=2e-3)

    def test_efficiency_and_fill_rate_bounded_and_monotone_in_lambda(self):
        for k in (0.25, 0.5, 0.75):
            means = []
            for lam in (0.0, 0.25, 0.5, 0.75, 1.0):
                effs = []
                for seed in range(5):
                    d = generate_valued(100, seed)
                    m = run_auction(d, k, linear_price_fn(cs_linear_coeffs(k), lam))
                    e = welfare(m, d) / max_welfare(d)
                    self.assertLessEqual(e, 1.0 + 1e-9)
                    self.assertLessEqual(fill_rate(m, d), 1.0 + 1e-9)
                    effs.append(e)
                means.append(sum(effs) / len(effs))
            self.assertTrue(all(x >= y - 1e-9 for x, y in zip(means, means[1:])), f"k={k}: {means}")

    def test_welfare_is_computed_from_true_valuations_not_quotes(self):
        pair = [Valued("B", OrderType.BID, 1, 12.0, 0), Valued("S", OrderType.ASK, 1, 6.0, 1)]
        m = run_auction(pair, 0.5, linear_price_fn(CS_K05, 1.0))
        self.assertEqual(len(m), 1)
        self.assertAlmostEqual(welfare(m, pair), 6.0, places=6)  # 12 - 6, không phải chênh lệch giá khai


if __name__ == "__main__":
    unittest.main()
