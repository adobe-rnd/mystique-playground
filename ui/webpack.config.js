const path = require('path');

module.exports = {
  devServer: {
    historyApiFallback: true,
    hot: true,
    port: 4010,
    host: 'localhost',
    webSocketServer: 'ws',
    allowedHosts: 'all',
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, PATCH, OPTIONS",
      "Access-Control-Allow-Headers": "X-Requested-With, content-type, Authorization"
    },
    client: {
      overlay: false,
    }
  },
  mode: 'development',
  devtool: 'source-map',
  entry: {
    toolbox: './src/toolbox_app.js',
    assistant: './src/assistant_app.js',
  },
  output: {
    filename: '[name].js',
    path: path.resolve(__dirname, 'dist'),
    clean: true
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: "babel-loader",
          options: {
            plugins: [
              ["@babel/plugin-proposal-decorators", {decoratorsBeforeExport: true, version: '2023-11'}],
            ]
          }
        }
      },
      {
        test: /\.css$/i,
        use: ["style-loader", "css-loader"],
      },
    ]
  },
  plugins: [
    // Add any plugins you need
  ],
};
