#libraries

import json
import os
import string
import time
import re
import sys

import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords
stop = set(stopwords.words('english'))
nltk.download('punkt')
from nltk.tokenize import word_tokenize

from flask import Flask, render_template, request, redirect, url_for

#global lists

allTweets = [] #stores all of the relevant fields for each post here
textContent = [] #stores just the text content of the posts
locations = [] #stores the index of the flagged posts
termsFound = [] #stores all offensive terms found in bow analysis
terms = [] #the dataset vocabularly is stored here
flaggedPosts = [] #flagged posts are stored in here

username = "default"
choice = 1
anythingFound = True
userScore = 0
final = False

#flask code

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])#home page
def first():
    return render_template('home.html')

@app.route('/select', methods=['GET', 'POST']) #pick which type of check
def select():
    return render_template('start.html')

@app.route('/login', methods=['GET', 'POST']) #gets login
def login():
    global choice
    choice = 1
    print("workplace check selected")
    return render_template("login.html")

@app.route('/promptText', methods=['GET', 'POST']) #get text input
def getText():
    global choice
    choice = 2
    print("security check selected")
    return render_template('getText.html')

@app.route('/next', methods=['GET', 'POST']) #alternate login page
def next():
    if request.method == "POST":
        text = request.form.get("textInput")
        spr = text.split()
        f = open("userChoice.txt", "w")
        for a in spr:
            f.write(a + "\n")
        f.close()
        return render_template('login.html')

@app.route('/clause', methods=['GET', 'POST']) #displays consent clause
def clause():
    global username
    if request.method == "POST":
        username = request.form.get("uname")
        main(username)
        return render_template('clause.html')

@app.route('/proceed') #displays results
def proceed():
    print(userScore)
    print(flaggedPosts)
    return render_template('proceed.html', score = userScore, len = len(flaggedPosts), flaggedPosts = flaggedPosts)

@app.route('/exit')
def exit():
    remove()
    return render_template('home.html')
 
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

#BOW and NLP code

def remove():
    global username
    global choice
    global anythingFound
    global userScore
    global final
    global allTweets
    global textContent
    global locations
    global termsFound
    global terms
    global flaggedPosts
    flaggedPosts = []
    username = "default"
    choice = 1
    anythingFound = True
    userScore = 0
    final = False
    allTweets = []
    textContent = []
    locations = []
    termsFound = []
    terms = []

def shut(): #to terminate the program
    time.sleep(3)
    print("Shutting down")
    sys.exit()

def scrape(username): #use scraping API to retrieve tweets
    command1 = "snscrape --jsonl --max-results 1000 twitter-search 'from:"
    command2 = "'> posts.json"
    allCommand = command1 + username + command2
    print(allCommand)
    os.system(allCommand)

def getData(): #get the necessary fields for the posts from the json file
    global textContent
    global allTweets
    with open('posts.json') as f: #open json file linked to the username
        for line in f: #iterates through each json object at a time
            d = {
                'url' : 'x',
                'rawContent' : 'x',
                'tID' : 0,
                'username' : 'x'
            } #the dictionary in which essential info about each tweet will be stored
            #fields needed include url, rawContent, id, username            
            data = json.loads(line)
            d['url'] = data['url']
            d['rawContent'] = data['rawContent']
            d['tID'] = data['id']
            d['username'] = data['username']

            #gets essential data from each json object/tweet
            current = data['rawContent']
            textContent.append(current)#adds data to list to be referred to later      
            allTweets.append(d)
    f.close()

def openDoc(choice): #open the correct set of terms
    global terms
    if choice == 1:
        print(choice)
        f = open("profanities.txt", "r").read().split('\n')
    if choice == 2:
        print(choice)
        f = open("userChoice.txt", "r").read().split('\n')
    for i in f:
        terms.append(i)
    
def removeLinks(posts): #remove links from a post
    newPosts = []
    for s in posts:
        x = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', " ", s).split()
        x= ' '.join(x)
        newPosts.append(x)
    return newPosts

def removeEmoji(posts): #remove emojis from a post
    newPosts = []
    for s in posts:
        x = s.encode('ascii', 'ignore').decode('ascii')
        newPosts.append(x)
    return newPosts

def removeNumbers(posts): #remove numbers from a post
    newPosts = []
    for s in posts:
        x = re.sub(r'[0-9]+', '', s)
        newPosts.append(x)
    return newPosts

def removePuncLower(posts): #removes punctuation and lowers all characters
    newPosts = []
    for s in posts:
        x = s.lower().translate(str.maketrans('', '', string.punctuation))
        newPosts.append(x)
    return newPosts

def removeStop(posts): #removes stop words
    newPosts = []
    for s in posts:
        x = ' '.join([word for word in s.split() if word not in stop])
        newPosts.append(x)
    return newPosts

def tokeniseIt(posts): #tokenises the strings
    newPosts = []
    for s in posts:
        x = word_tokenize(s)
        newPosts.append(x)
    return newPosts

def bowUse(posts): #bag of words representation of the document
    bow = {}
    for s in posts:
        words = s #the current tokenised post is stored here
        for i in words: #iterates over each word in list
            if i in bow:
                bow[i] = bow[i] + 1
            else:
                bow[i] = 1
    return bow

def calculate(model): #spits out a score based on how many profanities found
    global termsFound
    score = 0
    for key in model: #needs to iterate through bow
        if (key in terms) and (model[key] == 1): #if that item is in terms then...
            score += 1
            termsFound.append(key)
        elif (key in terms) and (model[key] == 2):
            score += 1.5
            termsFound.append(key)
        elif (key in terms) and (model[key] >= 3):
            score += 2
            termsFound.append(key)
    return score

def locate(posts): #find the posts with the offensive terms
    global anythingFound
    global termsFound
    global locations
    count = 0
    if termsFound: #if array has elements should proceed
        for s in posts:
            words = s #current tokenised post is stored here
            for i in words:
                if i in termsFound:
                    locations.append(count)#adds the index of the post to be located later on
                    break
            count += 1 #index variable
    else: #if array is empty then should proceed here
        print("No flagged posts found")
        anythingFound = False
        
def display(): #get the relevant fields of the flagged posts
    global flaggedPosts
    global anythingFound
    global locations
    global allTweets
    count = len(locations)
    if anythingFound == True:
        for i in range(count):
            x = locations[i]
            y = allTweets[x]
            flaggedPosts.append(y)
    else:
        flaggedPosts.append('No terms found')

def clean(): #remove posts that have been processed
    global choice
    os.system("rm posts.json")
    if choice == 2:
        os.system("rm userChoice.txt")

def main(inp): #where all data is proceeded
    scrape(inp)
    getData()
    openDoc(choice)
    processedData = removeLinks(textContent)
    processedData = removePuncLower(processedData)
    processedData = removeNumbers(processedData)
    processedData = removeEmoji(processedData)
    processedData = removeStop(processedData)
    processedData = tokeniseIt(processedData)

    bowRep = bowUse(processedData)
    global userScore
    userScore = calculate(bowRep)
    locate(processedData)
    
    display()
    clean()
