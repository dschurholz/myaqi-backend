# Forecasting

This module implements the logic for forecasting air quality data from historical time series. Follow the next steps to run a prediction cycle:

*Note: all the following commands are executed from within the `./manage shell` console.*

### 1. Writing data to a file

First we need to write the data from the databases into a CSV file that has the format to be read by the lstm_forecast module.

    >>> from forecasting import write_time_series
    >>> write_time_series.run(aq_sites=[10001], pollutants={'10001': ['BPM2.5', 'CO']}, include_traffic=True, include_fires=True)

### 2. Run a forecast

With the previous step done we can run an experiment to see a LSTM prediction in practice. 

    >>> from forecasting import lstm_forecast
    >>> lstm_forecast.run(file_name='10001_PM2.5_CO_predictionFORECAST.csv', columns=None, predict_col='manual', train_prop=0.7, n_input=24, n_output=1, epochs=100, neurons=50, batch_size=24, load_from_file=None, save_model=False, evaluate=True, save_prediction=False)

### 3. Plot a forecast

With the previous step done we can plot the ran experiment to see a LSTM prediction result. 

    >>> from forecasting import lstm_forecast
    >>> lstm_forecast.run_print_forecast(file_name='10001_PM2.5_CO_predictionFORECAST.csv', fig_title=None, whole=False,
        date_slice=None)

For other functions in this module build and check the [documentation](https://github.com/dschurholz/myaqi-backend/tree/master/docs). 