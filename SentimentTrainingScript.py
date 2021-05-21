import nltk
import random
from nltk.corpus import twitter_samples
from nltk.classify.scikitlearn import SklearnClassifier
import pickle
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from sklearn.linear_model import LogisticRegression, SGDClassifier
from sklearn.svm import LinearSVC
from nltk.tokenize import word_tokenize

# Loading in the twitter_samples corpus into positive and negative
positive_tweets = twitter_samples.strings('positive_tweets.json')
negative_tweets = twitter_samples.strings('negative_tweets.json')

# Create empty list to hold the words we want for analysis
all_words = []
# empty list to hold the words and the sentiment attached
documents = []

# Allowed word types J = adjective, R = adverb, V = verb
allowed_words = ["J", "R", "V"]

# For each instance in positive tweets tag as positive and add to documents, then tokenize the instance and filter by
# allowed word types, allowed words are added to all_words list.
for p in positive_tweets:
    documents.append((p, "pos"))
    word = word_tokenize(p)
    pos = nltk.pos_tag(word)
    for w in pos:
        if w[1][0] in allowed_words:
            all_words.append(w[0].lower())

# Same as above simply for negative tweet samples
for p in negative_tweets:
    documents.append((p, "neg"))
    word = word_tokenize(p)
    pos = nltk.pos_tag(word)
    for w in pos:
        if w[1][0] in allowed_words:
            all_words.append(w[0].lower())

# change all_words to hold the frequency distribution of the instances in all_words. This reduces duplication
all_words = nltk.FreqDist(all_words)

# word_features list holds all_words.keys which is each unique word from all_words
word_features = list(all_words.keys())

# Serialize the word features and save them as a file for use in sentiment mod
save_word_features = open("pickled-algorithms/word_features.pickle", "wb")
pickle.dump(word_features, save_word_features)
save_word_features.close()


# tokenize each tweet then for each feature in word_features check if the feature is in the tokenized tweet. If so
# add the feature to the features dict. Return the features dict. This format is required for the classifiers
def find_features(tweet):
    words = word_tokenize(tweet)
    features = {}
    for w in word_features:
        features[w] = (w in words)

    return features


# Using above method to create a new list called featuresets, this contains the features and the attached sentiment for
# each tweet instance
featuresets = [(find_features(tweet), sentiment) for (tweet, sentiment) in documents]
random.shuffle(featuresets)
print(len(featuresets))

# Split the featuresets up into a training and testing split of 80/20 since there are 10000 instances
testing_set = featuresets[8000:]
training_set = featuresets[:8000]

# Training the Naive Bayes algorithm using the training set, then printing out the accuracy and most informative
# features
classifier = nltk.NaiveBayesClassifier.train(training_set)
print("Original Naive Bayes Algo accuracy = ", (nltk.classify.accuracy(classifier, testing_set)) * 100, "%")
classifier.show_most_informative_features(15)

# Serializing and saving the trained algorithm for fast retrieval in sentiment mod.
save_classifier = open("pickled-algorithms/originalnaivebayes.pickle", "wb")
pickle.dump(classifier, save_classifier)
save_classifier.close()

# Training and saving the rest of the classifiers
MNB_classifier = SklearnClassifier(MultinomialNB())
MNB_classifier.train(training_set)
print("MNB_classifier accuracy = ", (nltk.classify.accuracy(MNB_classifier, testing_set)) * 100, "%")

save_classifier = open("pickled-algorithms/MNB_classifier.pickle", "wb")
pickle.dump(MNB_classifier, save_classifier)
save_classifier.close()

BernoulliNB_classifier = SklearnClassifier(BernoulliNB())
BernoulliNB_classifier.train(training_set)
print("BernoulliNB_classifier accuracy = ", (nltk.classify.accuracy(BernoulliNB_classifier, testing_set)) * 100, "%")

save_classifier = open("pickled-algorithms/BernoulliNB_classifier.pickle", "wb")
pickle.dump(BernoulliNB_classifier, save_classifier)
save_classifier.close()

LogisticRegression_classifier = SklearnClassifier(LogisticRegression(max_iter=200))
LogisticRegression_classifier.train(training_set)
print("LogisticRegression_classifier accuracy = ",
      (nltk.classify.accuracy(LogisticRegression_classifier, testing_set)) * 100, "%")

save_classifier = open("pickled-algorithms/LogisticRegression_classifier.pickle", "wb")
pickle.dump(LogisticRegression_classifier, save_classifier)
save_classifier.close()

LinearSVC_classifier = SklearnClassifier(LinearSVC())
LinearSVC_classifier.train(training_set)
print("LinearSVC_classifier accuracy = ", (nltk.classify.accuracy(LinearSVC_classifier, testing_set)) * 100, "%")

save_classifier = open("pickled-algorithms/LinearSVC_classifier.pickle", "wb")
pickle.dump(LinearSVC_classifier, save_classifier)
save_classifier.close()


SGDC_classifier = SklearnClassifier(SGDClassifier())
SGDC_classifier.train(training_set)
print("SGDClassifier accuracy = ", nltk.classify.accuracy(SGDC_classifier, testing_set) * 100, "%")

save_classifier = open("pickled-algorithms/SGDC_classifier.pickle", "wb")
pickle.dump(SGDC_classifier, save_classifier)
save_classifier.close()
