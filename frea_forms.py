import os
import sys
import pyexcel as pe
import functools
import argparse
import FormParser

__version__ = '0.0.1'

ap = argparse.ArgumentParser(description='Process forms into csv.')
ap.add_argument('input', nargs=1,
                help = 'Folder with form files.')
ap.add_argument('-fd', '--form_definitions', required=True,
                help='JSON file containing form field definitions.')
args = ap.parse_args(sys.argv[1:])

try:
    assert (len(args.input) == 1), \
        "Pass one folder to process on the command line."
    folder = args.input[0]

    assert os.path.isdir(folder), \
        "{0} is not a valid path, please pass the folder to process.".format(folder)
    contents = map (functools.partial(os.path.join, folder), os.listdir(folder))
    file_names = [f for f in contents if os.path.isfile(os.path.join(folder, f))]

    form_definitions = args.form_definitions
    assert os.path.isfile(form_definitions), \
        "{0} is not a valid file name with form definitions.".format(form_definitions)
    form_parsers = list(FormParser.load_form_parsers(form_definitions))

    for file_name in file_names:
        sheet_arr = pe.get_sheet(file_name=file_name).to_array()

        parsed = 0
        for fp in form_parsers:
            if fp.parse_array(sheet_arr):
                print ('Processed {0} form.'.format(fp.name))
                parsed += 1
        if parsed == 0:
            print ('Unable to process {0}, no suitable form parser.'.format(file_name))

except AssertionError as e:
    print (e)
except Exception as e:
    print ('Unexpected error \'{0}\', contact a developer.'.format(str(e)))
