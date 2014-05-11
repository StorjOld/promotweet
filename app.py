#!/usr/bin/python
# -*- coding: utf-8 -*-
from gevent import monkey; monkey.patch_all()
from gevent.pywsgi import WSGIServer
from flask import Flask, request, jsonify, session, redirect, render_template, url_for
from flask.ext.pymongo import PyMongo
from flask.ext.mongo_sessions import MongoDBSessionInterface
import requests
import json
from requests_oauthlib import OAuth1
from urlparse import parse_qs
from urllib import quote_plus
from TwitterAPI import TwitterAPI

# Notes:
# This should be pretty robust. May want to add more error handling in the future.

application = Flask('__name__')
#application.config['DEBUG'] = True

# MongoDB configuration
application.config['MONGO_HOST'] = 'localhost'
application.config['MONGO_DBNAME'] = 'storj_social'
#application.config['MONGO_USERNAME'] = ''
#application.config['MONGO_PASSWORD'] = ''

# Storj configuriation
application.config['STORJ_API_ENDPOINT'] = 'http://node2.storj.io/api'

# OAuth tokens for 'Tweet for Storj Space' Twitter application
application.config['TWITTER_CONSUMER_KEY'] = ''
application.config['TWITTER_CONSUMER_SECRET'] = ''
application.config['TWITTER_CALLBACK_URL'] = 'http://localhost:8000/twitter/access'
application.config['TWITTER_REDIRECT_URL'] = 'http://node2.storj.io'
application.config['TWITTER_PROMO_TWEET'] = 'It\'s time to decentralize storage. Try Storj today! http://storj.io #storj'

mongo = PyMongo(application)
with application.app_context():
	application.session_interface = MongoDBSessionInterface(application, mongo.db, 'sessions')

class Twitter:
	"""Tools to interact with Twitter"""
	def obtainRequestToken(self):
		oauth = OAuth1(
			application.config['TWITTER_CONSUMER_KEY'], 
			application.config['TWITTER_CONSUMER_SECRET'])
		r = requests.post(url='https://api.twitter.com/oauth/request_token?oauth_callback=%s' % quote_plus(application.config['TWITTER_CALLBACK_URL']), auth=oauth)
		credentials = parse_qs(r.content)
		self.request_key = credentials.get('oauth_token')[0]
		self.request_secret = credentials.get('oauth_token_secret')[0]

	def createAPI(self, key, secret):
		session['twttr'].api = TwitterAPI(
		application.config['TWITTER_CONSUMER_KEY'],
		application.config['TWITTER_CONSUMER_SECRET'],
		key,
		secret)

	def obtainAuthorizationUrl(self):
		authUrl = 'https://api.twitter.com/oauth/authorize?oauth_token=%s' % self.request_key
		return authUrl

	def getUser(self):
		r = session['twttr'].api.request('account/verify_credentials', {'skip_status': 1})
		for item in r:
			return {'id': item['id'], 'screen_name': item['screen_name']}

	def postTweet(self):
		r = session['twttr'].api.request('statuses/update', {'status': application.config['TWITTER_PROMO_TWEET']})
		return True if r.status_code == 200 else False

class TokenAPI:
	"""Interactions with Storj Token API"""
	def __init__(self, token):
		self.token = token

	def redeemCode(self, code):
		payload = {'promocode': code}
		headers = {'content-type': 'application/json'}
		r = requests.post(url=application.config['STORJ_API_ENDPOINT'] + '/token/redeem/' + self.token, data=json.dumps(payload), headers=headers)
		return True if r.status_code == 201 else False

@application.route('/twitter/get-space', methods = ['POST'])
def requestAuth():
	session['twttr'] = Twitter()
	session['storj'] = TokenAPI(request.form['token'])
	session['twttr'].obtainRequestToken()
	url = session['twttr'].obtainAuthorizationUrl()
	return jsonify({'url' : url})

@application.route('/twitter/access', methods = ['GET'])
def access():
	oauth_token = request.args.get('oauth_token')
	oauth_verifier = request.args.get('oauth_verifier')
	oauth = OAuth1(
		application.config['TWITTER_CONSUMER_KEY'],
		application.config['TWITTER_CONSUMER_SECRET'],
		session['twttr'].request_key,
		session['twttr'].request_secret,
		verifier=oauth_verifier)
	r = requests.post(url='https://api.twitter.com/oauth/access_token', auth=oauth)
	credentials = parse_qs(r.content)
	access_token_key = credentials.get('oauth_token')[0]
	access_token_secret = credentials.get('oauth_token_secret')[0]
	session['twttr'].createAPI(access_token_key, access_token_secret)

	userInfo = session['twttr'].getUser()
	foundTwitterUsers = mongo.db.twitter_received_space.find_one({'tid': userInfo['id']})
	if(foundTwitterUsers != None):
		error = "You have already redeemed your free 5GB of Storj space."
		return render_template('error.html', error_msg=error)
	
	posted = session['twttr'].postTweet()
	if(not posted):
		error = "We were unable to post a tweet on your behalf. Please try again later."
		return render_template('error.html', error_msg=error)

	foundCoupons = mongo.db.twitter_coupons.find_one({'status': 'ok'})
	if(foundCoupons == None):
		error = "We apologize but this promotion has expired."
		return render_template('error.html', error_msg=error)
	else:
		promocode = foundCoupons['code']
		mongo.db.twitter_coupons.update({'code':promocode}, {'code':promocode, 'status':'used'})

	redeemed = session['storj'].redeemCode(promocode)
	if(not redeemed):
		error = "We were able to post your tweet, but not redeem your free storage space. Please contact us."
		return render_template('error.html', error_msg=error)

	mongo.db.twitter_received_space.insert({'tid':userInfo['id'], 'screen_name':userInfo['screen_name']})

	return render_template('redirect.html')

if __name__ == '__main__':
	#application.run(host='0.0.0.0', port=8000, debug=True)
    server = WSGIServer(('0.0.0.0', 80), application)
    server.serve_forever()