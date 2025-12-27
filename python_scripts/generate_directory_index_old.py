#!/usr/bin/env python3

# Legacy utility: recursively generate index.html files for all subdirectories.
# Kept for reference; prefer generate_directory_index.py for current usage.
# No Home Assistant runtime side effects.

#import argparse
#import fnmatch
#import os
#import sys


index_file_name = 'index.html'

CSS = """ <style>

body {
    background: #f4f4f4;
    margin: 2em 1.5em;
}
/*
body {
    margin: 20px;
    background: #f5f5f5;
    -webkit-box-shadow: rgba(89, 89, 89, 0.449219) 2px 1px 9px 0px;
    -moz-box-shadow: rgba(89, 89, 89, 0.449219) 2px 1px 9px 0px;
    box-shadow: rgba(89, 89, 89, 0.449219) 2px 1px 9px 0px;
    border-radius: 11px;
    -moz-border-radius: 11px;
    -webkit-border-radius: 11px;
    height: 100%;
    min-height: 100%;
}
*/
li {
    font-family: sans-serif;
    font-size: 12pt;
    line-height: 14pt;
    list-style:none;
    list-style-type:none;
    padding: 3px 10px;
    margin: 3px 15px;
    display: block;
    clear:both;
}

.content {
    width: 600px;
    background-color: white;
    margin-bottom: 5em;
    padding-bottom: 3em;
    -webkit-box-shadow: rgba(89, 89, 89, 0.449219) 2px 1px 9px 0px;
    -moz-box-shadow: rgba(89, 89, 89, 0.449219) 2px 1px 9px 0px;
    box-shadow: rgba(89, 89, 89, 0.449219) 2px 1px 9px 0px;
    border: 0;
    border-radius: 11px;
    -moz-border-radius: 11px;
    -webkit-border-radius: 11px;
    height: 96%;
    min-height: 90%;
}


.size {
    float: right;
    color: gray;
}

h1 {
    padding: 10px;
    margin: 15px;
    font-size:13pt;
    border-bottom: 1px solid lightgray;
}

a {
    font-weight: 500;
    perspective: 600px;
    perspective-origin: 50% 100%;
    transition: color 0.3s;
    text-decoration: none;
    color: #060606;
}

a:hover,
a:focus {
    color: #e74c3c;
}

a::before {
    background-color: #fff;
    transition: transform 0.2s;
    transition-timing-function: cubic-bezier(0.7,0,0.3,1);
    transform: rotateX(90deg);
    transform-origin: 50% 100%;
}

a:hover::before,
a:focus::before {
    transform: rotateX(0deg);
}

a::after {
    border-bottom: 2px solid #fff;
}

 </style>
"""


def process_dir(top_dir, output_file, filter):

    index_file_name = output_file
        
    for parentdir, dirs, files in os.walk(top_dir):

        abs_path = os.path.join(parentdir, index_file_name)

        try:
            index_file = open(abs_path, "w")
        except Exception as e:
#            print('cannot create file %s %s' % (abs_path, e))
            continue
        index_file.write('''<!DOCTYPE html>
    <html>
     <head>{css}</head>
     <body>
      <div class="content">
       <h1>{curr_dir}</h1>
       <li><a style="display:block; width:100%" href="..">&#x21B0;</a></li>'''.format(
                css=CSS,
                curr_dir=os.path.basename(os.path.abspath(parentdir))
            )
            )

        for dirname in sorted(dirs):

            absolute_dir_path = os.path.join(parentdir, dirname)

            if not os.access(absolute_dir_path, os.W_OK):
#                print("***ERROR*** folder {} is not writable! SKIPPING!".format(absolute_dir_path))
                continue

            index_file.write("""
       <li><a style="display:block; width:100%" href="{link}">&#128193; {link_text}</a></li>""".format(
                    link=dirname,
                    link_text=dirname
                )
                )

        for filename in sorted(files):

            if filter and not fnmatch.fnmatch(filename, filter):
                continue

            # don't include index.html in the file listing
            if filename.strip().lower() == index_file_name.lower():
                continue

            try:
                size = int(os.path.getsize(os.path.join(parentdir, filename)))

                index_file.write(
    """
       <li>&#x1f4c4; <a href="{link}">{link_text}</a><span class="size">{size}</span></li>""".format(
                                link=filename,
                                link_text=filename,
                                size=pretty_size(size))
                    )

            except Exception as e:
#                print('ERROR writing file name:', e)
                repr(filename)

        index_file.write("""
  </div>
 </body>
</html>""")
        index_file.close()


# bytes pretty-printing
UNITS_MAPPING = [
    (1024 ** 5, ' PB'),
    (1024 ** 4, ' TB'),
    (1024 ** 3, ' GB'),
    (1024 ** 2, ' MB'),
    (1024 ** 1, ' KB'),
    (1024 ** 0, (' byte', ' bytes')),
]


def pretty_size(bytes, units=UNITS_MAPPING):
    """Human-readable file sizes.

    ripped from https://pypi.python.org/pypi/hurry.filesize/
    """
    for factor, suffix in units:
        if bytes >= factor:
            break
    amount = int(bytes / factor)

    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix


top_dir = data.get("top_dir")

output_file = data.get("output_file")

filter = data.get("filter")

process_dir(top_dir, output_file, filter)