from slackbot.bot import Bot
from slackbot.bot import respond_to
import random
import cStringIO
import traceback
import string
import re
import sys
import json
import urllib2


def main():
    # Open the corpus indicated in cmd line
    try:
        markov_file = open(sys.argv[1])
    except:
        print("Please include the corpus file.")
        return

    # Generate Markov text
    global markov_obj

    markov_obj = Markov(markov_file)

    # Send the markov data to the Slackbot
    bot = Bot()
    bot.run()

@respond_to('cyber', re.IGNORECASE)
# Listens for the word 'cyber'
def cyber(message):

    # Indicate success on the termial
    print ("response successful")

    # Generate Markov text
    global markov_obj

    try:
        # Attempt to reply to the message, but if not the program
        # doesn't crash and burn
        message.reply(message.reply(markov_obj.generate_markov_text()))
    except:
        pass


class Markov(object):

    def __init__(self, open_file):
        # Initialize class
        self.cache = {}
        self.open_file = open_file
        self.words = self.file_to_words()
        self.word_size = len(self.words)
        self.database()


    def file_to_words(self):
        # Open and split the corpus
        self.open_file.seek(0)
        data = self.open_file.read()
        words = data.split()
        return words


    def triples(self):
        # This generates triples from strings in the corpus.

        # Skip if the string has less than 3 words.
        if len(self.words) < 3:
            return

        # Generate
        for i in range(len(self.words) - 2):
            yield (self.words[i], self.words[i+1], self.words[i+2])

    def database(self):
        for w1, w2, w3 in self.triples():
            key = (w1, w2)
            if key in self.cache:
                self.cache[key].append(w3)
            else:
                self.cache[key] = [w3]

    def generate_markov_text(self, size=10):
        # debug variable
        TEST = 0

        if TEST == 1:
            print ("I'm trying to generate markov txt")

        seed = random.randint(0, self.word_size-3)
        seed_word, next_word = self.words[seed], self.words[seed+1]
        w1, w2 = seed_word, next_word
        gen_words = []
        i = 0
        gen_words.append(w1)
        #skip to next sentence to avoid fragmented beginnings.
        while (not (gen_words[len(gen_words)-1].endswith("."))):
                w1, w2 = w2, random.choice(self.cache[(w1, w2)])
                gen_words.append(w1)
        #now clear for the next bit.
        del gen_words[:]
        w1, w2 = w2, random.choice(self.cache[(w1, w2)])
        gen_words.append(w1)
        #now build the thing for real.
        while (not (gen_words[len(gen_words)-1].endswith("."))) or i < size:
            if (w1, w2) in self.cache:
                w1, w2 = w2, random.choice(self.cache[(w1, w2)])
                gen_words.append(w1)
                i += 1
            else:
                if TEST == 1:
                    print ("I'm still in test mode.")

                possible_next_word = []
                for i in xrange(len(self.words)):
                    if unicode(w1.lower()) == unicode(self.words[i].lower()):
                        possible_next_word.append(i)
                w2 = self.words[random.choice(possible_next_word)+1]
                gen_words.append(w1)
                i += 1

        if(sum(len(letters) for letters in gen_words) < 300):
            return ' '.join(gen_words)
        else:
            return self.generate_markov_text()

if __name__ == "__main__":
    main()
