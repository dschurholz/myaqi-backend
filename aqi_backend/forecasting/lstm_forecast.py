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
    raw_train = values[:n_train_hours, :]
    raw_test = values[n_train_hours:, :]
    print('# Training Vals', len(raw_train[:, 0]))
    print('# Test Vals', len(raw_test[:, 0]))
    # split into input and outputs
    n_obs = n_input * n_features
    train_X, train_y = raw_train[:, :n_obs], raw_train[:, -1]
    test_X, test_y = raw_test[:, :n_obs], raw_test[:, -1]
    # reshape input to be 3D [samples, timesteps, features]
    train_X = train_X.reshape((train_X.shape[0], n_input, n_features))
    test_X = test_X.reshape((test_X.shape[0], n_input, n_features))
    print(train_X.shape, train_y.shape, test_X.shape, test_y.shape)

    return train_X, train_y, test_X, test_y, raw_train, raw_test


def _print_validation_data(train_stats, val_stats):
    # plot train and validation loss across multiple runs
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(train_stats['loss'], color='blue', label='train')
    plt.plot(val_stats['loss'], color='orange', label='validation')
    plt.title('model train vs validation loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend()

    # plot train and validation accuracy across multiple runs
    plt.subplot(2, 1, 2)
    plt.plot(train_stats['accuracy'], color='green', label='train')
    plt.plot(val_stats['accuracy'], color='red', label='validation')
    plt.title('model train vs validation accuracy')
    plt.ylabel('accuracy')
    plt.xlabel('epoch')
    plt.legend()

    plt.show()


def _fit_model(
        train_X, train_y, test_X, test_y, epochs, n_neurons, batch_size):

    print('Model training with batch_size: {}, epochs: {} and {} '
          'neurons.'.format(batch_size, epochs, n_neurons))
    # design network
    train_stats = {
        'loss': pd.DataFrame(),
        'accuracy': pd.DataFrame()
    }
    val_stats = {
        'loss': pd.DataFrame(),
        'accuracy': pd.DataFrame()
    }

    model = Sequential()
    model.add(LSTM(
        n_neurons, input_shape=(train_X.shape[1], train_X.shape[2])))
    model.add(Dense(1))
    model.compile(loss='mae', optimizer='adam', metrics=['accuracy'])
    # fit network
    history = model.fit(
        train_X, train_y, epochs=epochs, batch_size=batch_size,
        # validation_data=(test_X, test_y), verbose=2, shuffle=False)
        validation_split=0.33, verbose=2, shuffle=False)
    # loss history
    train_stats['loss'] = history.history['loss']
    val_stats['loss'] = history.history['val_loss']
    # accuracy story
    train_stats['accuracy'] = history.history['acc']
    val_stats['accuracy'] = history.history['val_acc']

    _print_validation_data(train_stats, val_stats)
    return model


def _fit_model_experiments(
        train_X, train_y, test_X, test_y, epochs, n_neurons, batch_size,
        scaler, n_input, n_features, predict_col_name):

    print('Running model training experiments with batch_sizes: {}, epochs: {}'
          ' and {} neurons.'.format(batch_size, epochs, n_neurons))
    # design network
    train_stats = {
        'loss': pd.DataFrame(),
        'accuracy': pd.DataFrame(),
        'val_loss': pd.DataFrame(),
        'val_accuracy': pd.DataFrame(),
        'forecasts': pd.DataFrame(),
        'mae': [],
        'rmse': [],
        'precision': [],
        'recall': [],
        'correlation': []
    }
    test_stats = {
        'forecasts': pd.DataFrame(),
        'stats': [],
        'mae': [],
        'rmse': [],
        'precision': [],
        'recall': [],
        'correlation': []
    }
    model = Sequential()
    model.add(LSTM(
        n_neurons, input_shape=(train_X.shape[1], train_X.shape[2])))
    model.add(Dense(1))
    model.compile(loss='mae', optimizer='adam', metrics=['accuracy'])

    for i in range(epochs):
        # fit network
        history = model.fit(
            train_X, train_y, epochs=1, batch_size=batch_size,
            # validation_data=(test_X, test_y), verbose=2, shuffle=False)
            validation_split=0.33, verbose=0, shuffle=False)
        train_stats['loss'][str(i)] = history.history['loss']
        train_stats['val_loss'][str(i)] = history.history['val_loss']
        # accuracy story
        train_stats['accuracy'][str(i)] = history.history['acc']
        train_stats['val_accuracy'][str(i)] = history.history['val_acc']
        model.reset_states()

        y_actual, y_forecast, stats = _evaluate_model(
            model, n_features, n_input, train_X, train_y, scaler, batch_size,
            predict_col_name)
        # loss history
        train_stats['forecasts'][str(i)] = y_forecast
        train_stats['mae'].append(stats['mae'])
        train_stats['rmse'].append(stats['rmse'])
        train_stats['precision'].append(stats['precision']['micro'])
        train_stats['recall'].append(stats['recall']['micro'])
        train_stats['correlation'].append(stats['correlation'])

        # Save last for stateful prediction
        if i < epochs - 1:
            model.reset_states()

        y_actual, y_forecast, stats = _evaluate_model(
            model, n_features, n_input, test_X, test_y, scaler, batch_size,
            predict_col_name)
        test_stats['forecasts'][str(i)] = y_forecast
        test_stats['mae'].append(stats['mae'])
        test_stats['rmse'].append(stats['rmse'])
        test_stats['precision'].append(stats['precision']['micro'])
        test_stats['recall'].append(stats['recall']['micro'])
        test_stats['correlation'].append(stats['correlation'])
        model.reset_states()

    return train_stats, test_stats


def recall_curve(Y_test, y_score, labels):
    # For each class
    precision = dict()
    recall = dict()

    # A "macro-average": quantifying score on each class separately
    recall["macro"] = skmet.recall_score(
        Y_test, y_score, labels=labels, average="macro")
    precision["macro"] = skmet.precision_score(
        Y_test, y_score, labels=labels, average="macro")

    # A "micro-average": quantifying score on all classes jointly
    recall["micro"] = skmet.recall_score(
        Y_test, y_score, labels=labels, average="micro")
    precision["micro"] = skmet.precision_score(
        Y_test, y_score, labels=labels, average="micro")

    # print('Precision score macro: {} and micro: {}'
    #       .format(precision['macro'], precision['micro']))
    # print('Recall score macro: {} and micro: {}'
    #       .format(recall['macro'], recall['micro']))

    return precision, recall


def _evaluate_model(
        model, n_features, n_input, test_X, test_y, scaler, batch_size,
        predict_col_name):
    # make a prediction
    # print(test_X.shape)
    yhat = model.predict(test_X)
    test_X = test_X.reshape((test_X.shape[0], n_input * n_features))
    # invert scaling for forecast
    y_forecast = np.concatenate((yhat, test_X[:, -(n_features - 1):]), axis=1)
    y_forecast = scaler.inverse_transform(y_forecast)
    y_forecast = y_forecast[:, 0]
    # print(y_forecast)
    # invert scaling for actual
    test_y = test_y.reshape((len(test_y), 1))
    y_actual = np.concatenate((test_y, test_X[:, -(n_features - 1):]), axis=1)
    y_actual = scaler.inverse_transform(y_actual)
    y_actual = y_actual[:, 0]
    # print(y_actual)
    # calculate RMSE
    stats = {}
    stats['rmse'] = sqrt(skmet.mean_squared_error(y_actual, y_forecast))
    stats['mae'] = skmet.mean_absolute_error(y_actual, y_forecast)

    # label values for classification statistical analysis
    if predict_col_name in FORECASTABLE_POLLUTANTS:
        pollutant = predict_col_name.lower()
        y_ac_labels, y_fc_labels = _label_values(
            y_actual, y_forecast, pollutant)
        le_ac = skprep.LabelEncoder()
        le_fc = skprep.LabelEncoder()
        le_ac.fit(y_ac_labels)
        le_fc.fit(y_fc_labels)
        labels = np.concatenate((
            le_ac.transform(le_ac.classes_),
            le_fc.transform(le_fc.classes_)
        ))
        precision, recall = recall_curve(
            le_ac.transform(y_ac_labels), le_fc.transform(y_fc_labels), labels)
        stats['correlation'] = skmet.matthews_corrcoef(
            y_ac_labels, y_fc_labels)
        stats['precision'] = precision
        stats['recall'] = recall

    return y_actual, y_forecast, stats


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
        train_prop=0.7, n_input=24, n_output=1, epochs=100, neurons=100,
        batch_size=24, load_from_file=None, save_file=False, evaluate=True):

    # Load dataset
    dataset = get_time_series(file_name, columns)
    n_features = len(dataset.columns)
    n_train_hours = int(365 * 48 * train_prop)

    # Prepare dataset for supervised learning
    reframed, scaler, predict_col_name = _prepare_time_series(
        dataset, predict_col, n_input, n_output)

    # Split dataset into training and test sets
    train_X, train_y, test_X, test_y, raw_train, raw_test = _split_dataset(
        reframed, n_train_hours, n_features, n_input)

    if load_from_file is None:
        # Fit to LSTM model
        model = _fit_model(
            train_X, train_y, test_X, test_y, epochs, neurons, batch_size
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
        y_actual, y_forecast, stats = _evaluate_model(
            model, n_features, n_input, test_X, test_y, scaler, batch_size,
            predict_col_name)

        print('TestMAE=%f' % stats['mae'])
        print('TestRMSE=%f' % stats['rmse'])
        print('TestPRECSSN=%f' % stats['precision']['micro'])
        print('TestRECALL=%f' % stats['recall']['micro'])
        print('TestCORR=%f' % stats['correlation'])

        # Printing the prediction
        _print_prediction(test_index, y_actual, y_forecast, fig_title)


def run_experiments(
        file_name='10001_aq_series.csv', columns=None, predict_col='manual',
        train_prop=0.7, n_input=24, n_output=1, runs=1,
        epochs=[2, 3], neurons=2,
        batch_sizes=24):

    f = file_name.split('.csv')[0]

    # Load dataset
    dataset = get_time_series(file_name, columns)
    n_features = len(dataset.columns)
    n_train_hours = int(365 * 48 * train_prop)
    neurons = round(
        n_train_hours / (neurons * (n_features * n_input + n_output)))

    # Prepare dataset for supervised learning
    reframed, scaler, predict_col_name = _prepare_time_series(
        dataset, predict_col, n_input, n_output)

    # Split dataset into training and test sets
    train_X, train_y, test_X, test_y, raw_train, raw_test = _split_dataset(
        reframed, n_train_hours, n_features, n_input)

    results = {
        'mae_vals': [],
        'mae': pd.DataFrame(),
        'rmse_vals': [],
        'rmse': pd.DataFrame(),
        'precision_vals': [],
        'precision': pd.DataFrame(),
        'recall_vals': [],
        'recall': pd.DataFrame(),
        'correlation_vals': [],
        'correlation': pd.DataFrame()
    }

    for e in epochs:
        for r in range(1, runs + 1):
            print('Experiments run: %d' % r)
            train_stats, test_stats = _fit_model_experiments(
                train_X, train_y, test_X, test_y, e, neurons, batch_sizes,
                scaler, n_input, n_features, predict_col_name
            )

            mae = pd.DataFrame()
            mae['train'] = train_stats['mae']
            mae['test'] = test_stats['mae']
            rmse = pd.DataFrame()
            rmse['train'] = train_stats['rmse']
            rmse['test'] = test_stats['rmse']
            precision = pd.DataFrame()
            precision['train'] = train_stats['precision']
            precision['test'] = test_stats['precision']
            recall = pd.DataFrame()
            recall['train'] = train_stats['recall']
            recall['test'] = test_stats['recall']
            correlation = pd.DataFrame()
            correlation['train'] = train_stats['correlation']
            correlation['test'] = test_stats['correlation']

            # Plotting
            plt.clf()
            fig = plt.figure(figsize=(12, 6))
            plt.suptitle('Run #%d with %d epochs' % (r, e))
            ax = fig.add_subplot(221)
            ax.plot(mae['train'], color='blue')
            ax.plot(mae['test'], color='orange')
            ax.set_title('MAE')
            ax = fig.add_subplot(222)
            ax.plot(rmse['train'], color='blue')
            ax.plot(rmse['test'], color='orange')
            ax.set_title('RMSE')
            ax = fig.add_subplot(223)
            ax.set_title('PRECISION')
            ax.plot(precision['train'], color='blue')
            ax.plot(precision['test'], color='orange')
            ax = fig.add_subplot(224)
            ax.set_title('CORRELATION')
            ax.plot(correlation['train'], color='blue')
            ax.plot(correlation['test'], color='orange')
            plt.savefig(
                os.path.join(
                    FIGS_DATA_DIR, 'epochs',
                    '%d_epochs_%d_run_%s.png' % (e, r, f)
                ), quality=100, format='png', pad_inches=0.25)
            print('%d, %d) TrainMAE=%f, TestMAE=%f' % (
                r, e, mae['train'].iloc[-1], mae['test'].iloc[-1]))
            print('%d, %d) TrainRMSE=%f, TestRMSE=%f' % (
                r, e, rmse['train'].iloc[-1], rmse['test'].iloc[-1]))
            print('%d, %d) TrainPRECSSN=%f, TrainPRECSSN=%f' % (
                r, e, precision['train'].iloc[-1], precision['test'].iloc[-1]))
            print('%d, %d) TrainRECALL=%f, TestRECALL=%f' % (
                r, e, recall['train'].iloc[-1], recall['test'].iloc[-1]))
            print('%d, %d) TrainCORRELATION=%f, TestCORRELATION=%f' % (
                r, e, correlation['train'].iloc[-1],
                correlation['test'].iloc[-1]))

            results['mae_vals'].append(test_stats['mae'][-1])
            results['rmse_vals'].append(test_stats['rmse'][-1])
            results['precision_vals'].append(test_stats['precision'][-1])
            results['recall_vals'].append(test_stats['recall'][-1])
            results['correlation_vals'].append(test_stats['correlation'][-1])

        results['mae'][str(e)] = results['mae_vals']
        results['rmse'][str(e)] = results['rmse_vals']
        results['precision'][str(e)] = results['precision_vals']
        results['recall'][str(e)] = results['recall_vals']
        results['correlation'][str(e)] = results['correlation_vals']
        results['mae_vals'] = []
        results['rmse_vals'] = []
        results['precision_vals'] = []
        results['recall_vals'] = []
        results['correlation_vals'] = []

    plt.figure(figsize=(12, 6))
    for k, v in results.items():
        if not k.endswith('_vals'):
            plt.clf()
            print(k.upper() + ':')
            print(v.describe())
            print()
            v.boxplot()
            plt.savefig(
                os.path.join(
                    FIGS_DATA_DIR, 'epochs', '%s_stats_%s.png' % (k, f)),
                quality=100, format='png', pad_inches=0.25)


def run_print_features(
        file_name='10001_aq_series.csv', columns=None, save_fig=False,
        fig_title=None, sliced=None):
    dataset = get_time_series(file_name, columns)
    values = dataset.values
    # specify columns to plot
    groups = list(range(0, len(dataset.columns)))
    i = 1
    # plot each column
    fig, ax = plt.subplots(len(groups), 1, sharex=True, figsize=(12, 6))

    if sliced:
        dts = list(map(
            lambda d: datetime.datetime.strptime(
                d, DATETIME_FORMAT), dataset.index
        ))
        fds = dates.date2num(dts)
        # hfmt = dates.DateFormatter('%m/%d %Hh')
        hfmt = dates.DateFormatter('%Y/%m/%d')
        date_slice = sliced

    for group in groups:
        if sliced:
            ax[group].plot(
                fds[date_slice[0]:date_slice[1]],
                values[date_slice[0]:date_slice[1], group],
                label=dataset.columns[group]
            )
            # ax[group].xaxis.set_label('Date and hour')
            # ax[group].yaxis.set_label('# of Cars')
            if (date_slice[1] - date_slice[0]) <= 300:
                ax[group].xaxis.set_major_locator(
                    dates.HourLocator(interval=6))
            else:
                ax[group].xaxis.set_major_locator(
                    plt.MaxNLocator(6))
            ax[group].xaxis.set_major_formatter(hfmt)
            # plt.setp(ax[group].get_xticklabels(), rotation=80)
        else:
            ax[group].plot(
                values[1500:3500, group],
                label=dataset.columns[group]
            )
            ax[group].xaxis.set_label('Time')
        # ax[group].legend(frameon=False)
        ax[group].grid(True)
        col_name = dataset.columns[group]
        ax[group].set_title(
            col_name, fontsize=20, x=1.01, y=0.4, loc='right', ha='left')
        i += 1
    if save_fig:
        if fig_title is None:
            fig_title = file_name.split('.csv')[0]
        else:
            fig_title = fig_title.lower().replace(' ', '_')
        figfile_name = '{}_{}_ATTRS.eps'.format(
            fig_title, 'WHOLE' if not sliced else 'SLICED')
        plt.savefig(
            os.path.join(FIGS_DATA_DIR, figfile_name), quality=100,
            format='eps', pad_inches=0.25, bbox_inches='tight')
    else:
        plt.show()
