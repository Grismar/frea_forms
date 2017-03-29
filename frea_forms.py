import os
import sys
import pyexcel as pe
import functools
import argparse
import FormParser

__version__ = '0.1.1'
DEBUG = False

ap = argparse.ArgumentParser(description='Process forms into csv.')
ap.add_argument('input', nargs=1,
                help = 'Folder with form files.')
ap.add_argument('-o', '--output_folder', default=None,
                help='Folder to write output to (default is same as input).')
ap.add_argument('-fd', '--form_definitions', required=True,
                help='JSON file containing form field definitions.')
args = ap.parse_args(sys.argv[1:])

try:
    # accept a single positional argument, the input folder
    assert (len(args.input) == 1), \
        "Pass one folder to process on the command line."
    folder = args.input[0]

    # require that folder exists and retrieve all the names of files in the root of that folder
    # TODO: add an option to traverse subdirectories
    assert os.path.isdir(folder), \
        "{0} is not a valid path, please pass the folder to process.".format(folder)
    contents = map (functools.partial(os.path.join, folder), os.listdir(folder))
    file_names = [f for f in contents if os.path.isfile(os.path.join(folder, f))]

    # required option for form_definitions, initialise form_parsers as a list of FormParser
    form_definitions = args.form_definitions
    assert os.path.isfile(form_definitions), \
        "{0} is not a valid file name with form definitions.".format(form_definitions)
    form_parsers = list(FormParser.load_form_parsers(form_definitions))

    # either output_folder is the same as folder, or set explicitly (and required to exist)
    if args.output_folder is None:
        output_folder = folder
    else:
        output_folder = args.output_folder
    assert os.path.isdir(output_folder), \
        "{0} is not a valid path, please pass a folder to write to.".format(output_folder)

    # iterate over all files in folder, assume they are sheets, attempt to parse
    for file_name in file_names:
        sheet_arr = pe.get_sheet(file_name=file_name).to_array()

        parsed = 0
        for fp in form_parsers:
            try:
                if fp.parse_array(sheet_arr):
                    print ('Processed {0} form {1}.'.format(fp.name, file_name))
                    parsed += 1
            except Exception as e:
                print ('Error during processing of {0}: \'{1}\''.format(file_name, str(e)))
                if DEBUG == True:
                    raise e
        if parsed == 0:
            print ('Unable to process {0}, no suitable form parser.'.format(file_name))

    # write out the collected content of all parsers
    for fp in form_parsers:
        fp.write_csv(os.path.join(output_folder, fp.name+'.csv'))

except AssertionError as e:
    print (e)
except Exception as e:
    print ('Unexpected error \'{0}\', contact a developer.'.format(str(e)))
    if DEBUG == True:
        raise e
