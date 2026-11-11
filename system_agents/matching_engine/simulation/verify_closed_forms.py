"""Kiểm chứng công thức đóng (hệ số cân bằng, hiệu quả tiệm cận) bằng mô phỏng lớn.

Chạy: python verify_closed_forms.py (mất khoảng 20-30 giây).
Dự đoán đối chiếu (suy ra độc lập bởi nhiều bên, xem docs/MATCHING_ENGINE_SPEC.md mục 9.6):
  - hệ số: bid = k(1-k)/(2(1+k)) + v/(1+k), ask = (1-k)/2 + c/(2-k);
  - hiệu quả tiệm cận k = 0.5: 1 - lam^2 / (4 (3 - lam)^2); với lam = 1: 1 - (1 - k + k^2)^2 / 9.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from generator import generate_valued  # noqa: E402
from metrics import max_welfare, run_auction, welfare  # noqa: E402
from strategies import ASK, BID, cs_linear_coeffs, linear_price_fn  # noqa: E402


def check_coefficients() -> bool:
    all_ok = True
    for k in (0.1, 0.25, 0.5, 0.75, 0.9):
        co = cs_linear_coeffs(k)
        got = (*co[BID], *co[ASK])
        want = (k * (1 - k) / (2 * (1 + k)), 1 / (1 + k), (1 - k) / 2, 1 / (2 - k))
        ok = all(abs(x - y) < 1e-12 for x, y in zip(got, want))
        all_ok &= ok
        print(f"k={k}: hệ số khớp công thức đóng: {ok}")
    return all_ok


def mean_efficiency(k: float, lam: float, n: int, seeds: range) -> float:
    vals = []
    for s in seeds:
        d = generate_valued(n, s)
        m = run_auction(d, k, linear_price_fn(cs_linear_coeffs(k), lam))
        vals.append(welfare(m, d) / max_welfare(d))
    return sum(vals) / len(vals)


def main() -> int:
    ok = check_coefficients()
    print("\nlam   dự đoán(k=0.5)   sim n=500 (20 seed)   sim n=4000 (6 seed)")
    for lam in (0.25, 0.5, 0.75, 1.0):
        pred = 1 - lam**2 / (4 * (3 - lam) ** 2)
        e500 = mean_efficiency(0.5, lam, 500, range(20))
        e4000 = mean_efficiency(0.5, lam, 4000, range(6))
        print(f"{lam:4}  {pred:.4f}           {e500:.4f}                {e4000:.4f}")
        ok &= abs(e4000 - pred) < 0.005
    print("\nk     dự đoán(lam=1)   sim n=4000 (6 seed)")
    for k in (0.25, 0.5, 0.75):
        pred = 1 - (1 - k + k * k) ** 2 / 9
        e = mean_efficiency(k, 1.0, 4000, range(6))
        print(f"{k:4}  {pred:.4f}           {e:.4f}")
        ok &= abs(e - pred) < 0.005
    print("\nKẾT QUẢ:", "KHỚP" if ok else "LỆCH")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
