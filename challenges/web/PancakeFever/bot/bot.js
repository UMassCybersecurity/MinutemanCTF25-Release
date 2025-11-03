const express = require('express');
const path = require('path');
const puppeteer = require('puppeteer');
const app = express();
const port = 9000;
const FLAG = process.env.FLAG
app.use(express.urlencoded({ extended: true }));

app.use(express.json());
app.get('/', (req, res) => {

  console.log("Bot is get")
  res.sendFile(path.join(__dirname, 'public', 'bot.html'));
});

app.post('/lookup', async (req, res) => {
  console.log("Bot is triggered")
  const { URL } = req.body;

  if (!URL) {
    return res.send({ error: 'Missing URL' });
  }

  const reg = new RegExp(`^http://web.minuteman.umasscybersec.org:1337`);
  if (!reg.test(URL)) {
    return res.send({ error: 'Please send a URL from the Garfield site!' });
  }

  const result = await goToURL(URL);
  if (!result) {
    console.log("no result")
    return res.send({'success':`Garfield saw nothing.`});
  }
  const adminResponse = result ? `Garfield looked at this and saw \n ${result}` : `Garfield saw nothing.`;
  res.send({ success: adminResponse });
});

async function goToURL(url) {
  let text = '';
  const browser = await puppeteer.launch({
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox']
  });
  const page = await browser.newPage();

  await page.setCookie({
    name: 'flag',
    value: FLAG, 
    url: `http://${process.env.DOMAIN}`,
  });

  page.on('dialog', async dialog => {
    text += `[ALERT] ${dialog.message()}\n`;
    await dialog.accept();
  });

  await page.goto(url);
  await new Promise(resolve => setTimeout(resolve, 2000));
  await browser.close();
  return text;
}

app.listen(port, () => {
  console.log(`Bot service running on port ${port}`);
});
