const nextConfig = {
  output: "standalone",
  async headers() {
    return [
      {
        source: "/sw.js",
        headers: [{ key: "Content-Type", value: "application/javascript" }],
      },
    ];
  },
};

export default nextConfig;
