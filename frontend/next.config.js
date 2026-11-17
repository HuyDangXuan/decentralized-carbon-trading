/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  async rewrites() {
    const engine = (process.env.MATCHING_API_URL ?? process.env.NEXT_PUBLIC_MATCHING_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");
    const paths = ["orders", "orders/:orderId", "orderbook/:tokenId", "sessions/current"];
    return paths.map((path) => ({
      source: `/matching/api/v1/${path}`,
      destination: `${engine}/api/v1/${path}`,
    }));
  },
};

module.exports = nextConfig;
