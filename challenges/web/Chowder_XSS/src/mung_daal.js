const puppeteer = require('puppeteer'); // Puppeteer is a module used to mimick a browser.
const env = require('dotenv').config(); // Module used to get environment variables.

const port = process.env.port || 4501 // use the port specified in the environment of the server. Otherwise, use a test port.

function checkOrder(flag, order_id){ // Have Mung Daal (the admin) check an order. This simulates him using a browser to open the order on the website.
  flag = flag + ""; // turn flag into string, ngl I forget why I did this
  return new Promise(async (res,rej)=>{
    await new Promise((resolve) => setTimeout(resolve, .5*60*1000)); // Chowder needs 30 seconds to deliver the order to Mung Daal!
    const browser = await puppeteer.launch({ // launches google chrome
      executablePath: '/usr/bin/google-chrome-stable',
      args: ['--no-sandbox']
    });
    let page = await browser.newPage(); // opens a blank new page
    await page.setCookie(...[{ // Mung Daal's browser will carry a super secret cookie while visiting orders!
      'name':'flag',
      'value':flag,
      'url':'http://127.0.0.1'
    }]);
    page // Debug data. Don't worry about this part
      .on('console', message =>
      {
        console.log(`[BROWSER] ${message.type().substr(0, 3).toUpperCase()} ${message.location().url} ${message.text()}`);
      })
      .on('pageerror', ({ message }) => console.log(message))
      .on('response', response =>
        {
        console.log(`[BROWSER] ${response.status()} ${response.url()}`);

        })
      .on('requestfailed', request =>
      console.log(`[BROWSER] ${request.failure()} ${request.url()}`))

    await page.goto(`http://127.0.0.1:${port}/order/${order_id}`); // Visit the page with the order
    await new Promise((resolve) => setTimeout(resolve, 0.5*60*1000)); // Stay on the page for 30 seconds

    return res(await browser.close()); // Leave
  })
}

module.exports = checkOrder // Allows the app.js file to run this method.
