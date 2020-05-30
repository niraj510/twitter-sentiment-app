import os
import re
import tweepy
from tweepy import OAuthHandler
from textblob import TextBlob
#from nltk.sentiment.vader import SentimentIntensityAnalyzer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from langdetect import detect
import pandas as pd
import collections
from collections import Counter
import string
from pathlib import Path

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
        
        
    
    def get_tweet_sentiment_vader(self, tweet):
        #analysis = TextBlob(self.clean_tweet(tweet))
        analysis = self.sia.polarity_scores(tweet)["compound"]
        if analysis > 0:
            return 'positive'
        elif analysis == 0:
            return 'neutral'
        
        return 'negative'
        
     

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
            
    def get_tweetsAllTweets(self):


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
            
    def getLocation(self):
      
        alltweets = self.get_tweetsAllTweets()
        outtweets = [[tweet.created_at,tweet.entities["hashtags"],tweet.entities["user_mentions"],tweet.favorite_count,
                      tweet.geo,tweet.id_str,tweet.lang,tweet.retweet_count,tweet.retweeted,tweet.source,tweet.text,
                      tweet._json["user"]["location"],tweet._json["user"]["name"],tweet._json["user"]["time_zone"],
                      tweet._json["user"]["utc_offset"]] for tweet in alltweets]
        
        
        location_data = []
        place = pd.Series([str(i[0]) for i in outtweets])
        print("place",place);
        location_data = pd.Series([str(i[12]) for i in outtweets])
        
        return(location_data)
      
    def filter_twitter_data(self,tweets):

        id_list = [tweet.id for tweet in tweets]
        tweet_Data = pd.DataFrame(id_list,columns=['id'])
        tweet_Data["retweet_count"]= [tweet.retweet_count for tweet in tweets]
       
    
    
        Sentiments_list = []
        Sentiments_group = []
        Subjectivity_list = []
        Subjectivity_group = []
        tweet_text_list = []
        tweet_source = []
        tweet_translation= []
        tweet_location_list = []
        
        for tweet in tweets:
            raw_tweet_text = tweet.text
            message = TextBlob(tweet.text)
            location = tweet.author.location
            source = tweet.source
            tweet_source.append(source)
            message = str(message)
            new_message = ""
    
            for letter in range(0,len(message)):
                current_read =message[letter]
                if ord(current_read) > 126:
                    continue
                else:
                    new_message =new_message+current_read
    
            message = new_message
            tweet_translation.append(message)
            #message = fix_pattern(message)
            message = TextBlob(message)
            
            sentiment = message.sentiment.polarity
            if (sentiment > 0):
                Sentiments_group.append('positive')
            elif (sentiment < 0):
                Sentiments_group.append('negative')
            else:
                Sentiments_group.append('neutral')
                
            subjectivity = message.sentiment.subjectivity
            if (subjectivity > 0.4):
                Subjectivity_group.append('subjective')
            else:
                Subjectivity_group.append('objective')
                
            Sentiments_list.append(sentiment)
            Subjectivity_list.append(subjectivity)
            tweet_text_list.append(raw_tweet_text)
            tweet_location_list.append(location)
            
            
        tweet_Data["sentiments"] = Sentiments_list
        tweet_Data["sentiments_group"] = Sentiments_group
        tweet_Data["subjectivity"]= Subjectivity_list
        tweet_Data["subjectivity_group"] = Subjectivity_group
        tweet_Data["location"] = tweet_location_list
        tweet_Data["text"] = tweet_text_list
        tweet_Data["translate"] = tweet_translation
    
     
        return (tweet_Data)
    
    def generate_chart(self,tweetsDataframe):


       retweet_table = []
        
     
    
       retweet_table.append(["Tweets"])
       df = tweetsDataframe[['translate']].drop_duplicates()[:6]
       for key in df['translate']:
          temp = [key]
          retweet_table.append(temp)
      
    
       new_list = []
       for item in tweetsDataframe['translate']:
       	new_item = [item]
       	new_list.append(new_item)
    
       text = ""    
       text_tweets = new_list
       length = len(text_tweets)
    
       for i in range(0, length):
        text = text_tweets[i][0] + " " + text
    
       lower_case = text.lower()
       cleaned_text = lower_case.translate(str.maketrans('', '', string.punctuation))
       tokenized_words = cleaned_text.split()
       #print(tokenized_words)
    
       stop_words = ["i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself",
                   "will", "just", "don", "should", "now"]
    
       final_words = [word for word in tokenized_words if word not in stop_words]
       emotion_list = []
       with open('emotions.txt', 'r') as file:
        	for line in file:
        		clear_line = line.replace('\n', '').replace(',', '').replace("'", '').strip()
        		word, emotion = clear_line.split(':')
        		if word in final_words:
        			emotion_list.append(emotion)
    
       w = Counter(emotion_list)
       c = dict(w)
    
       emotion_keys = []
       emotion_values = []
    
       for k,y in c.items():
        	emotion_keys.append(k)
        	emotion_values.append(y)
       #print(emotion_keys,emotion_values)
    
       emotion_table = []
       #emotion_table.append(["Emotion","Count"])
    
       for key,value in zip(emotion_keys,emotion_values):
         #print(key,value)
       	 temp = [key,value]
       	 emotion_table.append(temp)
       
       print(emotion_table)
       
       return (emotion_table)