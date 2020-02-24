#!/usr/bin/python3
__author__ = 'young_30'

import re
import pinyin
from collections import Counter
from functools import lru_cache

file_path = 'data_sets/article_9k.txt'


class PinyinCouter:
    """Provide the operations to counter in Chinese-Pinyin."""
    def __init__(self, dataset, counters={}):
        """Create the obj with two attributes.

        :param dataset: The file path
        :param counter: Defaul couter by a blank dict
        """
        self._dataset = dataset
        self._counter = counters

    @property
    def get_counter(self):
        return self._counter

    def read_file(self):
        with open(self._dataset, encoding='utf-8-sig') as f:
            CHINESE_CHARATERS = f.read()
        filter_list = re.findall('[^[a-zA-Z0-9]+', CHINESE_CHARATERS.replace('\n', ""))
        filter_text = "".join(filter_list)
        return filter_text  # you can try filter_text[:100000] to increase the spped, but sacrify a bit accuracy

    @property
    def pinyin_pair(self):
        return pinyin.get(self.read_file(), format="strip", delimiter=" ")

    def pinyin_counter(self):
        pinyin_list = self.pinyin_pair.split(" ")
        self._counter = Counter(pinyin_list)

    def expand_counter(self, n):
        """Expand the counter to 2-gram, 3-gram, 4-gram... till n-gram.

        :param n: the ngram model number
        :return: a final big counter
        """
        final_counter = Counter()
        for i in range(2, n+1):
            expand_list = generate_ngrams(self.pinyin_pair, i)
            final_counter += Counter(expand_list)
        return self.get_counter + final_counter


class EditDistance:
    """Provide the operation to calculate the edit distance.

    :Attribute alphabet: the Letter string between a-z.
    """
    alphabet = 'abcdefghijklmnopqrstuvwxyz'
    def __init__(self):
        pass

    def edits0(self, word):
        """Return all strings that are zero edits away from word (i.e., just word itself)."""
        return {word}

    def edits2(self, word):
        """Return all strings that are two edits away from this pinyin."""
        return {e2 for e1 in self.edits1(word) for e2 in self.edits1(e1)}

    def edits3(self, word):
        """Return all strings that are three edits away from this pinyin."""
        return {e3 for e2 in self.edits2(word) for e3 in self.edits1(e2)}

    def edits1(self, word):
        """Return all strings that are one edit away from this pintin"""
        pairs = self.splits(word)
        deletes = EditDistance.get_deletes(pairs)
        transposes = EditDistance.get_transposes(pairs)
        replaces = EditDistance.get_replaces(pairs)
        inserts = EditDistance.get_inserts(pairs)
        return set(deletes + transposes + replaces + inserts)

    @staticmethod
    def get_deletes(pairs):
        return [a + b[1:] for (a, b) in pairs if b]

    @staticmethod
    def get_transposes(pairs):
        return [a + b[1] + b[0] + b[2:] for (a, b) in pairs if len(b) > 1]

    @staticmethod
    def get_replaces(pairs):
        return [a + c + b[1:] for (a, b) in pairs for c in EditDistance.alphabet if b]

    @staticmethod
    def get_inserts(pairs):
        return [a + c + b for (a, b) in pairs for c in EditDistance.alphabet]

    def splits(self, word):
        """Return a list of all possible (first, rest) pairs that comprise pinyin."""
        return [(word[:i], word[i:]) for i in range(len(word) + 1)]


def generate_ngrams(sentence, n):
    """Build the ngram model by two different method.
       Fun1: Use the zip function to help us generate n-grams (faster)
       Fun2: Use List generation (slower)

    :param sentence: the initial string
    :param n: gram model number
    :return:
    """
    # length = len(sentence.split(" "))
    tokens = [token for token in sentence.split(" ") if token != ""]
    ngrams = zip(*[tokens[i:] for i in range(n)])
    # ngrams = [tokens[i: n+i] for i in range(length) if n+i <= length]
    return ["".join(ngram) for ngram in ngrams]


def known(words, counter):
    """Find the words exit in counter.

    :param words: should be a list
    :param counter: background counter
    :Return: the pinyin words we have noticed.
    """
    return {w for w in words if w in counter}


def correct(word, counter, ed):
    """Find the most possible pinyin based on edit distance.

    :param word: The incorrect sentence or word
    :param counter: The base counter data to correct the word
    :param ed: The EditDistance obj
    :return: A most likely word after correction
    """
    # Prefer edit distance 0, then 1, then 2; otherwise default to word itself.
    candidates = (known(ed.edits0(word), counter) or
                  known(ed.edits1(word), counter) or
                  known(ed.edits2(word), counter) or
                  [word]
                  )
    return max(candidates, key=counter.get)  # return the most possible

# To split the string after correction
def P(string_list, counter, default=0):
    """Get the probability of a list of strings depend on Thesaurus.

    :param string_list: The origin semantics list
    :param default: The origin probability
    :param count: The Couter for search
    :return: A chance number less than 1
    """
    probility = 1
    for token in string_list:
        if token not in counter:
            probility *= default
        else:
            probility *= counter.get(token) / sum(counter.values())
    return probility


# some global variables
notes = []
split_solutions = {}

count1 = PinyinCouter(file_path)
count1.pinyin_counter()
counter = count1.get_counter


@lru_cache(maxsize=2 ** 10)
def best_split(string):
    """split a string to a few words into the dict according to the max probability.

    :param string: the phrase to be cut
    :return: the most likely percentage
    """
    # global counter
    # global notes
    # global split_solutions
    notes = [(P([string], counter), '', string)] + [(best_split(string[:i]) * best_split(string[i:]),
                                                     string[:i], string[i:]) for i in range(1, len(string))]
    prob, left, right = max(notes, key=lambda x: x[0])

    split_solutions[string] = (left, right)
    return prob


def parse_split_solution(string):
    """Operate the split function.

    :param string: the phrase without splitting
    :return: a complete phrase after split
    """
    left, right = split_solutions[string]
    if not left: return [right]
    return parse_split_solution(left) + parse_split_solution(right)


def mixin(demo, max_counter, edit_op):
    """Integrate the correction and split operation.

    :param demo: the original phrase
    :param max_counter: the background counter
    :param edit_op: param for correct function
    :return: the final right phrase
    """
    fix_text = correct(demo, max_counter, edit_op)
    prob = best_split(fix_text)
    return parse_split_solution(fix_text)


def main():
    edit_op = EditDistance()
    final_counter = count1.expand_counter(4)

    # testing the function
    sample1 = "qignhuadaxeu"    # "清华大学"
    sample2 = "zhesihyiege"     # "这是一个"
    correct_sample1 = mixin(sample1, final_counter, edit_op)
    correct_sample2 = mixin(sample2, final_counter, edit_op)
    print(correct_sample1)
    print(correct_sample2)


if __name__ == '__main__':
    main()
