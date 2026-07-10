import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ["@placementos/types"],
  output: "standalone",
};

export default nextConfig;
