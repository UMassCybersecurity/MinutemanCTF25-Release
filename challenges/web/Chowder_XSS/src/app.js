const express = require('express'); // module used to code javascript servers
const { v4: uuidv4 } = require('uuid'); // used to generate unique IDs
const path = require('path'); // helper module to more easily handle paths on a website
const cookiep = require('cookie-parser'); // used to parse http cookies.
const bodyp = require('body-parser'); // used to request bodies of http requests

const fs = require('fs'); // used to read local files on the server. Mostly to retrieve the HTML page

const redis = require('redis'); // a database. technically a cache but just think of it as a database. It functions like a dictionary.
const mung_daal = require('./mung_daal.js'); // other code in the challenge here. make sure to read this!

const dom_purify = require('isomorphic-dompurify') // a way to sanitize for XSS

const app = express(); // start up a basic express server. this will handle requets for us.
const flag = process.env.FLAG || "MINUTEMAN{TEST_FLAG}" // use the flag specified in the environment of the server. Otherwise, use a test flag.
const port = process.env.port || 4501; // use the port specified in the environment of the server. Otherwise, use a test port.

const client = redis.createClient({ // create the redis instance
  'url': process.env.REDIS_URL
})
client.on('error', err => console.log('Redis Client Error', err));
client.connect();

app.use(cookiep()); // use the modules imported above. This allows us to conveniently retrieve this data from requests that the server receives
app.use(bodyp.urlencoded())
app.use('/images', express.static('images')); // allow clients to access the files in the images directory/

async function set_cache(key,val){ // helper function to store items in the redis database
  return (await client.set(key,JSON.stringify(val)));
}

async function get_cache(key){ // helper function to store items in the redis database
  return JSON.parse(await client.get(key));
}

app.get('/', async (req, res) => { // what happens when a client visits the base website with a get request
  let UID = req.cookies.order_id; // ensures that the client is assigned an ID. If they don't have one, set their ID for them to a random one.
  if(!UID){
    UID = uuidv4();
    res.set({'Set-Cookie':`order_id=${UID}`});
  }

  res.redirect(`/order/${UID}`); // redirect the client to the order page corresponding to their ID.
})

app.get('/order/:id',async (req,res)=>{ // what happens when a client visits the order endpoint. The last part of the URL is stored in req.params.id (hence the :id part)
  if(!req.params) { // you didn't pass in an ID!'

    return res.redirect('/')
  }

  let order = await get_cache(req.params.id); // retrieve the order data for the user, if it exists

  res.setHeader('Content-Type', 'text/html'); // builds the HTML page to send to the client
  let htmlContent;
  fs.readFile(path.join(__dirname,'public','index.html'), (err, data) => {
      if(err) {
        res.send("Problem creating HTML");
      } else {
        htmlContent = data.toString(); // get the html page in public/index.html and store it as a string

        if(order) { // if there is an order already, place it into the HTML page
          let content = '<div id="order">';

          content += order

          content += '</div>';
          htmlContent = htmlContent.replace('<div id="order">You haven\'t submitted an order yet!</div>', content);
        }
        res.send(htmlContent); // send html to the client with the changes above.
      }
  });
})

app.post('/create',async (req,res)=>{ // let client create an order with a post request.
  let order_id; // javascript scoping requires us to declare this outside the if statement
  if(!req.cookies || !req.cookies.order_id || !(typeof req.cookies.order_id === 'string') || !(client.exists(req.cookies.order_id))){ // make sure cookie exists to avoid crashes
    order_id = uuidv4();
    res.set({'Set-Cookie':`order_id=${order_id}`});
  } else {
    order_id = req.cookies.order_id
  }
  if(!req.body.order){ // check if an order was given in the HTTP request body.
    return res.send("Did not get a order!")
  }
  const order = req.body.order

  await set_cache(req.cookies.order_id, order); // save the order to the database

  if(DOMPurify.sanitize(order) === order) { // checks if there's any suspicious code in the order, specifically XSS.
    mung_daal(flag, order_id); // if it's safe, have Mung Daal take a look at it!'
    return res.send(`Chowder is taking your order to the kitchen. Mung Daal will review your order soon! Visit <href>/order/${order_id}</href> to see your order!`);
  } else { // if there's suspicious content in the order, don't let Mung Daal look at it! He has confidential data in his browser!
    return res.send(`Truffles noticed something suspicious with your order! Look upon your order at <href>/order/${order_id}</href> and reflect on your actions, you Rapscallion!`);
  }
})

app.listen(port, () => { // tells the server to accept connections on the given port
  console.log(`Example app listening on port ${port}`)
})
