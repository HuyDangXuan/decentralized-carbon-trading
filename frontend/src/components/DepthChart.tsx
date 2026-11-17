import { microUsdcToUsd } from "../lib/orders";
import type { OrderBookSnapshot, OrderBookLevel } from "../services/matchingApi";

function cumulative(levels: OrderBookLevel[]) {
  let volume = 0n;
  return levels.map(level => ({ price: BigInt(level.pricePerUnit), volume: volume += BigInt(level.remainingAmount) }));
}

export function DepthChart({ book }: { book: OrderBookSnapshot | null }) {
  if (!book || book.bids.length + book.asks.length === 0) return null;
  const bids = cumulative(book.bids), asks = cumulative(book.asks);
  const points = [...bids, ...asks];
  const min = points.reduce((value, point) => point.price < value ? point.price : value, points[0].price);
  const max = points.reduce((value, point) => point.price > value ? point.price : value, points[0].price);
  const volume = points.reduce((value, point) => point.volume > value ? point.volume : value, 1n);
  const coordinates = (levels: typeof bids) => levels.map(point => {
    const x = max === min ? 500 : Number((point.price - min) * 1000n / (max - min));
    const y = 180 - Number(point.volume * 160n / volume);
    return `${x},${y}`;
  }).join(" ");
  return <figure className="mb-5 border-b border-gray-700 pb-4">
    <figcaption className="text-sm text-gray-300 mb-2">Độ sâu thị trường · khối lượng tích lũy</figcaption>
    <svg viewBox="-10 0 1020 195" role="img" aria-label={`Độ sâu mua bán từ ${microUsdcToUsd(min)} đến ${microUsdcToUsd(max)} USDC/tCO2e, khối lượng tối đa ${volume} tCO2e`} className="w-full h-36">
      <path d="M0 180H1000" stroke="#4b5563" fill="none" />
      {bids.length > 0 && <polyline points={coordinates(bids)} stroke="#4ade80" strokeWidth="3" fill="none" vectorEffect="non-scaling-stroke" />}
      {asks.length > 0 && <polyline points={coordinates(asks)} stroke="#f87171" strokeWidth="3" fill="none" vectorEffect="non-scaling-stroke" />}
      {points.map((point, i) => <circle key={i} cx={max === min ? 500 : Number((point.price - min) * 1000n / (max - min))} cy={180 - Number(point.volume * 160n / volume)} r="4" fill={i < bids.length ? "#4ade80" : "#f87171"} />)}
    </svg>
    <div className="flex justify-between text-xs text-gray-400"><span>{microUsdcToUsd(min)} USDC/tCO₂e</span><span>{volume.toString()} tCO₂e tối đa</span><span>{microUsdcToUsd(max)} USDC/tCO₂e</span></div>
  </figure>;
}
