"""Engine khớp lệnh phiên đấu giá kép (Periodic Double Auction).

Cài đặt thuần số nguyên, không I/O, không sửa đầu vào, kết quả không phụ thuộc
thứ tự đầu vào.
"""

from dataclasses import dataclass
from typing import List, Optional, Tuple


@dataclass(frozen=True)
class BookOrder:
    order_id: str
    side: str  # "BID" | "ASK"
    price_ticks: int  # > 0
    remaining: int  # > 0
    sessions_alive: int = 0
    seq: int = 0  # thứ tự đến, chỉ cho fifo
    tif: str = "GTC"  # "GTC" | "IOC"


@dataclass(frozen=True)
class Fill:
    bid_id: str
    ask_id: str
    amount: int
    price_ticks: int


def _round_price(n: int, k_den: int, rounding: str) -> int:
    """Làm tròn thương n / k_den về số nguyên thuần túy (không dùng float)."""
    q, r = divmod(n, k_den)
    if rounding == "floor":
        return q
    if rounding == "ceil":
        return q + (1 if r > 0 else 0)
    if rounding == "half_up":
        return q + (1 if 2 * r >= k_den else 0)
    if rounding == "half_even":
        return q + (1 if (2 * r > k_den or (2 * r == k_den and q % 2 != 0)) else 0)
    raise ValueError(f"Invalid rounding: {rounding}")


def _allocate_side(
    side_orders: list[BookOrder],
    side: str,
    V: int,
    tie_break: str,
) -> dict[str, int]:
    """Phân bổ khối lượng V cho một phía (BID hoặc ASK)."""
    alloc: dict[str, int] = {o.order_id: 0 for o in side_orders}
    if V == 0:
        return alloc

    # Các mức giá xếp theo độ ưu tiên tốt hơn: BID giảm dần, ASK tăng dần
    unique_prices = sorted(
        {o.price_ticks for o in side_orders},
        reverse=(side == "BID"),
    )

    cum_vol = 0
    marginal_price: Optional[int] = None
    avail_at_marginal = 0

    for p in unique_prices:
        vol_at_p = sum(o.remaining for o in side_orders if o.price_ticks == p)
        if cum_vol + vol_at_p < V:
            cum_vol += vol_at_p
            for o in side_orders:
                if o.price_ticks == p:
                    alloc[o.order_id] = o.remaining
        else:
            marginal_price = p
            avail_at_marginal = V - cum_vol
            break

    if marginal_price is None or avail_at_marginal <= 0:
        return alloc

    marginal_orders = [o for o in side_orders if o.price_ticks == marginal_price]
    vol_marginal = sum(o.remaining for o in marginal_orders)

    if avail_at_marginal == vol_marginal:
        for o in marginal_orders:
            alloc[o.order_id] = o.remaining
    else:
        if tie_break == "fifo":
            sorted_marginal = sorted(marginal_orders, key=lambda o: (o.seq, o.order_id))
            rem_avail = avail_at_marginal
            for o in sorted_marginal:
                take = min(o.remaining, rem_avail)
                alloc[o.order_id] = take
                rem_avail -= take
                if rem_avail == 0:
                    break
        elif tie_break == "age_prorata":
            ages = sorted({o.sessions_alive for o in marginal_orders}, reverse=True)
            rem_avail = avail_at_marginal
            for age in ages:
                subgroup = [o for o in marginal_orders if o.sessions_alive == age]
                sub_total = sum(o.remaining for o in subgroup)
                if rem_avail >= sub_total:
                    for o in subgroup:
                        alloc[o.order_id] = o.remaining
                    rem_avail -= sub_total
                    if rem_avail == 0:
                        break
                else:
                    # Nhóm con cuối bị thiếu -> Hamilton largest remainder
                    S = sub_total
                    base_allocs = {}
                    rems = {}
                    for o in subgroup:
                        r_i = o.remaining
                        q_i = (rem_avail * r_i) // S
                        rem_i = (rem_avail * r_i) % S
                        base_allocs[o.order_id] = q_i
                        rems[o.order_id] = rem_i

                    sum_base = sum(base_allocs.values())
                    R = rem_avail - sum_base

                    # Phá hòa: (-rem_i, -remaining, order_id)
                    sorted_sub = sorted(
                        subgroup,
                        key=lambda o: (-rems[o.order_id], -o.remaining, o.order_id),
                    )

                    for rank, o in enumerate(sorted_sub):
                        add_one = 1 if rank < R else 0
                        alloc[o.order_id] = base_allocs[o.order_id] + add_one

                    rem_avail = 0
                    break

    return alloc


def match_session(
    orders: list[BookOrder],
    k_num: int = 1,
    k_den: int = 2,
    tie_break: str = "age_prorata",
    pricing: str = "pair",
    rounding: str = "floor",
) -> list[Fill]:
    """Khớp lệnh định kỳ cho một phiên đấu giá kép (chỉ thư viện chuẩn, thuần số nguyên)."""
    # 1. Kiểm tra tính hợp lệ của tham số
    if k_den <= 0:
        raise ValueError(f"k_den must be positive, got {k_den}")
    if k_num < 0 or k_num > k_den:
        raise ValueError(f"k_num must be in [0, k_den], got {k_num}")
    if tie_break not in ("age_prorata", "fifo"):
        raise ValueError(f"Invalid tie_break: {tie_break}")
    if pricing not in ("pair", "marginal", "kda"):
        raise ValueError(f"Invalid pricing: {pricing}")
    if rounding not in ("floor", "ceil", "half_up", "half_even"):
        raise ValueError(f"Invalid rounding: {rounding}")

    seen_ids = set()
    bids: list[BookOrder] = []
    asks: list[BookOrder] = []
    for o in orders:
        if o.order_id in seen_ids:
            raise ValueError(f"Duplicate order_id: {o.order_id}")
        seen_ids.add(o.order_id)
        if o.price_ticks <= 0:
            raise ValueError(f"price_ticks must be > 0, got {o.price_ticks}")
        if o.remaining <= 0:
            raise ValueError(f"remaining must be > 0, got {o.remaining}")
        if o.side not in ("BID", "ASK"):
            raise ValueError(f"Invalid side: {o.side}")
        if o.tif not in ("GTC", "IOC"):
            raise ValueError(f"Invalid tif: {o.tif}")
        if o.sessions_alive < 0:
            raise ValueError(f"sessions_alive must be >= 0, got {o.sessions_alive}")
        if o.side == "BID":
            bids.append(o)
        else:
            asks.append(o)

    if not bids or not asks:
        return []

    # 2. Xác định khối lượng tổng V
    sorted_bids = sorted(bids, key=lambda o: -o.price_ticks)
    sorted_asks = sorted(asks, key=lambda o: o.price_ticks)

    i = 0
    j = 0
    rem_b = sorted_bids[0].remaining
    rem_a = sorted_asks[0].remaining
    V = 0
    while i < len(sorted_bids) and j < len(sorted_asks):
        bid_p = sorted_bids[i].price_ticks
        ask_p = sorted_asks[j].price_ticks
        if bid_p >= ask_p:
            match_amt = rem_b if rem_b < rem_a else rem_a
            V += match_amt
            rem_b -= match_amt
            rem_a -= match_amt
            if rem_b == 0:
                i += 1
                if i < len(sorted_bids):
                    rem_b = sorted_bids[i].remaining
            if rem_a == 0:
                j += 1
                if j < len(sorted_asks):
                    rem_a = sorted_asks[j].remaining
        else:
            break

    if V == 0:
        return []

    # 3. Phân bổ cho từng phía riêng
    bid_alloc = _allocate_side(bids, "BID", V, tie_break)
    ask_alloc = _allocate_side(asks, "ASK", V, tie_break)

    # 4. Ghép cặp và định giá
    matched_bids = [o for o in bids if bid_alloc[o.order_id] > 0]
    matched_asks = [o for o in asks if ask_alloc[o.order_id] > 0]

    if tie_break == "fifo":
        matched_bids.sort(key=lambda o: (-o.price_ticks, o.seq, o.order_id))
        matched_asks.sort(key=lambda o: (o.price_ticks, o.seq, o.order_id))
    else:  # age_prorata
        matched_bids.sort(key=lambda o: (-o.price_ticks, -o.sessions_alive, o.order_id))
        matched_asks.sort(key=lambda o: (o.price_ticks, -o.sessions_alive, o.order_id))

    b_m = min(o.price_ticks for o in matched_bids)
    a_m = max(o.price_ticks for o in matched_asks)

    unmatched_bids_prices = [
        o.price_ticks for o in bids if o.remaining - bid_alloc[o.order_id] > 0
    ]
    b_next = max(unmatched_bids_prices) if unmatched_bids_prices else None

    unmatched_asks_prices = [
        o.price_ticks for o in asks if o.remaining - ask_alloc[o.order_id] > 0
    ]
    a_next = min(unmatched_asks_prices) if unmatched_asks_prices else None

    uniform_p: Optional[int] = None
    if pricing == "marginal":
        n = k_num * b_m + (k_den - k_num) * a_m
        uniform_p = _round_price(n, k_den, rounding)
    elif pricing == "kda":
        hi = min(b_m, a_next) if a_next is not None else b_m
        lo = max(a_m, b_next) if b_next is not None else a_m
        n = k_num * hi + (k_den - k_num) * lo
        uniform_p = _round_price(n, k_den, rounding)

    fills: list[Fill] = []
    idx_b = 0
    idx_a = 0
    cur_rem_b = bid_alloc[matched_bids[0].order_id]
    cur_rem_a = ask_alloc[matched_asks[0].order_id]

    while idx_b < len(matched_bids) and idx_a < len(matched_asks):
        bid_order = matched_bids[idx_b]
        ask_order = matched_asks[idx_a]
        amount = min(cur_rem_b, cur_rem_a)

        if amount > 0:
            if pricing == "pair":
                n = k_num * bid_order.price_ticks + (k_den - k_num) * ask_order.price_ticks
                p = _round_price(n, k_den, rounding)
            else:
                p = uniform_p  # type: ignore

            price_ticks = min(max(p, ask_order.price_ticks), bid_order.price_ticks)

            fills.append(
                Fill(
                    bid_id=bid_order.order_id,
                    ask_id=ask_order.order_id,
                    amount=amount,
                    price_ticks=price_ticks,
                )
            )

        cur_rem_b -= amount
        cur_rem_a -= amount
        if cur_rem_b == 0:
            idx_b += 1
            if idx_b < len(matched_bids):
                cur_rem_b = bid_alloc[matched_bids[idx_b].order_id]
        if cur_rem_a == 0:
            idx_a += 1
            if idx_a < len(matched_asks):
                cur_rem_a = ask_alloc[matched_asks[idx_a].order_id]

    return fills
