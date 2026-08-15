/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  eslint: {
    // Linting is run separately in CI; don't block local builds on it.
    ignoreDuringBuilds: true,
  },
};

module.exports = nextConfig;
