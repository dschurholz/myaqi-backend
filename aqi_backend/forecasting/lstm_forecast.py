import os
import datetime

import numpy as np
import pandas as pd

import matplotlib
from django.conf import settings
if not settings.DEBUG:
    matplotlib.use('agg')

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
from .constants import (
    FIGS_DATA_DIR, FORECASTABLE_POLLUTANTS, MODELS_DATA_DIR,
    FORECASTS_DATA_DIR)
from .utils import get_time_series, get_file_name


def _series_to_supervised(data, n_in=1, n_out=1, dropnan=True):
    """ Convert a series to a supervised learning format for algorithm input.

    Parameters:
        data (list or numpy.array): pollutants time series values.
        n_in (int): number of previous time lags to consider for prediction.
        n_out (int): number of next time lags to output for prediction.

    Returns:
        agg (str1):The string which gets reversed. 
    
    """
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


def _normalize(values):
    """ Normalise a set of values to a range between 0 and 1.

    Parameters:
        values (numpy.array): pollutants time series values.

    Returns:
        scaler (MinMaxScaler): the sklearn scaler with the loaded values.
        scaled (numpy.array): the scaled (normalised) values.
    
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(values)
    return scaler, scaled


def _prepare_time_series(dataset, predict_col, n_input, n_output):
    """ Split dataset into training and test set.

    Parameters:
        reframed (pd.DataFrame): normalised pollutants time series values.
        n_train_hours (int): number of hours to consider as training data.
        n_features (int): number of variables.
        n_input (int): number of previous time lags to consider.

    Returns:
        reframed (pd.DataFrame): the normalized and prepared dataset.
        scaler (sklearn.MinMaxScaler): the scaler with loaded values.
        predict_col_name (string): the name of the column to be predicted. 
    
    """
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
    # if we want the user to be prompted for the colum to be predicted
    if predict_col == 'manual':
        try:
            predict_col = int(input(
                'Enter the variable to predict, a value between 1'
                ' and {}: '.format(col_num)))
        except ValueError:
            predict_col = 1

    # drop columns we don't want to predict
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
    """ Split dataset into training and test set.

    Parameters:
        reframed (pd.DataFrame): normalised pollutants time series values.
        n_train_hours (int): number of hours to consider as training data.
        n_features (int): number of variables.
        n_input (int): number of previous time lags to consider.

    Returns:
        train_X (np.array): training X data.
        train_y (np.array): training y data.
        test_X (np.array): test X data.
        test_y (np.array): test y data.
        raw_train (np.array): raw split training data.
        raw_train (np.array): raw split test data.
    
    """
    # split into train and test sets
    values = reframed.values
    raw_train = values[:n_train_hours, :]
    raw_test = values[n_train_hours:, :]
    print('# Training Rows', len(raw_train[:, 0]))
    print('# Test Rows', len(raw_test[:, 0]))
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
    """
    Plot train and validation loss across multiple runs.
    """
    plt.figure()
    plt.subplot(2, 1, 1)
    plt.plot(train_stats['loss'], color='blue', label='train')
    plt.plot(val_stats['loss'], color='orange', label='validation')
    plt.title('model train vs validation loss')
    plt.ylabel('loss')
    plt.xlabel('epoch')
    plt.legend()

    plt.show()


def _fit_model(
        train_X, train_y, test_X, test_y, epochs, n_neurons, batch_size):
    """ Fit the Keras LSTM model with the training and test data and
    meta-parameters. Also prints the validation performance

    Parameters:
        train_X (np.array): training X data.
        train_y (np.array): training y data.
        test_X (np.array): test X data.
        test_y (np.array): test y data.
        epochs (int): number of times to run the model.
        n_neurons (int): number of neurons for the LSTM hidden layer.
        batch_size (int): size of values pero run batch.

    Returns:
        model (Keras-model): the model on the finished training state.
    
    """
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
    model.compile(loss='mae', optimizer='adam')
    # fit network
    history = model.fit(
        train_X, train_y, epochs=epochs, batch_size=batch_size,
        # validation_data=(test_X, test_y), verbose=2, shuffle=False)
        validation_split=0.33, verbose=2, shuffle=False)
    # loss history
    train_stats['loss'] = history.history['loss']
    val_stats['loss'] = history.history['val_loss']

    _print_validation_data(train_stats, val_stats)
    return model


def _fit_model_experiments(
        train_X, train_y, test_X, test_y, epochs, n_neurons, batch_size,
        scaler, n_input, n_features, predict_col_name):
    """ A more controlable version of the _fit_model function, to gain more
    insights on the correct selection of hyperparameters. Evaluates the model
    after each epoch.

    Parameters:
        train_X (np.array): training X data.
        train_y (np.array): training y data.
        test_X (np.array): test X data.
        test_y (np.array): test y data.
        epochs (int): number of times to run the model.
        n_neurons (int): number of neurons for the LSTM hidden layer.
        batch_size (int): size of values pero run batch.
        scaler (sklearn.MinMaxScaler): scaler for the _evaluate function.
        n_input (int): number of previous time_lags considered.
        n_features (int): number of variables considered.
        predict_col_name (string): name of the column to be predicted.

    Returns:
        train_stats, test_stats: the statistics for the training and test runs.
    
    """    

    print('Running model training experiments with batch_sizes: {}, epochs: {}'
          ' and {} neurons.'.format(batch_size, epochs, n_neurons))
    # design network
    train_stats = {
        'forecasts': [],
        'mae': 0,
        'rmse': 0,
        'precision': 0,
        'recall': 0,
        'correlation': 0
    }
    test_stats = {
        'forecasts': [],
        'mae': 0,
        'rmse': 0,
        'precision': 0,
        'recall': 0,
        'correlation': 0
    }
    model = Sequential()
    model.add(LSTM(
        n_neurons, input_shape=(train_X.shape[1], train_X.shape[2])))
    model.add(Dense(1))
    model.compile(loss='mae', optimizer='adam', metrics=['accuracy'])

    for i in range(epochs):
        # fit network
        model.fit(
            train_X, train_y, epochs=1, batch_size=batch_size,
            # validation_data=(test_X, test_y), verbose=2, shuffle=False)
            validation_split=0.33, verbose=0, shuffle=False)
        model.reset_states()

    y_actual, y_forecast, stats = _evaluate_model(
        model, n_features, n_input, train_X, train_y, scaler, batch_size,
        predict_col_name)
    train_stats['forecasts'] = y_forecast
    train_stats['mae'] = stats['mae']
    train_stats['rmse'] = stats['rmse']
    train_stats['precision'] = stats['precision']['micro']
    train_stats['recall'] = stats['recall']['micro']
    train_stats['correlation'] = stats['correlation']

    y_actual, y_forecast, stats = _evaluate_model(
        model, n_features, n_input, test_X, test_y, scaler, batch_size,
        predict_col_name)
    test_stats['forecasts'] = y_forecast
    test_stats['mae'] = stats['mae']
    test_stats['rmse'] = stats['rmse']
    test_stats['precision'] = stats['precision']['micro']
    test_stats['recall'] = stats['recall']['micro']
    test_stats['correlation'] = stats['correlation']

    return train_stats, test_stats


def recall_curve(test_y, y_score, labels):
    """ Calculate the precision and recall for the predicted values.

    :param test_y: test y (predicted) data.
    :type test_y: np.array
    :param y_score: the according label for each value in test_y.
    :type y_score: np.array
    :param labels: all the possible labels that a value could get assigned.
    :type labels: string[]

    :rtype: tuple(dict, dict)
    Returns:
        - precision (dict): micro and macro precision values for the inputs.
        - recall (dict): micro and macro recall values for the inputs.
    
    """

    # For each class
    precision = dict()
    recall = dict()

    # A "macro-average": quantifying score on each class separately
    recall["macro"] = skmet.recall_score(
        test_y, y_score, labels=labels, average="macro")
    precision["macro"] = skmet.precision_score(
        test_y, y_score, labels=labels, average="macro")

    # A "micro-average": quantifying score on all classes jointly
    recall["micro"] = skmet.recall_score(
        test_y, y_score, labels=labels, average="micro")
    precision["micro"] = skmet.precision_score(
        test_y, y_score, labels=labels, average="micro")

    # print('Precision score macro: {} and micro: {}'
    #       .format(precision['macro'], precision['micro']))
    # print('Recall score macro: {} and micro: {}'
    #       .format(recall['macro'], recall['micro']))

    return precision, recall


def _evaluate_model(
        model, n_features, n_input, test_X, test_y, scaler, batch_size,
        predict_col_name):
    """ Evaluates the trained model with test values and returns predictions
    and desired staistics.

    Parameters:
        model (Keras model): the model with the trained state.
        n_features (int): number of variables considered.
        n_input (int): number of previous time_lags considered.
        test_X (np.array): test X data.
        test_y (np.array): test y data.
        scaler (sklearn.MinMaxScaler): scaler for the _evaluate function.
        batch_size (int): size of values pero run batch.
        predict_col_name (string): name of the column to be predicted.

    Returns:
        y_actual (string[]): original ground truth values.
        y_forecast (string[]): forecasted values.
        stats (dict): rmse, mae, correlation, precision and recall satistics for the
            prediction.
    
    """ 
    
    # make a prediction
    # print(test_X.shape)
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
        test_index, y_actual, y_forecast, fig_title, date_slice=None,
        whole=False):
    """ Print the forecasted vs. ground truth values into a graph.

    Parameters:
        test_index (Keras model): the model with the trained state.
        y_actual: original ground truth values.
        y_forecast: forecasted values.
        fig_title (string): name for figure and for file to print to.
        date_slice (tuple(int, int)): range of hours within the dataset to
            consider.
        whole (boolean): if to slice the dataset or consider it completely
            (separate option because of the need for axis lables change).
    
    """ 

    # Prediction Figure
    plt.figure(figsize=(16, 12))
    if not whole:
        if date_slice is None:
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
        if date_slice[1] - date_slice[0] < 25:
            ax.xaxis.set_major_locator(dates.HourLocator(interval=1))
        else:
            ax.xaxis.set_major_locator(plt.MaxNLocator(24))
        ax.xaxis.set_major_formatter(hfmt)
        plt.setp(ax.get_xticklabels(), rotation=80, fontsize=20)
        plt.setp(ax.get_yticklabels(), fontsize=20)
    else:
        ax = plt.gca()
        ax.xaxis.set_major_locator(plt.MaxNLocator(6))
        ax.plot(y_actual, color='blue', linewidth=1, label='Ground Truth')
        ax.plot(y_forecast, color='red', linewidth=1, label='Prediction')
    plt.grid(True)
    plt.legend(prop={'size': 26})

    if fig_title is not None:
        figfile_name = '{}.eps'.format(fig_title)
        plt.savefig(
            os.path.join(FIGS_DATA_DIR, figfile_name), quality=100,
            format='eps', pad_inches=0.25, bbox_inches='tight')
    else:
        plt.show()


def _label_values(y_actual, y_forecast, pollutant, aqi_scale='AUEPA'):
    """ Gets the list of AQI categories for a list of concentration levels
    for a given pollutant and a given AQI organisation.

    Parameters:
        y_actual (numpy.array): original ground truth values.
        y_forecast (numpy.array): forecasted values.
        pollutant (string): abbreviation of the pollutant (e.g., CO)
        aqi_scale (string): abbreviation of the AQI scale to use (e.g., AUEPA)

    Returns:
        y_actual_labels (string[]): a list of the abbreviations of each AQI
            category assigned to each value of y_actual.
        y_forecast_labels (string[]): a list of the abbreviations of each AQI
            category assigned to each value of y_forecast.
    
    """ 
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
        train_prop=0.7, n_input=24, n_output=1, epochs=100, neurons=50,
        batch_size=24, load_from_file=None, save_model=False, evaluate=True,
        save_prediction=False):
    """ Main function. Runs a training and forecast experiment with the given
    parameters.

    :param file_name: CSV file from which to load the experiment data.
    :type file_name: string
    :param columns: the columns from the CSV file to include in the execution.
    :type columns: string[]
    :param predict_col: index of column to be predicted.
    :type predict_col: int
    :param train_prop: percentage of dataset values to use as training set.
    :type train_prop: float
    :param n_input: number of previous time lags to consider in prediction.
    :type n_input: int
    :param n_output: number of future time lags to predict for pollutant.
    :type n_output: int
    :param epochs: number of iterations to run training phase.
    :type epochs: int
    :param neurons: number of neurons in the LSTM hidden layer.
    :type neurons: int
    :param batch_size: size of values per run to use in training.
    :type batch_size: int
    :param load_from_file: file path from which to load an already run Keras
        model from.
    :type load_from_file: string
    :param save_model: if to save the model in a temporary file.
    :type save_model: boolean
    :param evaluate: if to produce an evaluation of the model after training.
    :type evaluate: boolean
    :param save_prediction: if to save the predicted vs. ground truth values in
        a file.
    :type save_prediction: int

    """

    # Load dataset
    dataset = get_time_series(file_name, columns)
    n_features = len(dataset.columns)
    n_train_hours = int(len(dataset.values[:, 0]) * train_prop)
    # n_train_hours = int(365 * 48 * train_prop)
    # neurons = round(
    #     n_train_hours / (neurons * (n_features * n_input + n_output)))

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
        if save_model:
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

        if save_prediction:
            prediction_f = pd.DataFrame()
            prediction_f['date'] = test_index
            prediction_f['actual'] = y_actual[:]
            prediction_f['forecast'] = y_forecast[:]
            prediction_f.index.name = 'No'
            prediction_f.to_csv(
                os.path.join(FORECASTS_DATA_DIR, fig_title + 'FORECAST.csv'))

            with open(os.path.join(
                    FORECASTS_DATA_DIR, fig_title + 'METRICS.txt'), 'w+') as f:
                f.write('TestMAE=%f\n' % stats['mae'])
                f.write('TestRMSE=%f\n' % stats['rmse'])
                f.write('TestPRECSSN=%f\n' % stats['precision']['micro'])
                f.write('TestRECALL=%f\n' % stats['recall']['micro'])
                f.write('TestCORR=%f\n' % stats['correlation'])
        else:
            print('TestMAE=%f' % stats['mae'])
            print('TestRMSE=%f' % stats['rmse'])
            print('TestPRECSSN=%f' % stats['precision']['micro'])
            print('TestRECALL=%f' % stats['recall']['micro'])
            print('TestCORR=%f' % stats['correlation'])

            # Printing the prediction
            _print_prediction(test_index, y_actual, y_forecast, fig_title)


def run_experiments(
        file_name='10001_aq_series.csv', columns=None, predict_col='manual',
        train_prop=0.7, n_input=24, n_output=1, runs=1, epochs=[2, 3],
        neurons=2, batch_sizes=24):
    """ Runs the _fit_model_experiments function to tweak the hyper-parameters.
    TO-DO: The default set is to test the efficiency depending the number of
    epochs. To test batch_size or number of neurons, the code has to be
    changed.

    :param file_name: CSV file from which to load the experiment data.
    :type file_name: string
    :param columns: the columns from the CSV file to include in the execution.
    :type columns: string[]
    :param predict_col: index of column to be predicted.
    :type predict_col: int
    :param train_prop: percentage of dataset values to use as training set.
    :type train_prop: float
    :param n_input: number of previous time lags to consider in prediction.
    :type n_input: int
    :param n_output: number of future time lags to predict for pollutant.
    :type n_output: int
    :param runs: number of complete cycles to run.
    :type runs: int
    :param epochs: number of iterations to run training phase.
    :type epochs: int[]
    :param neurons: number of neurons in the LSTM hidden layer.
    :type neurons: int
    :param batch_size: size of values per run to use in training.
    :type batch_size: int

    """

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

            # mae = pd.DataFrame()
            # mae['train'] = train_stats['mae']
            # mae['test'] = test_stats['mae']
            # rmse = pd.DataFrame()
            # rmse['train'] = train_stats['rmse']
            # rmse['test'] = test_stats['rmse']
            # precision = pd.DataFrame()
            # precision['train'] = train_stats['precision']
            # precision['test'] = test_stats['precision']
            # recall = pd.DataFrame()
            # recall['train'] = train_stats['recall']
            # recall['test'] = test_stats['recall']
            # correlation = pd.DataFrame()
            # correlation['train'] = train_stats['correlation']
            # correlation['test'] = test_stats['correlation']

            # Plotting
            # plt.clf()
            # fig = plt.figure(figsize=(12, 6))
            # plt.suptitle('Run #%d with %d epochs' % (r, e))
            # ax = fig.add_subplot(221)
            # ax.plot(mae['train'], color='blue')
            # ax.plot(mae['test'], color='orange')
            # ax.set_title('MAE')
            # ax = fig.add_subplot(222)
            # ax.plot(rmse['train'], color='blue')
            # ax.plot(rmse['test'], color='orange')
            # ax.set_title('RMSE')
            # ax = fig.add_subplot(223)
            # ax.set_title('PRECISION')
            # ax.plot(precision['train'], color='blue')
            # ax.plot(precision['test'], color='orange')
            # ax = fig.add_subplot(224)
            # ax.set_title('CORRELATION')
            # ax.plot(correlation['train'], color='blue')
            # ax.plot(correlation['test'], color='orange')
            # plt.savefig(
            #     os.path.join(
            #         FIGS_DATA_DIR, 'epochs',
            #         '%d_epochs_%d_run_%s.png' % (e, r, f)
            #     ), quality=100, format='png', pad_inches=0.25)
            print('%d, %d) TrainMAE=%f, TestMAE=%f' % (
                r, e, train_stats['mae'], test_stats['mae']))
            print('%d, %d) TrainRMSE=%f, TestRMSE=%f' % (
                r, e, train_stats['rmse'], test_stats['rmse']))
            print('%d, %d) TrainPRECSSN=%f, TrainPRECSSN=%f' % (
                r, e, train_stats['precision'], test_stats['precision']))
            print('%d, %d) TrainRECALL=%f, TestRECALL=%f' % (
                r, e, train_stats['recall'], test_stats['recall']))
            print('%d, %d) TrainCORRELATION=%f, TestCORRELATION=%f' % (
                r, e, train_stats['correlation'], test_stats['correlation']))
            # plt.close()

            results['mae_vals'].append(test_stats['mae'])
            results['rmse_vals'].append(test_stats['rmse'])
            results['precision_vals'].append(test_stats['precision'])
            results['recall_vals'].append(test_stats['recall'])
            results['correlation_vals'].append(test_stats['correlation'])

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
            plt.close()


def run_print_features(
        file_name='10001_aq_series.csv', columns=None, save_fig=False,
        fig_title=None, sliced=None):
    """ Plots the features of a dataset for a graphical view of the PDF of each
    variable.

    :param file_name: CSV file from which to load the variables time series.
    :type file_name: string
    :param columns: the columns from the CSV file to include in the picture.
    :type columns: string[]
    :param save_fig: if to save the plot to a picture file.
    :type save_fig: boolean
    :param fig_title: the name of the plot and file name if saved.
    :type fig_title: string
    :param sliced: index range to consider when plotting the time series
    :type sliced: tuple(int, int)

    """

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
                values[:, group],
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


def run_print_forecast(
        file_name='10001_aq_series.csv', fig_title=None, whole=False,
        date_slice=None):
    """ Plots the predicted vs. ground truth values of a prediction run.

    :param file_name: CSV file from which to load the predicted time series.
    :type file_name: string
    :param fig_title: the name of the plot and file name if saved.
    :type fig_title: string
    :param whole: if to use the whole dataset when plotting.
    :type whole: boolean
    :param date_slice: index range to consider when plotting the time series
    :type date_slice: tuple(int, int)

    """
    dataset = get_time_series(file_name, file_dir=FORECASTS_DATA_DIR)

    y_actual = dataset['actual']
    y_forecast = dataset['forecast']
    test_index = dataset.index

    # Printing the prediction
    _print_prediction(
        test_index, y_actual, y_forecast, fig_title, date_slice=date_slice,
        whole=whole)
