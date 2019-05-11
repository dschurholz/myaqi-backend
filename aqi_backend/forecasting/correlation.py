import os
import numpy as np
import matplotlib.pyplot as plt

from .lstm_forecast import get_time_series
from .constants import FIGS_DATA_DIR


def run(file_name='10001_aq_series.csv', fig_title='AQ Variables Correlation'):
    data = get_time_series(file_name)
    corr = data.corr()
    fig = plt.figure()
    ax = fig.add_subplot(111)
    cax = ax.matshow(corr, cmap='coolwarm', vmin=-1, vmax=1)
    fig.colorbar(cax)
    ticks = np.arange(0, len(data.columns), 1)
    ax.set_xticks(ticks)
    plt.xticks(rotation=90)
    ax.set_yticks(ticks)
    ax.set_xticklabels(data.columns)
    ax.set_yticklabels(data.columns)
    if fig_title:
        figfile_name = '{}.eps'.format(fig_title.lower().replace(' ', '_'))
        plt.savefig(
            os.path.join(FIGS_DATA_DIR, figfile_name), quality=100,
            format='eps', pad_inches=0.25, bbox_inches='tight')
    else:
        plt.show()
