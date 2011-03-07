#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tweepy
import twitter
from twitter import TwitterError

import time
from threading import Thread
import sys
from urllib2 import URLError

#added for internal stuff

import traceback

consumer_key ='' #add the customer API key here
consumer_secret = '' #add the customer API secret key here

key = '' # temp oauth token eg HForwq844UL9Rp4QVpT142eXU1gOiPaGPUqhP2o
token = '' #temp oauth token key eg 8410805

serverKey='' # key once generating one from the key token and secret
secret =''# key secret generating one from the key token and secret

class Bot():
    SLEEP_TIME = 70;
    TWEETS_LENGTH = 140; 
    
    
    def getToken(self):
        auth = tweepy.OAuthHandler(consumer_key,consumer_secret )
        
        try:
            redirect_url = auth.get_authorization_url()
        except tweepy.TweepError:
            print 'Error! Failed to get request token.'
            
        print redirect_url
        
    def getKey(self):
        
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_request_token(key, secret)


        try:
            auth.get_access_token(token)
        except tweepy.TweepError:
            print 'Error! Failed to get access token.'
            
        print auth.access_token.key
        print auth.access_token.secret
        
        return
    
    def debug(self,message):
        '''
        Print a debug message
        '''
        try:    
            output= time.strftime("%Y/%m/%d %H:%M:%S ", time.localtime()) + str(message)
        except UnicodeEncodeError:
            output= time.strftime("%Y/%m/%d %H:%M:%S ", time.localtime()) + str(message.encode("utf-8"))
        print output
        return
    
    def Tweet(self,message,in_reply_to_status_id=None):
        '''
        Tweet a message
        '''
        self.api.PostUpdate(message, in_reply_to_status_id)
        self.debug('Tweeting:' + message)
        return
    
    def setRunning(self,status):
        self.running = status
        return
    def getRunning(self):
        return self.running
    
    def __init__(self,serverKey,access_token_secret):
        self.threads = []#the list of threads
        '''
        
        #search handlers
        
        '''
        
        self.api = twitter.Api(consumer_key=consumer_key,
                        consumer_secret=consumer_secret,
                        access_token_key=serverKey,
                        access_token_secret=access_token_secret)
        
        
    def initUsername(self):
        self.username =  self.api.VerifyCredentials().screen_name    
        
    def run(self):
        self.setRunning(True)
        for t in self.threads:
            t.start()
            
        while self.running:
            try:
                time.sleep(10)
            except KeyboardInterrupt:
                self.debug('Got Key interrupt')
                self.setRunning(False)
                    
                sys.exit()
        return
    
    def addSearchHandler(self,search,func):
        t = Thread(target=self.searchHandler, args=(search,func))
        self.threads.append(t)
        return
    
    def addUserHandler(self,search,func):
        t = Thread(target=self.userHandler, args=(search,func))
        self.threads.append(t)
        return
    
    def getUsername(self):
        return self.username;
    
    def addMentionHandler(self,func,seconds=SLEEP_TIME):
        t = Thread(target=self.mentionsHandler, args=(func,seconds))
        self.threads.append(t)
        return
    
    def mentionsHandler(self,func,seconds):
        self.peridocCheck(self.api.GetMentions,func,seconds)
        return
    
    def peridocCheck(self,searchFunc,func,seconds):
        oldResults = searchFunc()

        while self.running:
            try:
                #get new results
                newResults = [];
                newResults =searchFunc()
                
                mentions = [];
                
                for newResult in newResults:
                    found = False;
                    for oldResult in oldResults:
                        if oldResult.id == newResult.id:
                            found = True;
                            break;
                        
                    if not found:
                        mentions.append(newResult)
                
                oldResults = newResults
                
                for tweet in mentions:
                    func(tweet)
            except URLError:
                self.debug("failed to pull url: URLError at peridocCheck")
            except:
                traceback.print_exc(file=sys.stdout)
                self.debug("failed to pull url: at peridocCheck")
            time.sleep(seconds)
        return
    
    def userHandler(self,search,func,seconds=SLEEP_TIME):
        userid = self.api.GetUser(search).id
        self.debug(userid)
        try:
            self.peridocCheck((lambda: self.api.GetUserTimeline(userid)),func,seconds)
        except ValueError:
            self.debug("Value Error on userHandler for "+ search)
        return
        
    def searchHandler(self,search,func,seconds=SLEEP_TIME):
        '''
        Thread function that handles a search and callback function when new result is found
        '''
        self.peridocCheck((lambda: self.api.GetSearch(search)),func,seconds)
        return


    def getTweetCount(self,user):
        return self.api.GetUser(user).statuses_count

    
    def addReminderDaemon(self):
        '''
        Add the daemon that checks if we have reminders comming up
        Returns the thread class, so we can send a close DB command on exceptions
        '''
        t=self.TweetReminder(self)
        self.threads.append(t)
        return t
    
    def onReply(self,tweet):
        '''
        Handles a mention to the bot
        '''
        self.debug(tweet.text)
        return
        
if __name__ == '__main__':

    a = Bot(serverKey,secret)
    a.initUsername()
    
    a.addMentionHandler(a.onReply)
    a.run()
    
