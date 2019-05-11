import os
import datetime

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
from matplotlib import dates

from math import sqrt
from sklearn.preprocessing import MinMaxScaler
from sklearn import metrics as skmet
from sklearn import preprocessing as skprep
from keras.models import Sequential, load_model
from keras.layers import Dense
from keras.layers import LSTM

from au_epa_data.constants import DATETIME_FORMAT
from common.models import AQIOrganization
from .constants import FIGS_DATA_DIR, FORECASTABLE_POLLUTANTS, MODELS_DATA_DIR
from .utils import get_time_series, get_file_name


# convert series to supervised learning
def _series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    n_vars = 1 if type(data) is list else data.shape[1]
    df = pd.DataFrame(data)
    cols, names = list(), list()
    # input sequence (t-n, ... t-1)
    for i in range(n_in, 0, -1):
        cols.append(df.shift(i))
        names += [('var%d(t-%d)' % (j + 1, i)) for j in range(n_vars)]
    # forecast sequence (t, t+1, ... t+n)
    for i in range(0, n_out):
        cols.append(df.shift(-i))
        if i == 0:
            names += [('var%d(t)' % (j + 1)) for j in range(n_vars)]
        else:
            names += [('var%d(t+%d)' % (j + 1, i)) for j in range(n_vars)]
    # put it all together
    agg = pd.concat(cols, axis=1)
    agg.columns = names
    # drop rows with NaN values
    if dropnan:
        agg.dropna(inplace=True)
    return agg


# normalize train and test data to [0, 1]
def _normalize(values):
    # fit scaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(values)
    return scaler, scaled


def _prepare_time_series(dataset, predict_col, n_input, n_output):
    # load dataset
    values = dataset.values
    col_num = len(dataset.columns)
    # ===================================================
    # integer encode  a labeled discrete variable
    # encoder = LabelEncoder()
    # values[:, 4] = encoder.fit_transform(values[:, 4])
    # ===================================================
    # # ensure all data is float
    values = values.astype('float32')
    # # normalize features
    scaler, scaled = _normalize(values)
    # frame as supervised learning
    reframed = _series_to_supervised(scaled, n_input, n_output)
    # drop columns we don't want to predict
    if predict_col == 'manual':
        try:
            predict_col = int(input(
                'Enter the variable to predict, a value between 1'
                ' and {}: '.format(col_num)))
        except ValueError:
            predict_col = 1

    predict_col_name = dataset.columns[predict_col - 1]
    reframed_col_num = len(reframed.columns)
    output_start = n_input * col_num
    if predict_col is None or predict_col <= 1:
        drop_cols = list(range(output_start + 1, reframed_col_num))
    elif predict_col >= col_num:
        drop_cols = list(range(output_start, reframed_col_num - 1))
    else:
        drop_cols = list(
            range(output_start, output_start + (predict_col - 1))) + list(
            range(output_start + predict_col, reframed_col_num))

    reframed.drop(reframed.columns[drop_cols], axis=1, inplace=True)
    print(reframed.head())
    print(reframed.shape)

    return reframed, scaler, predict_col_name


def _split_dataset(reframed, n_train_hours, n_features, n_input):
    # split into train and test sets
    values = reframed.values
    train = values[:n_train_hours, :]
    test = values[n_train_hours:, :]
    print ('# Training Vals', len(train[:, 0]))
    print ('# Test Vals', len(test[:, 0]))
    # split into input and outputs
    n_obs = n_input * n_features
    train_X, train_y = train[:, :n_obs], train[:, -1]
    test_X, test_y = test[:, :n_obs], test[:, -1]
    print(train_X.shape, len(train_X), train_y.shape)
    # reshape input to be 3D [samples, timesteps, features]
    train_X = train_X.reshape((train_X.shape[0], n_input, n_features))
    test_X = test_X.reshape((test_X.shape[0], n_input, n_features))
    print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)
    print(train_X[:, 0])
    print(train_y[:])

    return train_X, train_y, test_X, test_y


def _fit_model(
        train_X, train_y, test_X, test_y, runs, epochs, n_neurons,
        batch_size):

    # design network
    train_runs = pd.DataFrame()
    val_runs = pd.DataFrame()
    for i in range(runs):
        model = Sequential()
        model.add(LSTM(
            n_neurons, input_shape=(train_X.shape[1], train_X.shape[2])))
        model.add(Dense(1))
        model.compile(loss='mae', optimizer='adam')
        # fit network
        history = model.fit(
            train_X, train_y, epochs=epochs, batch_size=batch_size,
            validation_data=(test_X, test_y), verbose=2, shuffle=False)
        # story history
        train_runs[str(i)] = history.history['loss']
        val_runs[str(i)] = history.history['val_loss']

    # plot train and validation loss across multiple runs
    plt.figure()
    plt.plot(train_runs, color='blue', label='train')
    plt.plot(val_runs, color='orange', label='validation')
    plt.title('model train vs validation loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend()
    plt.show()

    return model


def recall_curve(Y_test, y_score, labels):
    # For each class
    precision = dict()
    recall = dict()

    # A "macro-average": quantifying score on each class separately
    recall["macro"] = skmet.recall_score(
        Y_test, y_score, average="macro")
    precision["macro"] = skmet.precision_score(
        Y_test, y_score, average="macro")

    # A "micro-average": quantifying score on all classes jointly
    precision["micro"] = skmet.precision_score(
        Y_test, y_score, average="micro")
    recall["micro"] = skmet.recall_score(
        Y_test, y_score, average="micro")

    print('Precision score macro: {} and micro: {}'
          .format(precision['macro'], precision['micro']))
    print('Recall score macro: {} and micro: {}'
          .format(recall['macro'], recall['micro']))


def _evaluate_model(
        model, n_features, n_input, test_X, test_y, scaler, batch_size,
        predict_col_name):
    # make a prediction
    print(test_X.shape)
    yhat = model.predict(test_X)
    test_X = test_X.reshape((test_X.shape[0], n_input * n_features))
    # invert scaling for forecast
    y_forecast = np.concatenate((yhat, test_X[:, -(n_features - 1):]), axis=1)
    y_forecast = scaler.inverse_transform(y_forecast)
    y_forecast = y_forecast[:, 0]
    print(y_forecast)
    # invert scaling for actual
    test_y = test_y.reshape((len(test_y), 1))
    y_actual = np.concatenate((test_y, test_X[:, -(n_features - 1):]), axis=1)
    y_actual = scaler.inverse_transform(y_actual)
    y_actual = y_actual[:, 0]
    print(y_actual)
    # calculate RMSE
    rmse = sqrt(skmet.mean_squared_error(y_actual, y_forecast))
    print('Test RMSE: %.3f' % rmse)
    mae = skmet.mean_absolute_error(y_actual, y_forecast)
    print('Test MAE: %.3f' % mae)

    # label values for classification statistical analysis
    if predict_col_name in FORECASTABLE_POLLUTANTS:
        pollutant = predict_col_name.lower()
        y_ac_labels, y_fc_labels = _label_values(
            y_actual, y_forecast, pollutant)
        le_ac = skprep.LabelEncoder()
        le_fc = skprep.LabelEncoder()
        le_ac.fit(y_ac_labels)
        le_fc.fit(y_fc_labels)
        print(y_ac_labels[:20], y_fc_labels[:20])
        recall_curve(
            le_ac.transform(y_ac_labels), le_fc.transform(y_fc_labels),
            set(np.concatenate((le_ac.classes_, le_fc.classes_))))
        matthews = skmet.matthews_corrcoef(y_ac_labels, y_fc_labels)
        print('Test Matthews: %.3f' % matthews)

    return y_actual, y_forecast


def _print_prediction(
        test_index, y_actual, y_forecast, fig_title, whole=False):
    # Prediction Figure
    plt.figure(figsize=(16, 12))
    if not whole:
        date_slice = (24 * 10, 24 * 15)
        dts = list(map(
            lambda d: datetime.datetime.strptime(
                d, DATETIME_FORMAT), test_index))
        fds = dates.date2num(dts)
        hfmt = dates.DateFormatter('%m/%d %Hh')
        ax = plt.gca()
        ax.plot(
            fds[date_slice[0]:date_slice[1]],
            y_actual[date_slice[0]:date_slice[1]],
            color='blue', linewidth=1, label='ground truth')
        ax.plot(
            fds[date_slice[0]:date_slice[1]],
            y_forecast[date_slice[0]:date_slice[1]],
            color='red', linewidth=1, label='prediction')
        ax.xaxis.set_major_locator(dates.HourLocator(interval=6))
        ax.xaxis.set_major_formatter(hfmt)
        plt.setp(ax.get_xticklabels(), rotation=80)
    else:
        plt.plot(y_actual, color='blue', linewidth=1, label='Ground Truth')
        plt.plot(y_forecast, color='red', linewidth=1, label='Prediction')
    plt.grid(True)
    plt.legend()

    if fig_title is not None:
        figfile_name = '{}.eps'.format(fig_title)
        plt.savefig(
            os.path.join(FIGS_DATA_DIR, figfile_name), quality=100,
            format='eps', pad_inches=0.25, bbox_inches='tight')
    else:
        plt.show()


def _label_values(y_actual, y_forecast, pollutant, aqi_scale='AUEPA'):
    try:
        aqi_organization = AQIOrganization.objects.get(pk=aqi_scale)
    except AQIOrganization.DoesNotExist:
        aqi_organization = AQIOrganization.objects.get(pk='AUEPA')

    return (
        list(aqi_organization.get_categories(y_actual, pollutant)),
        list(aqi_organization.get_categories(y_forecast, pollutant))
    )


def run(
        file_name='10001_aq_series.csv', columns=None, predict_col='manual',
        train_prop=0.7, n_input=24, n_output=1, runs=1, epochs=100,
        neurons=100, batch_size=24, load_from_file=None, save_file=False,
        evaluate=True):

    # Load dataset
    dataset = get_time_series(file_name, columns)
    n_features = len(dataset.columns)
    n_train_hours = int(365 * 48 * train_prop)

    # Prepare dataset for supervised learning
    reframed, scaler, predict_col_name = _prepare_time_series(
        dataset, predict_col, n_input, n_output)

    # Split dataset into training and test sets
    train_X, train_y, test_X, test_y = _split_dataset(
        reframed, n_train_hours, n_features, n_input)

    if load_from_file is None:
        # Fit to LSTM model
        model = _fit_model(
            train_X, train_y, test_X, test_y, runs, epochs, neurons, batch_size
        )
        if save_file:
            model_title = get_file_name(
                file_name.split('_')[0], dataset.columns, 'model')
            model.save(os.path.join(MODELS_DATA_DIR, model_title + '.h5'))
    else:
        # Load model from file
        # Be sure that the same variables are passed as when the model was
        # saved.
        model = load_model(os.path.join(MODELS_DATA_DIR, load_from_file))

    # Statistical Eval
    if evaluate:
        fig_title = get_file_name(
            file_name.split('_')[0], dataset.columns, '_'.join([
                predict_col_name, 'prediction']))
        test_index = dataset.index[n_train_hours + n_input:]
        y_actual, y_forecast = _evaluate_model(
            model, n_features, n_input, test_X, test_y, scaler, batch_size,
            predict_col_name)

        # Printing the prediction
        _print_prediction(test_index, y_actual, y_forecast, fig_title)


def run_print_features(
        file_name='10001_aq_series.csv', columns=None, save_fig=False):
    dataset = get_time_series(file_name, columns)
    values = dataset.values
    # specify columns to plot
    groups = list(range(0, len(dataset.columns)))
    i = 1
    # plot each column
    fig, ax = plt.subplots(len(groups), 1, sharex=True, figsize=(20, 15))

    dts = list(map(
        lambda d: datetime.datetime.strptime(d, DATETIME_FORMAT), dataset.index
    ))
    fds = dates.date2num(dts)
    hfmt = dates.DateFormatter('%m/%d %Hh')

    date_slice = (24 * 50, 24 * 60)
    for group in groups:
        ax[group].plot(
            fds[date_slice[0]:date_slice[1]],
            values[date_slice[0]:date_slice[1], group],
            label=dataset.columns[group]
        )
        ax[group].xaxis.set_label('Date and hour')
        ax[group].yaxis.set_label('# of Cars')
        ax[group].xaxis.set_major_locator(dates.HourLocator(interval=6))
        ax[group].xaxis.set_major_formatter(hfmt)
        plt.setp(ax[group].get_xticklabels(), rotation=80)
        # ax[group].legend(frameon=False)
        ax[group].grid(True)
        col_name = dataset.columns[group]
        ax[group].set_title(
            col_name, x=1 + (0.008 * len(col_name)), y=0.45, loc='right')
        i += 1
    if save_fig:
        fig_title = file_name.split('.csv')[0]
        figfile_name = '{}_ATTRS.eps'.format(fig_title)
        plt.savefig(
            os.path.join(FIGS_DATA_DIR, figfile_name), quality=100,
            format='eps', pad_inches=0.25, bbox_inches='tight')
    else:
        plt.show()
