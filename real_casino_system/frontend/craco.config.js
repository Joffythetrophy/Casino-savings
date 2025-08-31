// CRACO config for REAL blockchain casino with crypto polyfills
const webpack = require('webpack');

module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      // Add polyfills for crypto and other Node.js modules needed for Solana
      webpackConfig.resolve.fallback = {
        ...webpackConfig.resolve.fallback,
        crypto: require.resolve('crypto-browserify'),
        stream: require.resolve('stream-browserify'),
        buffer: require.resolve('buffer'),
        process: require.resolve('process'),
        zlib: false,
        fs: false,
        net: false,
        tls: false,
        child_process: false,
        path: false,
        os: false,
      };

      // Add plugins for Buffer and process
      webpackConfig.plugins = [
        ...webpackConfig.plugins,
        new webpack.ProvidePlugin({
          Buffer: ['buffer', 'Buffer'],
          process: 'process',
        }),
      ];

      return webpackConfig;
    },
  },
};