import express from 'express';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const app = express();
const port = process.env.PORT || 3000;
const distPath = path.join(__dirname, 'dist');

console.log(`Serving from: ${distPath}`);

// Serve static files
app.use(express.static(distPath, {
  maxAge: '1h',
  etag: false
}));

// SPA fallback
app.get('*', (req, res) => {
  res.sendFile(path.join(distPath, 'index.html'), (err) => {
    if (err) {
      console.error('Error serving index.html:', err);
      res.status(500).send('Server error');
    }
  });
});

// Error handler
app.use((err, req, res, next) => {
  console.error('Server error:', err);
  res.status(500).send('Server error');
});

const server = app.listen(port, '0.0.0.0', () => {
  console.log(`✓ Frontend server listening on 0.0.0.0:${port}`);
});

server.on('error', (err) => {
  console.error('Server error:', err);
  process.exit(1);
});
