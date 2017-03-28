import re
import csv
import json

class FormParser:
    def __init__(self, form_def=None):
        self.field_names = []
        self.rows = []
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

    def _generate_field_names(self):
        # TODO: generate field_names
        pass

    def set_definition(self, form_def):
        self.form_def = form_def

        assert 'name' in form_def, "Form def without name."
        assert 'key' in form_def, "Form def without key."
        assert 'field_def' in form_def, "Form def without field definitions."

        self._generate_field_names()

    def parse_array(self, arr):
        # check for key
        c = field_to_coordinates(self.form_def['key']['field'])
        if not self.form_def['key']['phrase'].lower() in arr[c[0]][c[1]].lower():
            return False

        # TODO: generate row from arr

        return True

    def write_csv(self, file_name):
        # TODO: write all rows
        pass

def load_form_parsers(file_name):
    with open(file_name) as fd_file:
        fds = json.load(fd_file)

    for fd in fds:
        yield FormParser(fd)


def field_to_coordinates(field):
    def letter_value(c):
        return ord(c.lower()) - ord('a')

    match = re.match(r'^([a-zA-Z]{1,2})([0-9]+)$', field)
    assert match is not None, "Not a valid field {0}.".format(field)

    row = int(match.group(2)) - 1
    if len(match.group(1)) == 2:
        column = letter_value(match.group(1)[0]) * 26 + letter_value(match.group(1)[1])
    else:
        column = letter_value(match.group(1)[0])

    return (row, column)
