const express = require('express');
const path = require('path');
const app = express();
const port = 3000; // your port

app.use(express.static('public'));

// Route for "/"
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'index.html'));
});

// Route for "/payment"
app.get('/payment', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'payment.html'));
});

app.listen(port, () => {
  console.log(`App running at http://localhost:${port}`);
});
