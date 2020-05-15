import os
import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
#from nltk.sentiment.vader import SentimentIntensityAnalyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from langdetect import detect
import pandas as pd

recd_tweets = []

class TwitterClient(object):
    '''
    Generic Twitter Class for the App
    '''

    
    def __init__(self, query, retweets_only=False, with_sentiment=False, **kwargs):
        self.sia = SentimentIntensityAnalyzer()
        # keys and tokens from the Twitter Dev Console
        consumer_key = "Kq4mCtnOSPiNwA9ArvYq03DE7"
        consumer_secret = "aWBfVbrJWppmEy3mAbrjUHa6Y8AKU6qkCBZwA6ZpAO8BEFaoC2"
        access_token = "529590041-eZXHHkluorWkdRZRWiVYW3GVBuvr3VXt84cZcDYA"
        access_token_secret = "rqlG8jzmKTPU3bZoCwgRnOUoD5UYOx8KDjhoXySPrR3mI"
        
        # Attempt authentication
        try:
            self.auth = OAuthHandler(consumer_key, consumer_secret)
            self.auth.set_access_token(access_token, access_token_secret)
            self.query = query
            self.retweets_only = retweets_only
            self.with_sentiment = with_sentiment
            self.api = tweepy.API(self.auth)
            self.tweet_count_max = 100  # To prevent Rate Limiting
        except:
            print("Error: Authentication Failed")

    def set_query(self, query=''):
        self.query = query

    def set_retweet_checking(self, retweets_only='false'):
        self.retweets_only = retweets_only

    def set_with_sentiment(self, with_sentiment='false'):
        self.with_sentiment = with_sentiment

    def set_tweetcount(self, count=100):
        self.tweetcount = count

    def clean_tweet(self, tweet):
        return ' '.join(re.sub(
            r"(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())
    
    

    def get_tweet_sentiment(self, tweet):
        analysis = TextBlob(self.clean_tweet(tweet))
        if analysis.sentiment.polarity > 0:
            return 'positive'
        elif analysis.sentiment.polarity == 0:
            return 'neutral'
        else:
            return 'negative'
        
        
        
        # polarity += analysis.sentiment.polarity  # adding up polarities to find the average later

        # if (analysis.sentiment.polarity == 0):  # adding reaction of how people are reacting to find average later
        #     neutral += 1
        #     return neutral
        # elif (analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.3):
        #     wpositive += 1
        #     return wpositive
        # elif (analysis.sentiment.polarity > 0.3 and analysis.sentiment.polarity <= 0.6):
        #     positive += 1
        #     return positive
        # elif (analysis.sentiment.polarity > 0.6 and analysis.sentiment.polarity <= 1):
        #     spositive += 1
        #     return spositive
        # elif (analysis.sentiment.polarity > -0.3 and analysis.sentiment.polarity <= 0):
        #     wnegative += 1
        #     return wnegative
        # elif (analysis.sentiment.polarity > -0.6 and analysis.sentiment.polarity <= -0.3):
        #     negative += 1
        #     return negative
        # elif (analysis.sentiment.polarity > -1 and analysis.sentiment.polarity <= -0.6):
        #     snegative += 1
        #     return snegative
    
    def get_tweet_sentiment_vader(self, tweet):
        #analysis = TextBlob(self.clean_tweet(tweet))
        analysis = self.sia.polarity_scores(tweet)["compound"]
        if analysis > 0:
            return 'positive'
        elif analysis == 0:
            return 'neutral'
        
        return 'negative'
        
     
        
        # polarity += analysis.sentiment.polarity  # adding up polarities to find the average later

        # if (analysis.sentiment.polarity == 0):  # adding reaction of how people are reacting to find average later
        #     neutral += 1
        #     return neutral
        # elif (analysis.sentiment.polarity > 0 and analysis.sentiment.polarity <= 0.3):
        #     wpositive += 1
        #     return wpositive
        # elif (analysis.sentiment.polarity > 0.3 and analysis.sentiment.polarity <= 0.6):
        #     positive += 1
        #     return positive
        # elif (analysis.sentiment.polarity > 0.6 and analysis.sentiment.polarity <= 1):
        #     spositive += 1
        #     return spositive
        # elif (analysis.sentiment.polarity > -0.3 and analysis.sentiment.polarity <= 0):
        #     wnegative += 1
        #     return wnegative
        # elif (analysis.sentiment.polarity > -0.6 and analysis.sentiment.polarity <= -0.3):
        #     negative += 1
        #     return negative
        # elif (analysis.sentiment.polarity > -1 and analysis.sentiment.polarity <= -0.6):
        #     snegative += 1
        #     return snegative
    


    def cleanTxt(self,text):
        text =re.sub(r'@[A-Za-z0-9]+','',text) #removing @ Mentios
        text =re.sub(r"#",'',text) #removing the # symbol
        text =re.sub(r'RT[\s]+','',text)     #removing RT
        text =re.sub(r'https?:\/\/\S+','',text) #removing the hyper link
        return text
    
   
    
   
    
    #Create a function to get the Subjectivity
    def getSubjectivity(self,text):
       return TextBlob(text).sentiment.subjectivity
            
    #Create a function to get the Polarity
    def getPolarity(self,text):
       return TextBlob(text).sentiment.polarity
   
    def getSubject(self,tweets):
        subject = []
    #create a dataframe with a column called tweets
        #print("recd_tweets"+tweets.get_tweets)
        df = pd.DataFrame([tweet.text for tweet in tweets],columns=['Tweets'])
         #Cleaning the text               
        df['Tweets']=df['Tweets'].apply(self.cleanTxt)
        subject=df['Tweets'].apply(self.getSubjectivity)
        
        return subject
    
    def getPolar(self,tweets):
        polar = []
    #create a dataframe with a column called tweets
        #print("recd_tweets"+tweets.get_tweets)
        df = pd.DataFrame([tweet.text for tweet in tweets],columns=['Tweets'])
         #Cleaning the text               
        df['Tweets']=df['Tweets'].apply(self.cleanTxt)
        polar=df['Tweets'].apply(self.getPolarity)
        return polar
    
    def get_tweets(self):

        
        tweets = []
        recd_tweets1 = []
        unique_tweets = set()

        try:
            # how many groups of `tweet_count_max` tweets
            no_of_100tweets = self.tweetcount // self.tweet_count_max
            # how many do not belong in a `tweet_count_max` group
            no_of_remaining_tweets = self.tweetcount - \
                self.tweet_count_max * no_of_100tweets

            if no_of_remaining_tweets:
                recd_tweets = self.api.search(
                    q=self.query, count=no_of_remaining_tweets)
            else:
                recd_tweets = []

            maxId = recd_tweets[-1].id if recd_tweets else 0

            for _ in range(no_of_100tweets):
                nxtpg_recd_tweets = self.api.search(
                    q=self.query,
                    count=self.tweet_count_max,
                    max_id=str(maxId - 1))
                recd_tweets.extend(nxtpg_recd_tweets)
                maxId = nxtpg_recd_tweets[-1].id

            if not recd_tweets:
                pass
            
            # polarity = 0
            # positive = 0
            # wpositive = 0
            # spositive = 0
            # negative = 0
            # wnegative = 0
            # snegative = 0
            # neutral = 0   
            
            # recd_tweets1['recdtweets'] = recd_tweets
            # print("recd_tweets1"+recd_tweets1['recdtweets'])
            # tweets.append(recd_tweets1)
            for tweet in recd_tweets:
                try:
                    if detect(tweet.text) != 'en':
                        continue
                except:
                    continue

                parsed_tweet = {}

                parsed_tweet['text'] = tweet.text
                parsed_tweet['user'] = tweet.user.screen_name
                
                if self.with_sentiment == 1:
                    parsed_tweet['sentiment'] = self.get_tweet_sentiment(
                        tweet.text)
                    parsed_tweet['sentiment_vader'] = self.get_tweet_sentiment_vader(tweet.text)
                else:
                    parsed_tweet['sentiment'] = 'unavailable'
                    parsed_tweet['sentiment_vader'] = 'unavailable'

                if tweet.retweet_count > 0 and self.retweets_only == 1:
                    if parsed_tweet['text'] not in unique_tweets:
                        tweets.append(parsed_tweet)
                        unique_tweets.add(parsed_tweet['text'].lower())
                elif not self.retweets_only:
                    if parsed_tweet['text'] not in unique_tweets:
                        tweets.append(parsed_tweet)
                        unique_tweets.add(parsed_tweet['text'].lower())
            return tweets

        except tweepy.TweepError as e:
            print("Error : " + str(e))
            
    def get_tweets1(self):


        try:
            # how many groups of `tweet_count_max` tweets
            no_of_100tweets = self.tweetcount // self.tweet_count_max
            # how many do not belong in a `tweet_count_max` group
            no_of_remaining_tweets = self.tweetcount - \
                self.tweet_count_max * no_of_100tweets

            if no_of_remaining_tweets:
                recd_tweets = self.api.search(
                    q=self.query, count=no_of_remaining_tweets)
            else:
                recd_tweets = []

            maxId = recd_tweets[-1].id if recd_tweets else 0

            for _ in range(no_of_100tweets):
                nxtpg_recd_tweets = self.api.search(
                    q=self.query,
                    count=self.tweet_count_max,
                    max_id=str(maxId - 1))
                recd_tweets.extend(nxtpg_recd_tweets)
                maxId = nxtpg_recd_tweets[-1].id

            if not recd_tweets:
                pass
            
            return recd_tweets

        except tweepy.TweepError as e:
            print("Error : " + str(e))
