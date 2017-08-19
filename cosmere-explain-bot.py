# A Reddit bot that posts a summary of each Cosmere novel each time it is mentioned
# The summary is extracted from Coppermind.net

from bs4 import BeautifulSoup
from urllib.parse import urlparse

import praw
import time
import re
import requests
import bs4

path = '/Users/sanfengwang/Documents/GitHub/cosmereBot/visited.txt'
# Location of file where id's of already visited comments are maintained

header = "**This Novel's Placement in the Cosmere:**\n"
footer = '\n*---This summary was extracted from [Coppermind.net](http://coppermind.net)---*'


def authenticate():
    
    print('Authenticating...\n')
    reddit = praw.Reddit("copperbot",
                user_agent = 'web:cosmere-placement-bot:v0.1')
    print('Authenticated as {}\n'.format(reddit.user.me()))
    return reddit


def fetchdata(url):

    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')

    tag = soup.find('p')
    data = ''
    while True:
        if isinstance(tag, bs4.element.Tag):
            if (tag.name == 'div'):
                break
            else:
                data = data + '\n' + tag.text
                tag = tag.nextSibling
        else:
            tag = tag.nextSibling
    
    return data


def run_explainbot(reddit):

    booksWithThe = ["Final Empire", "Well of Ascension", "Hero of Ages", \
        "Alloy of Law", "Bands of Mourning", "Lost Metal", "Emperor's Soul", \
        "Way of Kings",  ]
    booksWithoutThe = ["Elantris", "Shadows of Self", "Warbreaker", \
    "Shadows for Silence in the Forests of Hell", "Sixth of the Dusk", "Secret History", \
    "Arcanum Unbounded", "White Sand", "Words of Radiance", "Oathbringer"]
    bookList = [booksWithThe, booksWithoutThe]
    
    print("Getting 250 comments...\n")
    
    for comment in reddit.subreddit('test').comments(limit = 250):

        for sublist in bookList:
            for title in sublist:
                if title in comment.body:
                    print(title + 'mentioned in comment with comment ID: ' + comment.id)
                    words = title.split()
                    if sublist == booksWithThe:
                        myurl = 'http://coppermind.net/wiki/The'
                        for word in words:
                            myurl = myurl + '_' + word
                    else:
                        myurl = 'http://coppermind.net/wiki/' + words[0]
                        for word in words[1:]:
                            myurl = myurl + '_' + word
                    file_obj_r = open(path,'r')
                                
                    try:
                        explanation = fetchdata(myurl)
                    except:
                        print('Exception!!! Page for novel does not exist\n')
                    else:
                        if comment.id not in file_obj_r.read().splitlines():
                            print('Link is unique...posting explanation\n')
                            comment.reply(header + explanation + footer)
                            
                            file_obj_r.close()

                            file_obj_w = open(path,'a+')
                            file_obj_w.write(comment.id + '\n')
                            file_obj_w.close()
                        else:
                            print('Already visited comment...no reply needed\n')
                else:
                    print("Comment does not contain a Cosmere novel")
            
            time.sleep(10)

    print('Waiting 60 seconds...\n')
    time.sleep(60)


def main():
    reddit = authenticate()
    while True:
        run_explainbot(reddit)


if __name__ == '__main__':
    main()