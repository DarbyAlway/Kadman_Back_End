// server.js
const express = require('express');
const app = express();
const port = 3000;

// Serve static files from public/
app.use(express.static('public'));

app.listen(port, () => {
  console.log(`LIFF app running at http://localhost:${port}`);
});
