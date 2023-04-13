from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

flaggedPosts = [{'url':"example", 'rawContent':"this is a tweet 1"}, {'url': "example", 'rawContent': "this is a tweet 2"}, {'url':"example", 'rawContent': "this is a tweet 3"}]
score = 53

@app.route('/', methods=['GET', 'POST'])#home page
def first():
    return render_template('home.html')

@app.route('/select', methods=['GET', 'POST']) #pick which type of check
def select():
    return render_template('start.html')

@app.route('/login', methods=['GET', 'POST']) #gets login
def login():
    return render_template("login.html")

@app.route('/promptText', methods=['GET', 'POST']) #get text input
def getText():
    return render_template('getText.html')

@app.route('/next', methods=['GET', 'POST']) #alternate login page
def next():
    if request.method == "POST":
        text = request.form.get("textInput")
        f = open("someText.txt", "w")
        f.write(text)
        f.close()
        return render_template('login.html')

@app.route('/clause', methods=['GET', 'POST']) #displays consent clause
def clause():
    if request.method == "POST":
        username = request.form.get("uname")
        return render_template('clause.html')

@app.route('/proceed') #displays results
def proceed():
        return render_template('proceed.html', score = score, len = len(flaggedPosts), flaggedPosts = flaggedPosts) 

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

