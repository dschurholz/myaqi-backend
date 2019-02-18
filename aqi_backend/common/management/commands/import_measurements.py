import logging
import os
import csv
import time
from collections import OrderedDict
from django.core.management.base import BaseCommand, CommandError

from epa_data.constants import COMMAND_MODEL_MAP, GENERAL_TABLE_FIELD_MAP

logger = logging.getLogger('myaqi.commands')


def model_fields_list(headers=[], table_map=GENERAL_TABLE_FIELD_MAP):
    table = OrderedDict(table_map)
    return [table[header] for header in headers]


class Command(BaseCommand):
    help = 'Import a set of measurements to the database tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--level', '-l',
            help='Level of logging'
        )
        parser.add_argument(
            '--type', '-t',
            action='store',
            type=str,
            default='Pm10Hourly',
            help='Import '
        )
        parser.add_argument(
            '--path', '-p',
            action="store",
            type=str,
            help='The path where the files to be import reside (absolute).'
        )
        parser.add_argument(
            '--filename', '-f',
            action="store",
            type=str,
            help=(
                'The name of the file to import; if file-prefix is True, '
                'this is treated as such prefix.'
            )
        )
        parser.add_argument(
            '--prefix',
            action="store_true",
            default=False,
            help=(
                'Use to import many files with same prefix, but different '
                'endings.')
        )
        parser.add_argument(
            '--format',
            action="store",
            default="csv",
            help=('The format of the files to import.')
        )

    def handle(self, *args, **options):
        # Setting logging
        level = options.get('level')
        if level:
            try:
                logger.setLevel(getattr(logging, level.upper()))
            except AttributeError:
                pass

        model = options.get('type')
        model_dict = OrderedDict(COMMAND_MODEL_MAP)
        try:
            model = model_dict[model]
        except KeyError:
            logger.error('Invalid model type: %e' % model)
            raise

        start_time = time.time()
        with_prefix = options.get('prefix')
        filename = options.get('filename')
        path = options.get('path')
        file_format = options.get('format')

        if with_prefix:
            files_to_import = [
                os.path.join(path, i) for i in os.listdir(path)
                if os.path.isfile(os.path.join(path, i)) and
                filename in i and ("." + file_format) in i
            ]
        else:
            files_to_import = (
                [os.path.join(path, filename)]
                if os.path.isfile(os.path.join(path, filename)) else [])

        logger.info('Opening files {0}.'.format(files_to_import))
        for data_file in files_to_import:
            with open(data_file, newline='') as open_file:
                header_reader = csv.reader(open_file)
                header = header_reader.__next__()
                fieldnames = model_fields_list(header)
                reader = csv.DictReader(open_file, fieldnames=fieldnames)
                measurements = []
                self.stdout.write('H {0}'.format(fieldnames))
                for i, row in enumerate(reader):
                    measurements.append(model(
                        **row
                    ))
                    if (i + 1) % 100000 == 0:
                        model.objects.bulk_create(measurements)
                        measurements = []
                        self.stdout.write(
                            self.style.SUCCESS(
                                'Successfully imported {0} measurements!'
                                .format(i + 1)))
                if len(measurements) > 0:
                    model.objects.bulk_create(measurements)
                self.stdout.write(
                    self.style.SUCCESS(
                        'Successfully imported {0} measurements from file {1}!'
                        .format(i + 1, data_file)))

        logger.info(
            "Done! Command was executed successfully."
            " It took %.4f minutes." % ((time.time() - start_time) / 60))
