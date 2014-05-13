promotweet
==========

Promotweet is a small Flask application that enables Storj users to acquire free space in return for tweeting about Storj.

In the main application, after clicking 'Tweet', a popup will appear asking the user for permission to let the Storj Twitter application post on its behalf. If the user accepts, relevant access tokens are sent back to the app and used to complete the transaction. If the transaction is successful, the popup will close and the node page will refresh, reflecting the additional storage space.

Protections are in place to prevent the user from tweeting repeatedly or redeeming the promotion more than once.

The app currently depends on MongoDB for recording coupon status, user redemption and server-side sessions.

# Configuration

## MongoDB
* `MONGO_HOST` Host of MongoDB server
* `MONGO_DBNAME` Name of database with relevant collections on MongoDB node
* `MONGO_USERNAME` Not currently in use, but recommended for production.
* `MONGO_PASSWORD` Not currently in use, but recommended for production.

## Storj API
* `STORJ_API_ENDPOINT` The base path used to access the Storj API

## Twitter
* `TWITTER_CONSUMER_KEY` API key for Storj Twitter application
* `TWITTER_CONSUMER_SECRET` API secret for Storj Twitter application
* `TWITTER_CALLBACK_URL` URL where access tokens are sent after Twitter user authorizes Storj to post on their behalf
* `TWITTER_REDIRECT_URL` URL to redirect to after successful tweet and redemption of free space
* `TWITTER_PROMO_TWEET` The tweet that will be posted on the user's behalf.