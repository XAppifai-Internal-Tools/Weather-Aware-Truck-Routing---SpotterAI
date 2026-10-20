import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{ source: "/api/:path*", destination: "http://127.0.0.1:8000/api/:path*" }];
  },
  experimental: {
    agentFeedback: true,
    proxyTimeout: 90_000,
  },
  cacheComponents: true,
  partialPrefetching: true,
  turbopack: {
    rules: {
      "*.css": {
        loaders: ["@tailwindcss/turbopack"],
        as: "*.css",
      },
    },
  },
};

export default nextConfig;
