# MongoDB configuration
MONGO_HOST 		= 'http://127.0.0.1'
MONGO_DBNAME	= 'storj_social'
#MONGO_USERNAME
#MONGO_PASSWORD

# Storj configuriation
STORJ_API_ENDPOINT = 'http://node2.storj.io/api'

# OAuth tokens for twitter app
TWITTER_CONSUMER_KEY = ''
TWITTER_CONSUMER_SECRET = ''
TWITTER_CALLBACK_URL = 'http://127.0.0.1/twitter/access'
TWITTER_REDIRECT_URL = 'http://node2.storj.io'
TWITTER_PROMO_TWEET = 'It\'s time to decentralize storage. Try Storj today! http://storj.io #storj'

try:
	from local_settings import *
except ImportError:
	pass