const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

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
    playground: './src/playground/main.js',
    copilot: './src/copilot/main.js',
    creator: './src/creator/main.js',
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
      {
        test: /\.(png|jpg|gif|svg|woff|woff2|eot|ttf|otf)$/i,
        use: [
          {
            loader: 'file-loader',
            options: {
              name: '[path][name].[ext]',
            },
          },
        ],
      },
    ]
  },
  plugins: [
    new HtmlWebpackPlugin({
      chunks: ['creator'],
      templateContent: `
        <html lang="">
          <head>
            <meta charset="utf-8">
            <title>Mystique Web Creator</title>
          </head>
          <body>
            <web-creator-component></web-creator-component>
          </body>
        </html>
      `,
    }),
  ],
};
