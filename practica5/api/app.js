const express = require("express");
const bodyParser = require("body-parser");
const Twit = require('twit')
const franc = require('franc')
const app = express();

const at = require('./security/AccessToken')

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false}));

/*Access to XMLHttpRequest at 'http://localhost:3000/api/ibex35volatilitypred' from origin 'http://localhost:8080' has
been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.*/
app.use((req, res, next) => {
  res.setHeader("Access-Control-Allow-Origin", "*");
  res.setHeader(
    "Access-Control-Allow-Headers",
    "Origin, X-Requested-With, Content-Type, Accept"
  );
  res.setHeader(
    "Access-Control-Allow-Methods",
    "GET, POST, PATCH, DELETE, OPTIONS"
  );
  next();
});

var T = new Twit({
    
    timeout_ms:           60*1000,  // optional HTTP request timeout to apply to all requests.
    strictSSL:            true,     // optional - requires SSL certificates to be valid.
})

app.get('/twitextract/extractTrends/:word', (req, res, next) => {

    const keyword = req.params.word;
    T.get('search/tweets', 
    { q: keyword + ' since:2020-01-01', count: 2, language: 'es' }, 
      function(err, data, response) {
        const tweets = data.statuses
        .map(tweet => `${tweet.text}`)
        //.filter(tweet => tweet.LANG === 'es')
        console.log(tweets)
        res.status(201).json({
          tweets
        });
    })
});

module.exports = app;