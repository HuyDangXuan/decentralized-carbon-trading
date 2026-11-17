"""Kiểm chéo hai điểm của Argon bằng mô hình nhỏ và bằng engine thật."""
import pathlib
import sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "system_agents" / "matching_engine"))
from session_engine import BookOrder, _allocate_side

# --- 1. L3, L4 bằng engine thật (nhóm cùng tuổi, cùng mức giá biên) ---
def alloc(vols, V, seqs=None):
    orders = [BookOrder(f"o{i}", "BID", 10, v, sessions_alive=0, seq=(seqs[i] if seqs else i)) for i, v in enumerate(vols)]
    r = _allocate_side(orders, "BID", V, "age_prorata")
    return [r[f"o{i}"] for i in range(len(vols))]

print("L3 A=2,B=1,C=1 V=2      ->", alloc([2, 1, 1], 2), "(A,B,C)")
print("L3 A1=1,A2=1,B=1,C=1 V=2 ->", alloc([1, 1, 1, 1], 2), "(A1,A2,B,C)")
print("L4 (1,3,3) V=3 ->", alloc([1, 3, 3], 3), "| V=4 ->", alloc([1, 3, 3], 4))

# --- 2. Replay sau thành công: tradeHash hiện tại, S1 (filledAmount đọc từ storage), phương án B (expectedFilled trong calldata) ---
def run(scheme, calls):
    filled = {"bid": 0, "ask": 0}
    executed = set()
    out = []
    amount = 100
    for (m, p, exp_bid, exp_ask) in calls:
        if scheme == "current":
            h = ("bid", "ask", m, p)
        elif scheme == "S1":
            h = ("bid", "ask", m, p, filled["bid"], filled["ask"])
        else:  # B: calldata mang expectedFilled và hợp đồng đối chiếu với storage
            if (exp_bid, exp_ask) != (filled["bid"], filled["ask"]):
                out.append("REVERT(fill mismatch)"); continue
            h = ("bid", "ask", m, p, exp_bid, exp_ask)
        if h in executed:
            out.append("REVERT(TradeAlreadyExecuted)"); continue
        if filled["bid"] + m > amount or filled["ask"] + m > amount:
            out.append("REVERT(amount exceeded)"); continue
        executed.add(h); filled["bid"] += m; filled["ask"] += m
        out.append(f"OK(filled={filled['bid']})")
    return out

# (a) gửi trùng đúng calldata (retry của Operator) sau khi lần đầu thành công
retry = [(30, 10, 0, 0), (30, 10, 0, 0)]
# (b) hai lần khớp hợp lệ khác phiên, cùng amount và giá (partial fill hợp lệ)
two_sessions = [(30, 10, 0, 0), (30, 10, 30, 30)]
for name, calls in (("retry cùng calldata", retry), ("hai phiên hợp lệ cùng amount/giá", two_sessions)):
    print(f"\n{name}")
    for sch in ("current", "S1", "B"):
        print(f"  {sch:8s}", run(sch, calls))
