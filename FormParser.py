import re
import csv
import json
import datetime
from collections import OrderedDict
from ordered_set import OrderedSet

class FormParser:
    def __init__(self, form_def=None):
        self.rows = []
        self.field_names = OrderedSet()
        if form_def is None:
            self.form_def = None
        else:
            self.set_definition(form_def)

    @property
    def name(self):
        if (self.form_def is not None) and ('name' in self.form_def):
            return self.form_def['name']
        else:
            return None

    def set_definition(self, form_def):
        self.form_def = form_def

        assert 'name' in form_def, "Form def without name."
        assert 'key' in form_def, "Form def without key."
        assert 'field_def' in form_def, "Form def without field definitions."

    def parse_array(self, arr):
        # check for key in array
        c = field_to_coordinates(self.form_def['key']['field'])
        if not self.form_def['key']['phrase'].lower() in arr[c[0]][c[1]].lower():
            return False

        row = OrderedDict()

        for k in self.form_def['field_def']:
            fd = self.form_def['field_def'][k]
            if isinstance(fd, str):
                c = field_to_coordinates(fd)
                row[k] = arr[c[0]][c[1]]
            elif 'field' in fd:
                c = field_to_coordinates(fd['field'])
                if 'type' in fd:
                    if fd['type'] == 'date':
                        # TODO
                        v = arr[c[0]][c[1]]
                        if isinstance(v, str) and ('format' in fd):
                            v = datetime.datetime.strptime(v, fd['format']).date()
                        if not isinstance(v, datetime.date):
                            raise Exception(
                                'Field {0} does not appear to be a date: {1}'.format(k, v))
                    elif fd['type'] == 'time':
                        v = arr[c[0]][c[1]]
                        if isinstance(v, str) and ('format' in fd):
                            v = datetime.datetime.strptime(v, fd['format']).time()
                        if not isinstance(v, datetime.time):
                            raise Exception(
                                'Field {0} does not appear to be a time: {1}'.format(k, v))
                    elif fd['type'] == 'comma-separated':
                        # TODO currently very basic, does not account for quotes, etc.
                        v = arr[c[0]][c[1]].split(',')
                    else:
                        v = None
                else:
                    v = arr[c[0]][c[1]]

                if isinstance(v, list):
                    if not 'label_template' in fd:
                        raise Exception('Unable to process multi-valued field def {0} without label_template.'.format(k))
                    i = 0
                    for x in v:
                        i += 1
                        row[fd['label_template'].format(i)] = x
                else:
                    row[k] = v

            elif 'range' in fd:
                if not 'label_template' in fd:
                    raise Exception('Unable to process \'range\' field def {0} without label_template.'.format(k))
                if not 'label_start' in fd:
                    raise Exception('Unable to process \'range\' field def {0} without label_start.'.format(k))
                if not 'label_increment' in fd:
                    raise Exception('Unable to process \'range\' field def {0} without label_increment.'.format(k))

                c_gen = range_to_coordinate_generator(fd['range'])

                label_index = int(fd['label_start'])
                for c in c_gen:
                    row[fd['label_template'].format(label_index)] = arr[c[0]][c[1]]
                    label_index += fd['label_increment']
            else:
                raise Exception("Unable to process field def {0}.".format(k))

        keys = OrderedSet(row.keys())
        if len(keys) < len(row.keys()):
            raise Exception('Duplicate column names.')
        self.field_names = OrderedSet(self.field_names | keys)
        self.rows.append(row)

        return True

    def write_csv(self, file_name):
        with open(file_name, 'w', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=self.field_names, quotechar='"', quoting=csv.QUOTE_ALL)

            writer.writeheader()
            writer.writerows(self.rows)

def load_form_parsers(file_name):
    with open(file_name) as fd_file:
        fds = json.load(fd_file, object_pairs_hook=OrderedDict)

    for fd in fds:
        yield FormParser(fd)

def _letter_value(c):
    return ord(c.lower()) - ord('a')

def _field_to_coordinates(c,r):
    row = int(r) - 1
    if len(c) == 2:
        column = _letter_value(c[0]) * 26 + _letter_value(c[1])
    else:
        column = _letter_value(c[0])

    return (row, column)

def field_to_coordinates(field_str):
    match = re.match(r'^([a-zA-Z]{1,2})([0-9]+)$', field_str)
    assert match is not None, "Not a valid field {0}.".format(field_str)

    return _field_to_coordinates(match.group(1), match.group(2))

def range_to_coordinate_generator(range_str):
    match = re.match(r'^([a-zA-Z]{1,2})([0-9]+):([a-zA-Z]{1,2})([0-9]+)$', range_str)
    assert match is not None, "Not a valid range {0}.".format(range_str)

    c1 = _field_to_coordinates(match.group(1), match.group(2))
    c2 = _field_to_coordinates(match.group(3), match.group(4))

    if (c1[0] == c2[0]):
        for i in range(c1[1], c2[1]+1):
            yield (c1[0], i)
    elif (c1[1] == c2[1]):
        for i in range(c1[0], c2[0]+1):
            yield (i, c1[1])
    else:
        for i in range(c1[0], c2[0]+1):
            for j in range(c1[1], c2[1] + 1):
                yield (i, j)
