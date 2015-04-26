#!/usr/bin/env python
# encoding: utf-8
"""
Twitter bot fixing English by following the lead of GIF.
"""
from __future__ import print_function, unicode_literals
import argparse
import random
import re
import sys
import twitter
import webbrowser
import yaml

TWITTER = None


def print_it(text):
    """ cmd.exe cannot do Unicode so encode first """
    print(text.encode('utf-8'))


def load_yaml(filename):
    """
    File should contain:
    consumer_key: TODO_ENTER_YOURS
    consumer_secret: TODO_ENTER_YOURS
    access_token: TODO_ENTER_YOURS
    access_token_secret: TODO_ENTER_YOURS
    """
    f = open(filename)
    data = yaml.safe_load(f)
    f.close()
    if not data.viewkeys() >= {
            'access_token', 'access_token',
            'consumer_key', 'consumer_secret'}:
        sys.exit("Twitter credentials missing from YAML: " + filename)
    return data


def tweet_it(string, credentials):
    """ Tweet string using credentials """
    global TWITTER
    if len(string) <= 0:
        return

    # Create and authorise an app with (read and) write access at:
    # https://dev.twitter.com/apps/new
    # Store credentials in YAML file
    if TWITTER is None:
        TWITTER = twitter.Twitter(auth=twitter.OAuth(
            credentials['access_token'],
            credentials['access_token_secret'],
            credentials['consumer_key'],
            credentials['consumer_secret']))

    print_it("TWEETING THIS:\n" + string)

    if args.test:
        print("(Test mode, not actually tweeting)")
    else:
        result = TWITTER.statuses.update(status=string)
        url = "http://twitter.com/" + \
            result['user']['screen_name'] + "/status/" + result['id_str']
        print("Tweeted:\n" + url)
        if not args.no_web:
            webbrowser.open(url, new=2)  # 2 = open in a new tab, if possible


def random_line(afile):
    """
    Based on algorithm R(3.4.2) (Waterman's "Reservoir Algorithm") from
    Knuth's "The Art of Computer Programming"
    """
    line = next(afile)
    for num, aline in enumerate(afile):
        if random.randrange(num + 2):
            continue
        line = aline
    return line


def hardg(gwords):
    """ Pick a random word and find its correct pronunciation """
    print("Pick a random word...")
    # This file is based on:
    # http://svn.code.sf.net/p/cmusphinx/code/trunk/cmudict/cmudict-0.7b
    with open(gwords) as afile:
        word = random_line(afile).strip()
    print_it(word)

    correct_pronounciation = "j" + word[1:]
    print_it(correct_pronounciation)
    return word, correct_pronounciation


def get_a_tweet(query, credentials):
    global TWITTER
    if TWITTER is None:
        TWITTER = twitter.Twitter(auth=twitter.OAuth(
            credentials['access_token'],
            credentials['access_token_secret'],
            credentials['consumer_key'],
            credentials['consumer_secret']))

    tweets = TWITTER.search.tweets(q=query, count=100)['statuses']

    kept = []
    print("Tweets found:", len(tweets))
    for tweet in tweets:
        text = tweet['text']
        if "@" in text:
            continue  # No spamming
        kept.append(text)

    print("Tweets kept:", len(kept))
    if kept:
        rando = random.choice(kept)
        print_it(rando)
        return rando

    # Nothing found
    return None


def fix_tweet(tweet, word, correct_pronounciation):
    """ In tweet, replace gif with word and jif with correct_pronounciation """

    # Caps
    tweet = re.sub("GIF", word.upper(), tweet)
    tweet = re.sub("JIF", correct_pronounciation.upper(), tweet)

    # Initial
    tweet = re.sub("Gif", word.title(), tweet)
    tweet = re.sub("Jif", correct_pronounciation.title(), tweet)

    # Lower case, mixed case
    tweet = re.sub("gif", word, tweet, flags=re.I)
    tweet = re.sub("jif", correct_pronounciation, tweet, flags=re.I)

    return tweet


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Twitter bot fixing English by following the lead of GIF.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-g', '--gwords',
        default='/Users/hugo/Dropbox/bin/data/hard-g-words.txt',
        help="File containing a list of words mistakenly pronounced with "
             "a hard G")
    parser.add_argument(
        '-y', '--yaml',
        default='/Users/hugo/Dropbox/bin/data/jifbot.yaml',
        help="YAML file location containing Twitter keys and secrets")
    parser.add_argument(
        '-nw', '--no-web', action='store_true',
        help="Don't open a web browser to show the tweeted tweet")
    parser.add_argument(
        '-x', '--test', action='store_true',
        help="Test mode: go through the motions but don't tweet anything")
    args = parser.parse_args()

    credentials = load_yaml(args.yaml)

    word, correct_pronounciation = hardg(args.gwords)

    print("Find a tweet...")
    tweet = get_a_tweet("gif jif", credentials)
    if not tweet:
        sys.exit("No tweet found, maybe next time.")
    tweet = fix_tweet(tweet, word, correct_pronounciation)

    tweet_it(tweet, credentials)

# End of file
