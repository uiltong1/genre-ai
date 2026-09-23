const { createProxyMiddleware } = require('http-proxy-middleware');

const API_HOST = process.env.REACT_APP_API_HOST || 'http://host.docker.internal:8000';

module.exports = function (app) {
  app.use(
    '/predict',
    createProxyMiddleware({
      target: API_HOST,
      changeOrigin: true,
      onProxyReq: (proxyReq) => {
        proxyReq.setHeader('Origin', API_HOST);
      },
    })
  );
};
