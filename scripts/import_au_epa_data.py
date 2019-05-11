import time
from django.core.management import call_command
from forecasting.constants import SITES_MONITORS, TIME_BASIS, DATES


def construct_url_args(site_id, monitor_id, timebasis_id, from_date, to_date):
    url_args = {
        "siteId": site_id,
        "monitorId": monitor_id,
        "fromDate": from_date,
        "timebasisid": '1HR_AV' if timebasis_id is None else timebasis_id,
        "toDate": to_date
    }

    return url_args

# CLEAN MEASUREMENT TABLE (CAUTION: IRREVERSIBLE)
# Measurement.objects.all().delete()


# IMPORT MEASUREMENTS
start_time = time.time()
for site, monitors in SITES_MONITORS.items():
    for monitor in monitors:
            for tb in TIME_BASIS[monitor]:
                for date in DATES:
                    call_command(
                        'au_epa_update', type='measurement', level='info',
                        url_args=construct_url_args(
                            site, monitor, tb, date[0], date[1])
                    )
                    # print(construct_url_args(
                    #     site, monitor, tb, date[0], date[1]))

print(
    "Done! Import was executed successfully.\n"
    " It took %.4f minutes." % ((time.time() - start_time) / 60.0))
