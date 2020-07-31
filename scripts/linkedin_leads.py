# -*- coding: utf-8 -*-

import re
import os
import csv

INPUT_FOLDER = "/Users/oferbr/Documents/LinkedinLeads/input"
OUTPUT_FOLDER = "/Users/oferbr/Documents/LinkedinLeads/output"
OUTPUT_SUFFIX = ".csv"

LINKEDIN_PATTERN = r"&amp;quot;(https://www.linkedin.com/in/[\w\-]+)&amp;quot;,&amp;quot;title&amp;quot;:{&amp;quot;textDirection&amp;quot;:&amp;quot;USER_LOCALE&amp;quot;,&amp;quot;text&amp;quot;:&amp;quot;([\w\-\.\,\(\) ]+)&amp;quot;,&amp;quot;"

def process_input_file(filepath):
    f = open(filepath)
    text = f.read()
    lst = re.findall(LINKEDIN_PATTERN, text)
    print(f"{filepath}: {len(lst)} rows")
    return lst

def write_output_file(path, output):
    output_filename = os.path.basename(path) + OUTPUT_SUFFIX
    output_filepath = os.path.join(OUTPUT_FOLDER, output_filename)
    print(f"*** Writing {len(output)} rows to: {output_filepath}")
    f = open(output_filepath, 'w')
    writer = csv.writer(f)
    writer.writerow(["Name", "Linkedin Profile"])
    for link, name in output:
        writer.writerow([name, link])

def process_folder(path, folders, files):
    output = []
    print(f"*** Processing folder ({len(files)} files): {path}")
    for filename in sorted(files):
        filepath = os.path.join(path, filename)
        lst = process_input_file(filepath)
        output.extend(lst)
    write_output_file(path, output)

def main():
    all_folders = list(os.walk(INPUT_FOLDER))
    for path, folders, files in all_folders[1:]:
        process_folder(path, folders, files)

if __name__ == "__main__":
    main()
