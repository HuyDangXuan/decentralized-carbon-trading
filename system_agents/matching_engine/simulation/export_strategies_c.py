"""Xuất chiến lược cân bằng một đơn vị (Thực nghiệm C) ra file .npz để dùng cho kiểm tra nhiều đơn vị.

`run_experiment_c.py` chỉ lưu giá khai tại 3 điểm (0.25, 0.50, 0.75); chiến lược thật là hàm
tuyến tính từng đoạn trên lưới nút `v_knots`, nên 3 điểm không đủ để dựng lại. Script này chạy lại
đúng `find_equilibrium` với cùng hạt giống và tham số như `run_experiment_c.py` (tất định), rồi lưu
nút chiến lược. Với mỗi cấu hình nó cũng tính lại loss một đơn vị trên cùng kịch bản kiểm định và in ra,
để đối chiếu với `exp_c_raw.csv` (nếu lệch nghĩa là không tái tạo được chiến lược cũ).

Ví dụ: python export_strategies_c.py --m 16,32 --k 1 --rule pair,marginal --out strategies
"""

import argparse
import os
import sys
import time
from pathlib import Path

_SIM_DIR = os.path.dirname(os.path.abspath(__file__))
_ENGINE_DIR = os.path.dirname(_SIM_DIR)
for d in (_SIM_DIR, _ENGINE_DIR):
    if d not in sys.path:
        sys.path.insert(0, d)

import numpy as np  # noqa: E402

from equilibrium_search import find_equilibrium  # noqa: E402
from kda_sim import draw_scenarios, max_welfare, welfare  # noqa: E402
from run_experiment_c import compute_loss_and_ci, get_seeds  # noqa: E402


def strategy_path(out_dir: Path, k: float, m: int, rule: str) -> Path:
    return Path(out_dir) / f"strategy_k{k:g}_m{m}_{rule}.npz"


def export_one(m: int, k: float, rule: str, scen: int, iters: int, eval_scen: int, out_dir: Path) -> dict:
    train_seed, _val_seed, eval_seed = get_seeds(m, k, rule)
    eq = find_equilibrium(m=m, k=k, rule=rule, seed=train_seed, n_scen=scen, max_iter=iters, mode="nonparametric")
    strategy = eq["strategy"]
    v_knots = np.asarray(eq["v_knots"], dtype=float)
    V, C = draw_scenarios(m=m, n_scen=eval_scen, seed=eval_seed)
    _eff, loss, ci = compute_loss_and_ci(welfare(V, C, strategy, k=k, rule=rule), max_welfare(V, C), num_blocks=10)
    path = strategy_path(out_dir, k, m, rule)
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        v_knots=v_knots,
        bid_knots=np.asarray(strategy[0], dtype=float),
        ask_knots=np.asarray(strategy[1], dtype=float),
        k=k, m=m, rule=rule, scen=scen, iters=iters, converged=bool(eq["converged"]),
    )
    return {"loss": float(loss), "ci": float(ci), "converged": bool(eq["converged"]), "path": str(path)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--m", required=True, help="danh sách m, ví dụ 16,32,64")
    p.add_argument("--k", type=float, required=True)
    p.add_argument("--rule", required=True, help="pair,marginal,kda")
    p.add_argument("--scen", type=int, default=40000)
    p.add_argument("--iters", type=int, default=40)
    p.add_argument("--eval-scen", type=int, default=400000)
    p.add_argument("--out", required=True)
    args = p.parse_args(argv)
    for m in [int(x) for x in args.m.split(",") if x.strip()]:
        for rule in [x.strip() for x in args.rule.split(",") if x.strip()]:
            if strategy_path(Path(args.out), args.k, m, rule).is_file():
                print(f"bỏ qua (đã có): m={m} k={args.k:g} {rule}", flush=True)
                continue
            t0 = time.time()
            r = export_one(m, args.k, rule, args.scen, args.iters, args.eval_scen, Path(args.out))
            print(
                f"m={m} k={args.k:g} {rule}: loss={r['loss']:.6e} ±{r['ci']:.1e} converged={r['converged']} "
                f"({time.time() - t0:.0f}s)",
                flush=True,
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
