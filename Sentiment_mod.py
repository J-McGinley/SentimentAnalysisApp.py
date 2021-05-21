import os
import pickle
import sys
from nltk.classify import ClassifierI
from statistics import mode
from nltk.tokenize import word_tokenize


# Application is bundled using pyinstaller, therefore the resource path must point to sys._MEIPASS\relative_path
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


# Voted classifier class which takes classifiers on initiation
class VotedClassifier(ClassifierI):
    def __init__(self, *classifiers):
        self._classifiers = classifiers

    # Method for classifying the data, takes features as input and the for each classifier it assigns a vote
    # Each vote is appended to the votes list and the mode is returned
    def classify(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)
        return mode(votes)

    # Method for determining the confidence level of the voted classification, it has same logic as above but once the
    # votes list is created the mode is counted then divided by the total. This gives us the mode over total. i.e. if
    # 5/6 say pos then confidence is rounded down to 80%
    def confidence(self, features):
        votes = []
        for c in self._classifiers:
            v = c.classify(features)
            votes.append(v)

        choice_votes = votes.count(mode(votes))
        conf = choice_votes / len(votes)
        return round(conf, 2)


# Loading the serialized documents into variables for use in the sentiment mod
wordFeaturesPath = resource_path(os.path.dirname(os.path.abspath(__file__))) + "\\pickled-algorithms\\word_features.pickle"
word_features5k_f = open(wordFeaturesPath, "rb")
word_features = pickle.load(word_features5k_f)
word_features5k_f.close()


classifierPath = resource_path(os.path.dirname(os.path.abspath(__file__))) + "\\pickled-algorithms\\originalnaivebayes.pickle"
open_file = open(classifierPath, "rb")
NaiveBayes_classifier = pickle.load(open_file)
open_file.close()

mnbClassifierPath = resource_path(os.path.dirname(os.path.abspath(__file__))) + "\\pickled-algorithms\\MNB_classifier.pickle"
open_file = open(mnbClassifierPath, "rb")
MNB_classifier = pickle.load(open_file)
open_file.close()

BernoulliNbClassifierPath = resource_path(os.path.dirname(os.path.abspath(__file__))) + "\\pickled-algorithms\\BernoulliNB_classifier.pickle"
open_file = open(BernoulliNbClassifierPath, "rb")
BernoulliNB_classifier = pickle.load(open_file)
open_file.close()

LogisticRegressionClassifierPath = resource_path(os.path.dirname(os.path.abspath(__file__))) + "\\pickled-algorithms\\LogisticRegression_classifier.pickle"
open_file = open(LogisticRegressionClassifierPath, "rb")
LogisticRegression_classifier = pickle.load(open_file)
open_file.close()


LinearSvcClassifierPath = resource_path(os.path.dirname(os.path.abspath(__file__))) + "\\pickled-algorithms\\LinearSVC_classifier.pickle"
open_file = open(LinearSvcClassifierPath, "rb")
LinearSVC_classifier = pickle.load(open_file)
open_file.close()

SgdcClassifierPath = resource_path(os.path.dirname(os.path.abspath(__file__))) + "\\pickled-algorithms\\SGDC_classifier.pickle"
open_file = open(SgdcClassifierPath, "rb")
SGDC_classifier = pickle.load(open_file)
open_file.close()

# Initializing an instance of the VotedClassifier class
voted_classifier = VotedClassifier(
                                  NaiveBayes_classifier,
                                  MNB_classifier,
                                  BernoulliNB_classifier,
                                  LogisticRegression_classifier,
                                  LinearSVC_classifier,
                                  SGDC_classifier)


# Find features method same as in sentiment training script, simply matches tokenized instances in a tweet
# to instances in word_features file. If they match then the features are returned
def find_features(tweet):
    words = word_tokenize(tweet)
    features = {}
    for w in word_features:
        features[w] = (w in words)
    return features


# Sentiment method. This implements the find features method, then takes the features and runs them through the
# voted classifier classify and confidence methods.
def sentiment(tweet):
    features = find_features(tweet)
    return voted_classifier.classify(features), voted_classifier.confidence(features)
