'''
Created on Jul 17, 2016

@author: Rohit Bhawal
'''
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import time
import os
import re
import json
import pandas as pd
import matplotlib.pyplot as myPlot
import numpy as np

ACCESS_TOKEN = "XXXXXXXXXX"
ACCESS_TOKEN_SECRET = "XXXXXXXXX"
CONSUMER_KEY = "XXXXXXXXXX"
CONSUMER_SECRET = "XXXXXXXXXXX"

TWEET_DATA_FILE = "TwitterData.txt"
POSITIVE_DATA_FILE = "positive-words.txt"
NEGATIVE_DATA_FILE = "negative-words.txt"

 
BRAND_NAMES = ['Samsung', 'Apple', 'HTC', 'Sony', 'Xiaomi', 'Huawei', 'Nokia', 'LG', 'Lenovo', \
               'OnePlus', 'Microsoft']

Positive_Words = []
Negative_Words = []

def loadPositiveData():
    data = open(getPosivitiveDatFilePath(), 'r')
    words = []
    for line in data:
        line = line.rstrip("\n")
        if not ';' in line:
            words.append(line)
    return words

def loadNegativeData():
    data = open(getNegativeDatFilePath(), 'r')
    words = []
    for line in data:
        line = line.rstrip("\n")
        if not ';' in line:
            words.append(line)
    return words

class myStreamListener(StreamListener):

    def on_data(self, data):
        print data
        dataFile = getTweetDataPath()
        myFile = open(dataFile, 'a')
        myFile.write(data)
        myFile.close()
            
        return True

    def on_error(self, status):
        print status

def listenTweets(waitTime=60):
    l = myStreamListener()
    auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    stream = Stream(auth, l)
    stream.filter(track=BRAND_NAMES, async= True)
    time.sleep(waitTime)
    print "Disconnecting"  
    stream.disconnect()

def getTweetDataPath():
    return os.path.join(os.path.dirname(__file__), TWEET_DATA_FILE)

def getPosivitiveDatFilePath():
    return os.path.join(os.path.dirname(__file__), POSITIVE_DATA_FILE)

def getNegativeDatFilePath():
    return os.path.join(os.path.dirname(__file__), NEGATIVE_DATA_FILE)

def wordSerch(word, text):
    word = word.lower()
    text = text.lower()
    match = re.search(word, text)
    if match:
        textBlock = text.split(' ')
        posCount = len(set(textBlock).intersection(Positive_Words))
        negCount = len(set(textBlock).intersection(Negative_Words))
        
        if not (posCount == 0 and negCount == 0):
            if posCount > negCount:
                return 1
            else:
                return -1
        else:
            return 0
    return -999

if __name__ == '__main__':
    listenTweets(60*60)
    Positive_Words = loadPositiveData()
    Negative_Words = loadNegativeData()

    tweets_data_path = getTweetDataPath()
    tweets_data = []
    tweets_file = open(tweets_data_path, "r")
    count = 1
    for line in tweets_file:
        try:
            tweet = json.loads(line)
            if 'text' in tweet:
                tweets_data.append(tweet)
#                 count = count + 1
#             if count > 10000:
#                 break;
        except:
            continue
    tweets = pd.DataFrame()   
    tweets['text'] = map(lambda tweet: tweet['text'], tweets_data)

    positivePlotData = []
    negativePlotData = []
    neutralPlotData = []

    for brand in BRAND_NAMES:
        tweets[brand] = tweets['text'].apply(lambda tweet: wordSerch(brand, tweet))
        try:
            positivePlotData.append(tweets[brand].value_counts()[1])
        except:
            positivePlotData.append(0)
        try:
            negativePlotData.append(tweets[brand].value_counts()[-1])
        except:
            negativePlotData.append(0)
        try:
            neutralPlotData.append(tweets[brand].value_counts()[0])
        except:
            neutralPlotData.append(0)

       
    indexVal = np.arange(len(BRAND_NAMES))
    width = 0.2
    fig, ax = myPlot.subplots()
    posPlot = myPlot.bar(indexVal, positivePlotData, width, alpha=1, color='g', label = "Positive")
    
    negPlot = myPlot.bar(indexVal + width, negativePlotData, width, alpha=1, color='r', label = "Negative")
    
    neuPlot = myPlot.bar(indexVal + width + width, neutralPlotData, width, alpha=1, color='b', label = "Neutral")
    
    ax.set_ylabel('Number of tweets', fontsize=15)
    ax.set_title('Brand Sentiment Analysis', fontsize=10, fontweight='bold')
    ax.set_xticks(indexVal+width+(width/2))
    ax.set_xticklabels(BRAND_NAMES)
    myPlot.legend()
    myPlot.tight_layout()
    myPlot.show()
    
