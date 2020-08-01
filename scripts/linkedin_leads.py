# -*- coding: utf-8 -*-

import re
import os
import csv

INPUT_FOLDER = "/Users/oferbr/Dropbox (Personal)/Ofer/Scripts/LinkedinLeads/input"
OUTPUT_FOLDER = "/Users/oferbr/Dropbox (Personal)/Ofer/Scripts/LinkedinLeads/output"
OUTPUT_PREFIX = "Ofer's Linkedin Leads - "
OUTPUT_SUFFIX = ".csv"

LINKEDIN_PATTERN = r"&amp;quot;(https://www.linkedin.com/in/[\w\-]+)&amp;quot;,&amp;quot;title&amp;quot;:{&amp;quot;textDirection&amp;quot;:&amp;quot;USER_LOCALE&amp;quot;,&amp;quot;text&amp;quot;:&amp;quot;([\w\-\.\,\(\) ]+)&amp;quot;,&amp;quot;"

# And just for documentation, here are the Linkedin Links, built by the recruiters,
# to help find potential leads. From these link results, I manually stored
# the HTML's that are now in the input folder
LEADERSHIP_SEARCH = "https://www.linkedin.com/search/results/people/?facetNetwork=%5B%22F%22%5D&origin=FACETED_SEARCH&title=%22Engineering%20Manager%22%20OR%20%22Head%20of%20Engineering%22%20OR%20%22development%20manager%22%20OR%20%22Director%20of%20Engineering%22%20OR%20CTO%20OR%20%22Head%20Of%22"
IC_SEARCH = "https://www.linkedin.com/search/results/people/?facetGeoRegion=%5B%22il%3A0%22%5D&facetIndustry=%5B%224%22%2C%2296%22%2C%226%22%5D&facetNetwork=%5B%22F%22%5D&origin=FACETED_SEARCH&title=%22Software%20Engineer%22%20OR%20%22Tech%20lead%22%20OR%20%22Software%20developer%22%20OR%20%22Full%20Stack%20developer%22%20OR%20%22Backend%20engineer%22%20OR%20%22Full%20Stack%20engineer%22"

def process_input_file(filepath):
    f = open(filepath)
    text = f.read()
    lst = re.findall(LINKEDIN_PATTERN, text)
    print(f"{filepath}: {len(lst)} rows")
    return lst

def write_output_file(path, output):
    output_filename = OUTPUT_PREFIX + os.path.basename(path) + OUTPUT_SUFFIX
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
