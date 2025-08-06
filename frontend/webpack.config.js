const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');
const webpack = require('webpack');

module.exports = {
  entry: './src/index.js',
  output: {
    path: path.resolve(__dirname, 'dist'),
    filename: 'bundle.js',
    publicPath: '/',
  },
  module: {
    rules: [
      {
        test: /\.(js|jsx)$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader',
          options: {
            presets: ['@babel/preset-env', '@babel/preset-react'],
          },
        },
      },
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader'],
      },
    ],
  },
  plugins: [
    new HtmlWebpackPlugin({
      template: './public/index.html',
    }),
    new webpack.DefinePlugin({
      'process.env.NODE_ENV': JSON.stringify(process.env.NODE_ENV || 'production'),
      'process.env.REACT_APP_API_URL': JSON.stringify(process.env.REACT_APP_API_URL || undefined),
      'process.env.REACT_APP_BACKEND_HOST': JSON.stringify(process.env.REACT_APP_BACKEND_HOST || undefined),
      'process.env.REACT_APP_BACKEND_PORT': JSON.stringify(process.env.REACT_APP_BACKEND_PORT || undefined),
    }),
  ],
  devServer: {
    static: {
      directory: path.join(__dirname, 'public'),
    },
    compress: true,
    port: 3000,
    historyApiFallback: true,
    proxy: {
      '/api': {
        target: process.env.BACKEND_URL || 'http://localhost:5000',
        changeOrigin: true,
        secure: false,
        timeout: 10000,
        proxyTimeout: 10000,
        onError: function (err, req, res) {
          console.log('Proxy error:', err);
          res.writeHead(502, {
            'Content-Type': 'application/json',
          });
          res.end(JSON.stringify({ error: 'Backend server unavailable' }));
        },
        onProxyReq: function (proxyReq, req, res) {
          console.log(`Proxying ${req.method} ${req.url} to ${process.env.BACKEND_URL || 'http://localhost:5000'}`);
        },
      },
    },
  },
  resolve: {
    extensions: ['.js', '.jsx'],
  },
};