=from datetime import datetime, timedelta as td
from flask import Flask, render_template, request, redirect
import gspread as gs

app = Flask(__name__)

# Assuming your credentials file is named 'gcredentials.json'
try:
    gc = gs.service_account(filename='gcredentials.json')
except FileNotFoundError:
    print("Error: 'gcredentials.json' not found.)
    exit(1)

try:
    ss = gc.open_by_key('key_id')
except Exception as e:
    print(f"Error opening spreadsheet: {e}")
    exit(1)

ws = ss.sheet1


class Tweet:
    def __init__(self, message, time, done, row_idx):
        self.message = message
        self.time = time
        self.done = done
        self.row_idx = row_idx


def date(date_time):
    o = None
    error_code = None
    try:
        o = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
    except ValueError as e:
        error_code = f'Error!{e}'
    if o is not None:
        now_time = datetime.utcnow() + td(hours=5, minutes=30)  # Corrected typo (utcnow instead of uctnow)
        if o < now_time:
            error_code = "time is already passed!"
    return o, error_code


@app.route('/')
def tweet_list():
    try:
        tr = ws.get_all_records()
        tweets = []
        for idx, tweet in enumerate(tr, start=2):
            tweet = Tweet(**tweet, row_idx=idx)
            tweets.append(tweet)
            tweets.reverse()
        ot = sum(1 for tweet in tweets if not tweet.done)
        return render_template('base.html', tweets=tweets, n_open_tweets=ot)
    except Exception as e:
        print(f"Error fetching tweets: {e}")
        return "Error fetching tweets", 500  # Return error message and status code


@app.route('/add_tweet', methods=['POST'])
def add_tweet():
    msg = request.form['message']
    if not msg:
        return 'you have not entered the message!'
    if len(msg) > 280:  # Corrected typo (closing parenthesis)
        return 'you exceeded the word count!'
    time = request.form['time']
    if not time:
        return "you have not entered the time"
    o, error_code = date(time)
    if error_code is not None:
        return error_code
    x = [str(o), msg, 0]
    ws.append_row(x)
    return redirect('/')
@app.route('/delete/<int:row_idx>',)
def delete_tweet(row_idx):
    ws.delete_rows(row_idx)
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
