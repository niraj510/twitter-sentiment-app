import os
from flask import Flask, request, render_template, jsonify
from twitter import TwitterClient
import json


def strtobool(v):
    return v.lower() in ["yes", "true", "t", "1"]


app = Flask(__name__)
# Setup the client <query string, retweets_only bool, with_sentiment bool>
api = TwitterClient('Donald Trump')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/tweets')
def tweets():
    retweets_only = request.args.get('retweets_only')
    api.set_retweet_checking(strtobool(retweets_only.lower()))
    with_sentiment = request.args.get('with_sentiment')
    api.set_with_sentiment(strtobool(with_sentiment.lower()))
    query = request.args.get('query')
    api.set_query(query)
    tweetcount = int(request.args.get('tweetcount'))
    api.set_tweetcount(tweetcount)

    tweets = api.get_tweets()
    tweetsForscatter = api.get_tweetsAllTweets()
    subject =[];
    polar = [];
    subject=   api.getSubject(tweetsForscatter)
    polar=   api.getPolar(tweetsForscatter)
    subject = subject.to_json()
    polar = polar.to_json()
    
    jsnobjectSubject =json.loads(subject)
    jsnobjectpolar =json.loads(polar)
    
    #emotinal analysis
    tweet_Data  = api.filter_twitter_data(tweetsForscatter)
    emotion_plot= []
    emotion_plot= api.generate_chart(tweet_Data)
 
    #location data
    location_data = api.getLocation();
    location_data = location_data.to_json()
   
    #print("hi", location_data);
    location_data = [['fo', 0],['us', 1],['jp', 2],['in', 3],['fr', 4],['cn', 5],['pt', 6],['sw', 7],['sh', 8],['ec', 9],['au', 10],
['ph', 11],['es',12],['bu',13],['mv', 14],['sp', 15],['gb', 16],['gr', 17],['dk', 18],['gl', 19],['pr', 20],['um', 21],
['vi', 22],['ca', 23],['ar', 24],['cl', 25],['cv', 26],['dm', 27],['sc', 28],['jm', 29],['om', 30],['vc', 31],['sb', 32],['lc', 33],['no', 34],
['kn', 35],['bh', 36],['id', 37],['mu', 38],['se', 39],['ru', 40],['tt', 41],['br', 42],['bs', 43],['pw', 44],['gd', 45],['ag', 46],['fj', 47],
['bb', 48],['it', 49],['mt', 50]]
    
    print("{} tweets".format(len(tweets)))
    return jsonify({'data': tweets, 'count': len(tweets), 
                    'subject' : jsnobjectSubject,
                    'polar' : jsnobjectpolar,
                    'emotion_plot' : emotion_plot,
                    'location_data' : location_data})


#port = int(os.environ.get('PORT', 5000))
#app.run(host="127.0.0.1", port=port, debug=True)
