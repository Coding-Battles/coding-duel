import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  eslint: {
    ignoreDuringBuilds: true,
  },
  typescript: {
    ignoreBuildErrors: true,
  },
  images: {
    remotePatterns: [
      {
        protocol: "https",
        hostname: "*.googleusercontent.com",
      },
      {
        protocol: "http",
        hostname: process.env.NEXT_PUBLIC_API_HOSTNAME || "localhost",
        port: "8000",
        pathname: "/uploads/**",
      },
    ],
  },
  devIndicators: false,
  reactStrictMode: false,

  
};

export default nextConfig;
