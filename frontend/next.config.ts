import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Allow the app to proxy API requests to the FastAPI backend in development
  async rewrites() {
    return [
      {
        source: '/api/backend/:path*',
        destination: `${process.env.NEXT_PUBLIC_API_URL ?? 'http://localhost:8000'}/api/:path*`,
      },
    ];
  },
};

export default nextConfig;
