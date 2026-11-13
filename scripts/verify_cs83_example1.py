"""Kiểm công thức Ví dụ 1 của Chatterjee–Samuelson (1983), tr. 842, bằng Monte Carlo (v̄ = 1)."""
import numpy as np
rng = np.random.default_rng(1)
N = 4_000_000
v = rng.random(N); c = rng.random(N)
print("k  P(trade) MC | paper (-k^2+k+2)/8 | total profit MC | paper (1+k)(2-k)/16 | eff MC vs 1/6")
for k in (0.25, 0.5, 0.75, 1.0):
    # chien luoc tuyen tinh o dung mien (CS83 p.842, Vi du 1a), v_bar = 1
    bid = np.where(v >= (1 - k) / 2, v / (1 + k) + k * (1 - k) / (2 * (1 + k)), 0.0)
    ask = np.where(c <= (2 - k) / 2, c / (2 - k) + (1 - k) / 2, 2.0)
    t = bid >= ask
    price = k * bid + (1 - k) * ask
    gain = np.where(t, v - c, 0.0)
    pb = np.where(t, v - price, 0.0).mean(); ps = np.where(t, price - c, 0.0).mean()
    print(f"{k:.2f} {t.mean():.4f}     | {(-k*k+k+2)/8:.4f}            | {gain.mean():.4f}          | {(1+k)*(2-k)/16:.4f}             | {gain.mean()/(1/6):.4f}"
          f"  (pi_b={pb:.4f} vs {(1+k)**2*(2-k)/48:.4f}, pi_s={ps:.4f} vs {(2-k)**2*(1+k)/48:.4f})")
