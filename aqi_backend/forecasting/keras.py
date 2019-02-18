from __future__ import print_function
from functools import reduce
import re

import numpy as np

from keras.utils.data_utils import get_file
from keras.layers.embeddings import Embedding
from keras import layers
from keras.layers import recurrent
from keras.models import Model
from keras.preprocessing.sequence import pad_sequences

from epa_data.models import (
  COHourly, Pm10Hourly, Pm25Hourly, TemparatureHourly, HumidityHourly,
  WindHourly, AtmosphericPressureHourly)
from epa_data.constants import COMMAND_MODEL_MAP


# def serialize_aqdata_t(**aqargs):
#     '''Return the tokens of a sentence including punctuation.
#     >>> tokenize('Bob dropped the apple. Where is the apple?')
#     ['Bob', 'dropped', 'the', 'apple', '.', 'Where', 'is', 'the', 'apple', '?']
#     '''
#     return [x.strip() for x in re.split(r'(\W+)?', sent) if x.strip()]


def get_time_series(
        year_start, year_end, sites, input_params=COMMAND_MODEL_MAP,
        frequence="hourly"):
    '''Given a file name, read the file, retrieve the stories,
    and then convert the sentences into a single story.
    If max_length is supplied,
    any stories longer than max_length tokens will be discarded.
    '''
    data = []
    for year in range(year_start, year_end):
        print("year", year)
        year_data = {}
        for aq_model_name, aq_model in input_params:
            model_yearly_data = aq_model.objects.filter(
                date_local__year=year, site_num=sites).order_by(
                'date_local', 'time_local')
            print("================\n", aq_model_name)
            print(len(model_yearly_data))
            for t in model_yearly_data:
                if str(t.date_local) not in year_data.keys():
                    year_data[str(t.date_local)] = {}
                # print(str(t.date_local))
                if str(t.time_local) not in year_data[str(t.date_local)].keys():
                    year_data[str(t.date_local)][str(t.time_local)] = []
                # print(str(t.time_local))
                year_data[str(t.date_local)][str(t.time_local)].append(
                    t.min_format)
                # print(year_data)

        for date, date_v in year_data.items():
            for time, time_v in date_v.items():
                data.append([date, time, *time_v])
    print(len(data))
    return data


# def vectorize_stories(data, word_idx, story_maxlen, query_maxlen):
#     xs = []
#     xqs = []
#     ys = []
#     for story, query, answer in data:
#         x = [word_idx[w] for w in story]
#         xq = [word_idx[w] for w in query]
#         # let's not forget that index 0 is reserved
#         y = np.zeros(len(word_idx) + 1)
#         y[word_idx[answer]] = 1
#         xs.append(x)
#         xqs.append(xq)
#         ys.append(y)
#     return (pad_sequences(xs, maxlen=story_maxlen),
#             pad_sequences(xqs, maxlen=query_maxlen), np.array(ys))


# RNN = recurrent.LSTM
# EMBED_HIDDEN_SIZE = 50
# SENT_HIDDEN_SIZE = 100
# QUERY_HIDDEN_SIZE = 100
# BATCH_SIZE = 32
# EPOCHS = 20
# print('RNN / Embed / Sent / Query = {}, {}, {}, {}'.format(RNN,
#                                                            EMBED_HIDDEN_SIZE,
#                                                            SENT_HIDDEN_SIZE,
#                                                            QUERY_HIDDEN_SIZE))


# Default QA1 with 1000 samples
# challenge = 'tasks_1-20_v1-2/en/qa1_single-supporting-fact_{}.txt'
# QA1 with 10,000 samples
# challenge = 'tasks_1-20_v1-2/en-10k/qa1_single-supporting-fact_{}.txt'
# QA2 with 1000 samples
# challenge = 'tasks_1-20_v1-2/en/qa2_two-supporting-facts_{}.txt'
# QA2 with 10,000 samples
# challenge = 'tasks_1-20_v1-2/en-10k/qa2_two-supporting-facts_{}.txt'
# with tarfile.open(path) as tar:
#     train = get_stories(tar.extractfile(challenge.format('train')))
#     test = get_stories(tar.extractfile(challenge.format('test')))

# vocab = set()
# for story, q, answer in train + test:
#     vocab |= set(story + q + [answer])
# vocab = sorted(vocab)

# Reserve 0 for masking via pad_sequences
# vocab_size = len(vocab) + 1
# word_idx = dict((c, i + 1) for i, c in enumerate(vocab))
# story_maxlen = max(map(len, (x for x, _, _ in train + test)))
# query_maxlen = max(map(len, (x for _, x, _ in train + test)))

# x, xq, y = vectorize_stories(train, word_idx, story_maxlen, query_maxlen)
# tx, txq, ty = vectorize_stories(test, word_idx, story_maxlen, query_maxlen)

# print('vocab = {}'.format(vocab))
# print('x.shape = {}'.format(x.shape))
# print('xq.shape = {}'.format(xq.shape))
# print('y.shape = {}'.format(y.shape))
# print('story_maxlen, query_maxlen = {}, {}'.format(story_maxlen, query_maxlen))

# print('Build model...')

# sentence = layers.Input(shape=(story_maxlen,), dtype='int32')
# encoded_sentence = layers.Embedding(vocab_size, EMBED_HIDDEN_SIZE)(sentence)
# encoded_sentence = RNN(SENT_HIDDEN_SIZE)(encoded_sentence)

# question = layers.Input(shape=(query_maxlen,), dtype='int32')
# encoded_question = layers.Embedding(vocab_size, EMBED_HIDDEN_SIZE)(question)
# encoded_question = RNN(QUERY_HIDDEN_SIZE)(encoded_question)

# merged = layers.concatenate([encoded_sentence, encoded_question])
# preds = layers.Dense(vocab_size, activation='softmax')(merged)

# model = Model([sentence, question], preds)
# model.compile(optimizer='adam',
#               loss='categorical_crossentropy',
#               metrics=['accuracy'])

# print('Training')
# model.fit([x, xq], y,
#           batch_size=BATCH_SIZE,
#           epochs=EPOCHS,
#           validation_split=0.05)

# print('Evaluation')
# loss, acc = model.evaluate([tx, txq], ty,
#                            batch_size=BATCH_SIZE)
# print('Test loss / test accuracy = {:.4f} / {:.4f}'.format(loss, acc))

# print(
data = get_time_series(2012, 2013, "0011", input_params=(
    # ('atmospheric_pressure_hourly', AtmosphericPressureHourly),
    ('co_hourly', COHourly),
    # ('humidity_hourly', HumidityHourly),
    #('pm10_hourly', Pm10Hourly),
    #('pm25_hourly', Pm25Hourly),
    ('temperature_hourly', TemparatureHourly)
    )
)

print (data[:10])
# )