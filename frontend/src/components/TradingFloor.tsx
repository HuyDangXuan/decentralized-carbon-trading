"use client";
import { useEffect, useRef, useState, type FormEvent } from "react";
import { useAccount } from "wagmi";
import { AUCTION_ABI_READY, getContractAddresses } from "../contracts";
import { useEIP712Order } from "../hooks/useEIP712Order";
import { microUsdcToUsd, OrderType, parseCreditAmount, parseTokenId, TimeInForce, usdToMicroUsdc } from "../lib/orders";
import { createOrderBookWS, matchingApi, WS_EVENTS, type CurrentSession, type OrderBookEntry, type OrderBookSnapshot, type OrderStatus } from "../services/matchingApi";
import { DepthChart } from "./DepthChart";

const labels: Record<OrderStatus, string> = {
  NEW: "Mới tiếp nhận", ACTIVE: "Đang chờ khớp", PARTIALLY_FILLED: "Khớp một phần", FILLED: "Đã khớp — chờ thanh toán",
  ROLLED_OVER: "Chuyển sang phiên tiếp", EXPIRED: "Hết hạn", CANCELLED: "Đã hủy", REJECTED: "Bị từ chối",
  ONCHAIN_PENDING: "Chờ xác nhận blockchain", SETTLED_FINAL: "Thanh toán đã xác nhận",
};
function price(value: string): string { return microUsdcToUsd(BigInt(value)); }

function AuctionTimer({ session }: { session: CurrentSession | null }) {
  const [now, setNow] = useState<number | null>(null);
  useEffect(() => { setNow(Date.now()); const timer = setInterval(() => setNow(Date.now()), 1000); return () => clearInterval(timer); }, []);
  if (!session || now === null) return <p className="text-sm text-gray-400">Chưa nhận được thông tin phiên từ sàn.</p>;
  const seconds = Math.max(0, Math.ceil(session.phaseEndsAt - now / 1000));
  const name = { CALL: "Gom lệnh", MATCH: "Khớp lệnh", SETTLE: "Thanh toán" }[session.phase];
  return <div aria-live="off" className="text-right">
    <p className="text-xs text-gray-400">Phiên {session.sessionId} · Chu kỳ {session.durationSeconds / 60} phút · {name}</p>
    <p className="text-2xl font-mono text-carbon-400">{String(Math.floor(seconds / 60)).padStart(2, "0")}:{String(seconds % 60).padStart(2, "0")}</p>
    {seconds === 0 && <p className="text-xs text-amber-300">Đang chờ sàn cập nhật giai đoạn tiếp theo.</p>}
  </div>;
}

function OrderSide({ orders, side }: { orders: OrderBookEntry[]; side: "BID" | "ASK" }) {
  const sorted = [...orders].sort((a, b) => {
    const diff = BigInt(a.pricePerUnit) - BigInt(b.pricePerUnit);
    return diff === 0n ? 0 : (diff > 0n ? 1 : -1) * (side === "BID" ? -1 : 1);
  }).slice(0, 10);
  const largest = sorted.reduce((max, order) => BigInt(order.remainingAmount) > max ? BigInt(order.remainingAmount) : max, 1n);
  return <div>
    <h3 className={`font-semibold mb-3 ${side === "BID" ? "text-green-400" : "text-red-400"}`}>{side === "BID" ? "Lệnh mua" : "Lệnh bán"}</h3>
    <div className="flex justify-between text-xs text-gray-400 mb-2"><span>Giá · USDC/tCO₂e</span><span>Còn lại · tCO₂e</span></div>
    {sorted.length === 0 && <p className="text-sm text-gray-500 py-6">Chưa có lệnh.</p>}
    {sorted.map(order => <div key={order.orderId} className="relative py-2 px-2 text-sm font-mono">
      <div aria-hidden className={`absolute inset-y-0 right-0 ${side === "BID" ? "bg-green-500/10" : "bg-red-500/10"}`} style={{ width: `${Number(BigInt(order.remainingAmount) * 100n / largest)}%` }} />
      <div className="relative flex justify-between gap-4"><span>{price(order.pricePerUnit)}</span><span>{order.remainingAmount}</span></div>
    </div>)}
  </div>;
}

interface TrackedOrder extends OrderBookEntry { chainId: number }
export function TradingFloor({ tokenId }: { tokenId: string }) {
  const { address, chainId, isConnected } = useAccount();
  const { signOrder, isSigning, error: signingError } = useEIP712Order();
  const [book, setBook] = useState<OrderBookSnapshot | null>(null);
  const [session, setSession] = useState<CurrentSession | null>(null);
  const [marketError, setMarketError] = useState("");
  const [sessionError, setSessionError] = useState("");
  const [message, setMessage] = useState("");
  const [formError, setFormError] = useState("");
  const [side, setSide] = useState<OrderType>(OrderType.BID);
  const [amount, setAmount] = useState("1");
  const [limitPrice, setLimitPrice] = useState("14.50");
  const [tif, setTif] = useState<TimeInForce>(TimeInForce.GTC);
  const [validMinutes, setValidMinutes] = useState("60");
  const [submitting, setSubmitting] = useState(false);
  const submittingRef = useRef(false);
  const [orders, setOrders] = useState<TrackedOrder[]>([]);
  const [refreshKey, setRefreshKey] = useState(0);
  const [historyError, setHistoryError] = useState("");
  const trackedIds = orders.filter(order => order.trader.toLowerCase() === address?.toLowerCase() && order.chainId === chainId && order.tokenId === tokenId).map(order => order.orderId).join(",");
  const scope = `${address ?? ""}:${chainId ?? ""}:${tokenId}`;
  const currentScope = useRef(scope); currentScope.current = scope;

  useEffect(() => {
    let active = true, refreshing = false;
    setBook(null); setSession(null);
    const refresh = async () => {
      if (refreshing) return;
      refreshing = true;
      const [bookResult, sessionResult] = await Promise.all([matchingApi.getOrderBook(tokenId), matchingApi.getCurrentSession(tokenId)]);
      refreshing = false;
      if (!active) return;
      setBook(bookResult.success ? bookResult.data ?? null : null);
      setMarketError(bookResult.success ? "" : bookResult.error ?? "Không tải được sổ lệnh.");
      setSession(sessionResult.success ? sessionResult.data ?? null : null);
      setSessionError(sessionResult.success ? "" : "Chưa tải được phiên; tạm dừng đặt lệnh.");
    };
    void refresh();
    const poll = setInterval(() => void refresh(), 10000);
    const ws = createOrderBookWS(tokenId);
    for (const event of WS_EVENTS) ws.on(event, () => void refresh());
    ws.connect();
    return () => { active = false; clearInterval(poll); ws.disconnect(); };
  }, [tokenId, refreshKey]);

  useEffect(() => { setMessage(""); setFormError(""); }, [scope]);

  useEffect(() => {
    if (!trackedIds) return;
    let active = true, pending = false;
    const refresh = async () => {
      if (pending) return;
      pending = true;
      const results = await Promise.all(trackedIds.split(",").map(id => matchingApi.getOrder(id)));
      pending = false;
      if (!active) return;
      setHistoryError(results.some(result => !result.success) ? "Một số trạng thái chưa cập nhật được; đang hiển thị lần xác nhận gần nhất." : "");
      setOrders(previous => previous.map(order => {
        if (order.chainId !== chainId || order.trader.toLowerCase() !== address?.toLowerCase() || order.tokenId !== tokenId) return order;
        const updated = results.find(result => result.success && result.data?.orderId === order.orderId)?.data;
        return updated ? { ...updated, chainId: order.chainId } : order;
      }));
    };
    void refresh(); const poll = setInterval(() => void refresh(), 5000);
    return () => { active = false; clearInterval(poll); };
  }, [trackedIds, address, chainId, tokenId]);

  const contract = getContractAddresses(chainId)?.carbonDoubleAuction;
  const phaseOpen = !!session && session.phase === "CALL" && session.cutoffAt > Date.now() / 1000;
  const canSign = isConnected && !!contract && AUCTION_ABI_READY && !!book && phaseOpen && !sessionError;
  async function submit(event: FormEvent) {
    event.preventDefault();
    if (submittingRef.current || !canSign) return;
    submittingRef.current = true; setSubmitting(true); setFormError(""); setMessage("");
    const originalScope = scope;
    try {
      if (!/^\d+$/.test(validMinutes) || Number(validMinutes) < 1 || Number(validMinutes) > 1440) throw new Error("Thời hạn phải từ 1 đến 1440 phút.");
      const signed = await signOrder({ orderType: side, tokenId: parseTokenId(tokenId), amount: parseCreditAmount(amount), pricePerUnit: usdToMicroUsdc(limitPrice), timeInForce: tif, deadline: BigInt(Math.floor(Date.now() / 1000) + Number(validMinutes) * 60) });
      if (!signed) return;
      if (currentScope.current !== originalScope) throw new Error("Ví, mạng hoặc token đã đổi; lệnh chưa được gửi.");
      const current = await matchingApi.getCurrentSession(tokenId);
      if (!current.success || current.data?.phase !== "CALL" || current.data.cutoffAt <= Date.now() / 1000) throw new Error("Phiên đã đóng nhận lệnh. Hãy đợi phiên tiếp theo.");
      if (currentScope.current !== originalScope) throw new Error("Ví, mạng hoặc token đã đổi; lệnh chưa được gửi.");
      const result = await matchingApi.submitOrder(signed);
      if (!result.success || !result.data) throw new Error(`${result.error ?? "Gửi lệnh thất bại."} Mã lệnh: ${signed.orderId}`);
      const accepted: TrackedOrder = { orderId: result.data.orderId, trader: signed.trader, orderType: side === OrderType.BID ? "BID" : "ASK", tokenId: signed.tokenId, amount: signed.amount, remainingAmount: signed.amount, pricePerUnit: signed.pricePerUnit, status: result.data.status, chainId: signed.chainId };
      setOrders(previous => [accepted, ...previous.filter(order => order.orderId !== accepted.orderId)]);
      if (currentScope.current === originalScope) { setMessage("Sàn đã tiếp nhận lệnh. Khớp lệnh và thanh toán sẽ được xác nhận riêng."); setRefreshKey(value => value + 1); }
    } catch (cause) { if (currentScope.current === originalScope) setFormError(cause instanceof Error ? cause.message : "Không gửi được lệnh."); }
    finally { submittingRef.current = false; setSubmitting(false); }
  }

  return <section className="mt-10 border-t border-gray-700 pt-8" aria-labelledby="trading-title">
    <div className="flex flex-wrap items-start justify-between gap-4 mb-6"><div><h2 id="trading-title" className="text-xl font-bold">Sàn giao dịch tín chỉ</h2><p className="text-sm text-gray-400 mt-1">Token #{tokenId} · 1 token = 1 tCO₂e · Thanh toán MockUSDC</p></div><AuctionTimer session={session} /></div>
    {marketError && <p role="status" className="mb-4 text-sm text-amber-300">Chưa kết nối được sổ lệnh: {marketError}</p>}
    <div className="grid lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 rounded-xl border border-gray-700 bg-gray-800/40 p-5">
        <DepthChart book={book} />
        {book?.lastClearingPrice && <p className="text-sm mb-4 text-gray-300">Giá khớp phiên gần nhất: {price(book.lastClearingPrice)} USDC/tCO₂e</p>}
        <div className="grid sm:grid-cols-2 gap-6"><OrderSide orders={book?.bids ?? []} side="BID" /><OrderSide orders={book?.asks ?? []} side="ASK" /></div>
        <p className="mt-5 text-xs text-gray-500">Thanh độ sâu biểu diễn khối lượng còn lại của tối đa 10 lệnh mỗi phía. Lệnh được khớp theo phiên; GTC tối đa 3 phiên.</p>
      </div>
      <form onSubmit={submit} className="rounded-xl border border-gray-700 p-5 space-y-4">
        <h3 className="font-semibold">Đặt lệnh giới hạn</h3>
        <label className="block text-sm">Loại lệnh<select className="trading-input" value={side} onChange={event => setSide(Number(event.target.value) as OrderType)}><option value={OrderType.BID}>Mua tín chỉ</option><option value={OrderType.ASK}>Bán tín chỉ</option></select></label>
        <label className="block text-sm">Khối lượng · tCO₂e<input className="trading-input" inputMode="numeric" value={amount} onChange={event => setAmount(event.target.value)} required /></label>
        <label className="block text-sm">Giá giới hạn · USDC/tCO₂e<input className="trading-input" inputMode="decimal" value={limitPrice} onChange={event => setLimitPrice(event.target.value)} required /></label>
        <label className="block text-sm">Hiệu lực<select className="trading-input" value={tif} onChange={event => setTif(Number(event.target.value) as TimeInForce)}><option value={TimeInForce.GTC}>GTC — chuyển tiếp tối đa 3 phiên</option><option value={TimeInForce.IOC}>IOC — hủy phần dư sau phiên</option></select></label>
        <label className="block text-sm">Hết hạn sau · phút<input className="trading-input" inputMode="numeric" value={validMinutes} onChange={event => setValidMinutes(event.target.value)} required /></label>
        <p className="text-xs text-gray-400">Ký lệnh không tốn gas. Cấp quyền chuyển token trước khi thanh toán có thể cần giao dịch blockchain.</p>
        {!isConnected ? <p className="text-sm text-amber-300">Kết nối ví để đặt lệnh.</p> : (!contract || !AUCTION_ABI_READY) ? <p className="text-sm text-amber-300">Chưa sẵn sàng giao dịch trên mạng này. Sàn đang chờ cấu hình hợp đồng.</p> : (!phaseOpen || sessionError) ? <p className="text-sm text-amber-300">Phiên chưa mở nhận lệnh.</p> : null}
        <button type="submit" disabled={!canSign || submitting || isSigning} className="w-full rounded-lg bg-carbon-600 py-3 font-semibold disabled:opacity-40 disabled:cursor-not-allowed">{isSigning ? "Đang chờ ký trên ví…" : submitting ? "Đang gửi lệnh…" : "Ký và gửi lệnh"}</button>
        {(formError || signingError) && <p role="alert" className="text-sm text-red-300 break-words">{formError || signingError?.message}</p>}
        {message && <p role="status" className="text-sm text-green-300">{message}</p>}
      </form>
    </div>
    <div className="mt-6"><h3 className="font-semibold mb-3">Lệnh gửi trong lần mở trang này</h3><p className="text-xs text-gray-400 mb-3">Trạng thái cập nhật từ sàn. “Đã khớp” chưa có nghĩa thanh toán blockchain đã hoàn tất.</p>
      {historyError && <p role="status" className="text-sm text-amber-300 mb-3">{historyError}</p>}
      <div className="overflow-x-auto"><table className="w-full text-sm text-left"><thead className="text-gray-400"><tr><th className="p-2">Lệnh</th><th className="p-2">Loại</th><th className="p-2">Giá USDC</th><th className="p-2">Còn lại / Tổng tCO₂e</th><th className="p-2">Trạng thái</th></tr></thead><tbody>
        {orders.filter(order => order.trader.toLowerCase() === address?.toLowerCase() && order.chainId === chainId && order.tokenId === tokenId).map(order => <tr key={order.orderId} className="border-t border-gray-800"><td className="p-2 font-mono" title={order.orderId}>{order.orderId.slice(0, 10)}…</td><td className="p-2">{order.orderType === "BID" ? "Mua" : "Bán"}</td><td className="p-2">{price(order.pricePerUnit)}</td><td className="p-2">{order.remainingAmount} / {order.amount}</td><td className="p-2">{labels[order.status]}{order.rolloverCount !== undefined ? ` (${order.rolloverCount}/3)` : ""}</td></tr>)}
        {!trackedIds && <tr><td colSpan={5} className="p-4 text-gray-500">Chưa có lệnh được sàn tiếp nhận trong lần mở trang này.</td></tr>}
      </tbody></table></div>
    </div>
  </section>;
}
