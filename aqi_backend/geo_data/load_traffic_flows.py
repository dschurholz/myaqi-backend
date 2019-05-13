import os
import csv
import copy
import time
from datetime import datetime, timedelta
from django.utils import timezone

from .models import TrafficFlow
from .constants import (
    TRAFFIC_FLOW_FIELD_MAPPING, TRAFFIC_FLOW_DATE, TRAFFIC_FLOW_DATE_FORMAT,
    TRAFFIC_FLOW_VOLUME, TRAFFIC_NB_DETECTOR, TRAFFIC_RELEVANT_STATIONS,
    TRAFFIC_FLOW_TEMPLATE, TRAFFIC_NB_SCATS_SITE, TRAFFIC_NM_REGION)

traffic_data_dir = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__), 'data', 'traffic'),
)


def save_flows(new_flows, total_flows):
    new_traffic_flows = map(
        lambda x: TrafficFlow(**x),
        new_flows)
    TrafficFlow.objects.bulk_create(
        new_traffic_flows)
    # print("{} Records added for site, from {} in total."
    #       "".format(len(new_flows), total_flows - 1))


def run(verbose=True):
    start_time = time.time()
    total_flows = 0
    for year_dir in os.listdir(traffic_data_dir):
        print("In folder:", year_dir)
        year_dir_path = os.path.join(traffic_data_dir, year_dir)
        file_list = sorted(os.listdir(year_dir_path))
        for traffic_file in file_list:
            # if traffic_file == "VSDATA_20170718.csv":
            if traffic_file.endswith(".csv"):
                print("Importing file:", traffic_file)
                with open(
                        os.path.join(year_dir_path, traffic_file)) as csv_file:
                    csv_reader = csv.reader(csv_file, delimiter=',')
                    field_pos = {}
                    date = None
                    first_line = 0
                    new_flows = []
                    for row in csv_reader:
                        if first_line == 0:
                            print('Column names are {}'.format(", ".join(row)))
                            field_pos = {c: i for i, c in enumerate(row)}
                            first_line = 1
                        elif (row[field_pos[TRAFFIC_NB_SCATS_SITE]] not in
                                TRAFFIC_RELEVANT_STATIONS):
                            continue
                        else:
                            if row[field_pos[TRAFFIC_NB_DETECTOR]] == '1':
                                # Save preexisting flows
                                if len(new_flows) > 0:
                                    save_flows(new_flows, total_flows)
                                    new_flows = []

                                date = datetime.strptime(
                                    row[field_pos[TRAFFIC_FLOW_DATE]],
                                    TRAFFIC_FLOW_DATE_FORMAT)
                                date = timezone.make_aware(date, is_dst=False)
                                print(
                                    "Adding measurements for site: {}\n"
                                    "On date: {}".format(
                                        row[field_pos[TRAFFIC_NB_SCATS_SITE]],
                                        date.strftime(TRAFFIC_FLOW_DATE_FORMAT)
                                    )
                                )
                                for i in range(0, 24):
                                    new_flow = copy.copy(TRAFFIC_FLOW_TEMPLATE)
                                    new_flow[
                                        TRAFFIC_FLOW_FIELD_MAPPING[
                                            TRAFFIC_NB_SCATS_SITE]] = row[
                                        field_pos[TRAFFIC_NB_SCATS_SITE]]
                                    new_flow[
                                        TRAFFIC_FLOW_FIELD_MAPPING[
                                            TRAFFIC_NM_REGION]] = row[
                                        field_pos[TRAFFIC_NM_REGION]]
                                    new_flow[TRAFFIC_FLOW_FIELD_MAPPING[
                                        TRAFFIC_FLOW_DATE]] = (
                                            date + timedelta(hours=i))
                                    new_flows.append(new_flow)

                            for i in range(0, 96, 4):
                                volume = 0
                                for j in range(i, i + 4):
                                    idx = ('V0' + str(j)
                                           if j < 10 else 'V' + str(j))
                                    try:
                                        val = int(row[field_pos[idx]])
                                    except ValueError:
                                        continue
                                    else:
                                        if val > 0:
                                            volume += int(row[field_pos[idx]])

                                nf = int(i / 4)
                                new_flows[nf][TRAFFIC_FLOW_VOLUME] += volume

                            total_flows += 1

                    if len(new_flows) > 0:
                        save_flows(new_flows, total_flows)
                continue
            else:
                continue
        continue
    print(
        "Done! %d records. Import was executed successfully.\n"
        " It took %.4f minutes." % (
            total_flows, (time.time() - start_time) / 60.0))
