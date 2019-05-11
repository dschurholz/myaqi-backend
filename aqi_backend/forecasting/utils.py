import os
import datetime
import numpy as np
import pandas as pd
from django.utils import timezone

from au_epa_data.constants import DATETIME_FORMAT
from .constants import AQ_DATA_DIR


def get_datetime_span_dict(start_date, end_date):
    span_dict = {}
    date = timezone.make_aware(start_date, is_dst=False)
    end_date = timezone.make_aware(end_date, is_dst=False)

    while date <= end_date:
        span_dict[date.strftime(DATETIME_FORMAT)] = []
        date = date + datetime.timedelta(hours=1)
    span_dict[end_date.strftime(DATETIME_FORMAT)] = []

    return span_dict


def mean_absolute_percentage_error(y_true, y_pred):
    y_true, y_pred = np.array(y_true), np.array(y_pred)

    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def get_time_series(file_name, columns):
    file = os.path.join(AQ_DATA_DIR, file_name)
    index_col = 1
    if columns is not None:
        columns = ['date'] + columns
        index_col = 0
    dataset = pd.read_csv(file, index_col=index_col, usecols=columns)
    if columns is None:
        dataset.drop('No', axis=1, inplace=True)
    # summarize first 5 rows
    print(dataset.head(5))
    return dataset


def get_file_name(site_id, variable_list, extra=''):
    return '_'.join([site_id, '_'.join(variable_list), extra])
