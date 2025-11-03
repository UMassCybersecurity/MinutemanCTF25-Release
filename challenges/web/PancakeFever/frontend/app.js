const express = require('express');
const path = require('path');
const app = express();
const port = 1337;

app.use(express.static(path.join(__dirname, 'public')));
app.use(express.urlencoded({ extended: true }));

const allowedFlavors = ["blueberries", "strawberries", "cheese"];

app.get('/', (req, res) => {
  res.send(`
    <html>
      <head>
        <title>Garfield's Pancake Palace</title>
        <style>
          body {
            background-image: url('https://www.hollywoodreporter.com/wp-content/uploads/2024/01/O_f2840_0210_comp_v005.1112-H-2024.jpg?w=1296&h=730&crop=1');
            background-size: cover;           /* make it fill the whole screen */
            background-repeat: no-repeat;     /* don’t tile the image */
            background-position: center;      /* center it nicely */
            font-family: "Comic Sans MS", cursive;
            text-align: center;
            padding-top: 60px;
            color: #333;
          }
          form {
            background: rgba(255, 255, 255, 0.9); /* translucent white box */
            display: inline-block;
            padding: 30px;
            border-radius: 20px;
            box-shadow: 3px 3px 10px rgba(0,0,0,0.3);
          }
          input {
            margin: 10px;
            padding: 10px;
            border-radius: 10px;
            border: 1px solid #ccc;
          }
          button {
            background: orange;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
          }
        </style>
      </head>
      <body>
        <h1>😸 Garfield's Pancake Palace 🥞</h1>
        <h3>Garfield loves pancakes — enter your name and favorite flavor!</h3>
        <form action="/pancake" method="get">
          <input type="text" name="name" placeholder="Your name" required><br/>
          <input type="text" name="flavor" placeholder="Pancake flavor" required><br/>
          <button type="submit">Submit</button>
        </form>
      </body>
    </html>
  `);
});

app.get('/pancake', (req, res) => {
  const { name, flavor } = req.query;
  if (!name || !flavor) {
    return res.redirect('/');
  }

  if (!allowedFlavors.includes(flavor)) {
    return res.status(400).send(`
      <h2>Invalid flavor!</h2>
      <p>Please choose from: ${allowedFlavors.join(", ")}</p>
      <a href="/">Go back</a>
    `);
  }

  res.send(`
    <h2>Hello ${name}!</h2>
  `);
});

app.listen(port, () => {
  console.log(`Frontend running on port ${port}`);
});