import logging
import urllib
import os
import time
import json
import requests
import xml.etree.ElementTree as ET
from collections import OrderedDict
from django.core.management.base import BaseCommand, CommandError

from au_epa_data.constants import (
    AU_VIC_URL_MAP,
    COMMAND_MODEL_MAP,
    ENTRIES,
    ENTRIES_COUNT,
    FOREIGN_KEY,
    FOREIGN_KEY_SELF,
    MANY_2_MANY,
    REL_FIELD_NAME,
    REL_FIELD_TYPE,
    RELATIONAL_TABLE_STRUCTURE,
    SERVICES_METADATA,
    TABLE_STRUCTURE,
    UNIQUE_PARAMS,
)

logger = logging.getLogger('myaqi.commands')


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
            default='Site',
            help='Model to update.'
        )
        parser.add_argument(
            '--url', '-u',
            action="store",
            type=str,
            default="",
            help='The url for the web service from which to fetch the data.'
        )
        parser.add_argument(
            '--format',
            action="store",
            default="application/json",
            help=('The format of the endpoint data.')
        )
        parser.add_argument(
            '--url_args',
            action='store',
            type=json.loads,
            default=None,
            help='Extra parameter to use on the url endpoint in JSON format.'
        )

    def handle(self, *args, **options):
        # Setting logging
        level = options.get('level')
        if level:
            try:
                logger.setLevel(getattr(logging, level.upper()))
            except AttributeError:
                pass

        model_type = options.get('type')
        model_dict = OrderedDict(COMMAND_MODEL_MAP)
        try:
            model = model_dict[model_type]
        except KeyError:
            logger.error('Invalid model type: %e' % model_type)
            raise

        start_time = time.time()
        url = options.get('url')
        url_args = options.get('url_args')
        if not url:
            url = OrderedDict(AU_VIC_URL_MAP)[model_type]
        if url_args is not None:
            url = '?'.join([url, urllib.parse.urlencode(url_args)])
        data_format = options.get('format')

        headers = {'content-type': data_format}
        logger.info('Fetching {0}s from {1}.'.format(model_type, url))
        r = requests.get(url, headers=headers)

        if r.status_code >= 300:
            logger.error(
                "Error while fetching data from api %s."
                " after %.4f minutes." % (
                    url, (time.time() - start_time) / 60.0))
            return False

        metadata = OrderedDict(SERVICES_METADATA)
        model_metadata = OrderedDict(metadata[model_type])
        model_table = OrderedDict(model_metadata[TABLE_STRUCTURE])
        model_rel_table = OrderedDict(
            model_metadata[RELATIONAL_TABLE_STRUCTURE])
        root = r.json()

        logger.info('Fetched {0} {1}s!'.format(
            root[model_metadata[ENTRIES_COUNT]], model_type))
        for i, entry in enumerate(root[model_metadata[ENTRIES]]):
            logger.debug('{0} #{1}: {2}'.format(model_type, i, entry))
            unique_fields = {}
            default_fields = {}
            for k, attr in model_table.items():
                if k in model_metadata[UNIQUE_PARAMS]:
                    unique_fields[attr] = entry[k]
                else:
                    default_fields[attr] = entry[k]

            logger.debug('unique_fields: {0}\ndefault_fields: {1}'.format(
                unique_fields, default_fields))
            obj, created = model.objects.update_or_create(
                **unique_fields, defaults=default_fields)

            if model_rel_table is not None:
                obj_needs_update = False
                for f, rel_type in model_rel_table.items():
                    logger.debug('rel_type: {0}'.format(rel_type))
                    entry_attributes = entry[f]
                    if entry_attributes is None:
                        continue

                    rel_metadata = OrderedDict(metadata[rel_type])
                    if rel_metadata[TABLE_STRUCTURE] is not None:
                        rel_table = OrderedDict(rel_metadata[TABLE_STRUCTURE])
                        rel_model = model_dict[rel_type]
                    else:
                        rel_table = None
                    rel_func = rel_metadata[REL_FIELD_TYPE]
                    rel_entry_list = []

                    if type(entry[f]) == dict:
                        entry_attributes = [entry_attributes]

                    if rel_func == MANY_2_MANY and rel_table is None:
                        rel_entry_list = [entry_attributes]
                    else:
                        for rel_entry in entry_attributes:
                            fields = {
                                attr: rel_entry[k]
                                for k, attr in rel_table.items()
                            }

                            if rel_func == FOREIGN_KEY:
                                fields[rel_metadata[REL_FIELD_NAME]] = obj
                            logger.debug('rel_fields: {0}'.format(fields))
                            rel_obj, rel_created = \
                                rel_model.objects.get_or_create(**fields)

                            if rel_func == FOREIGN_KEY_SELF:
                                setattr(
                                    obj,
                                    rel_metadata[REL_FIELD_NAME],
                                    rel_obj
                                )
                                obj_needs_update = True

                            if rel_func == MANY_2_MANY:
                                rel_entry_list.append(rel_obj)

                    if rel_func == MANY_2_MANY and len(rel_entry_list) > 0:
                        obj.update_m2m_field(rel_type, rel_entry_list)

                if obj_needs_update:
                    obj.save()

        logger.info(
            "Done! Command was executed successfully."
            " It took %.4f minutes." % ((time.time() - start_time) / 60.0))
