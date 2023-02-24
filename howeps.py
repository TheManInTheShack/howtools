# ==============================================================================
# howeps
# How can we make Ashaya's HOW Episode database better?

#  - integrate show notes with autotags
#  - pull thumbnails of vids (youtube/spotify)
#  - pull tags from episodes online?
# ==============================================================================

# ------------------------------------------------------------------------------
# Import
# ------------------------------------------------------------------------------
from datetime import datetime
import os
import sys
import argparse
import shutil
import json

import requests

import numpy as np
import pandas as pd
from docx import Document

# ------------------------------------------------------------------------------
# Command line interface
# ------------------------------------------------------------------------------
def cli():
    parser = argparse.ArgumentParser()
    #parser.add_argument("name",  type=str, help="your name")
    #parser.add_argument("other_arg_alas", type=int, help="help text to be displayed")
    args = parser.parse_args()
    return args

# ------------------------------------------------------------------------------
# Initialization
# - name of csv source file of the database
# - folder holding show notes
# - list of specific show notes documents to work with
# ------------------------------------------------------------------------------
def initialize(args):
    init = {}

    init['csv_src'] = "data\\ash_start.csv"

    init['shownotes_loc'] = "data\\shownotes"

    init['shownotes'] = []

    for f in os.listdir(init['shownotes_loc']):
        if f.endswith("docx"):
            init['shownotes'].append(f)

    #init['shownotes'].append("A White Cloak Turned is Still White_ Selmy _ Cole.docx")
    #init['shownotes'].append("ACOK Wrap Up.docx")

    init['currency'] = []
    init['currency'].append("$")

    return init

# ------------------------------------------------------------------------------
# Main
# ------------------------------------------------------------------------------
def main(args, init):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    print("Starting procedure...")

    # --------------------------------------------------------------------------
    # Get the input data into a dataframe for ease of use
    #    data['Video title']
    #    data['Video publish time']
    #    data['Series']
    #    data['Visibility']
    #    data['YouTube Link']
    #    data['Spotify Link']
    #    data['Guest']
    #    data['YouTube']
    #    data['Pod']
    #    data['Patreon']
    #    data['Content']
    #    data['Views']
    #    data['Spotify 2']
    #    data['Series 1']
    # --------------------------------------------------------------------------
    epdata = pd.read_csv(init['csv_src']).replace(np.nan, "")

    # --------------------------------------------------------------------------
    # Get the unique contents of things that have multi-responses in the cells
    # --------------------------------------------------------------------------
    series = get_delimited_lex(epdata['Series'])
    guests = get_delimited_lex(epdata['Guest'])

    # --------------------------------------------------------------------------
    # Read show notes documents and organize the contents into notes data
    # --------------------------------------------------------------------------
    ndata = {}
    for sfile in init['shownotes']:
        ndata[sfile] = parse_show_notes_file(sfile, init['shownotes_loc'])

    # --------------------------------------------------------------------------
    # Add thumbnail link for youtube
    # --------------------------------------------------------------------------
    epdata['Thumbnail Link'] = get_yt_thumbnails(epdata)

    # --------------------------------------------------------------------------
    # Save updated data table to file
    # --------------------------------------------------------------------------
    x = epdata.to_excel("new_db.xlsx")

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    print("...finished!")


# ------------------------------------------------------------------------------
# Get all the thumbnails
# ------------------------------------------------------------------------------
def get_yt_thumbnails(epdata):
    # --------------------------------------------------------------------------
    # Grab the youtube thumbnail
    # --------------------------------------------------------------------------
    thumbs = []
    for idx, rec in epdata.iterrows():
        content = rec['Content']
        if len(content) == 11:
            thumbs.append(f"https://img.youtube.com/vi/{content}/0.jpg")
        else:
            thumbs.append("NO YOUTUBE")

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return thumbs


# ------------------------------------------------------------------------------
# Given a word document expected to be basically in HOW show notes, extract
# and organize useful things.
# ------------------------------------------------------------------------------
def parse_show_notes_file(filename, location):
    # --------------------------------------------------------------------------
    # Start
    # --------------------------------------------------------------------------
    fpath = os.path.join(location, filename)
    print(f"...reading file '{fpath}'...")

    # --------------------------------------------------------------------------
    # Get the actual file and parse out the text into a list of paragraphs
    # --------------------------------------------------------------------------
    doc = Document(fpath)

    text = []
    for para in doc.paragraphs:
        text.append(para.text)

    # --------------------------------------------------------------------------
    # Work through the paragraphs
    # --------------------------------------------------------------------------
    super_chats = []
    for i, line in enumerate(text):
        # ----------------------------------------------------------------------
        # A dollar sign in the line indicates a super-chat, which are generally
        # going to be on three lines:
        # 1. Donor name
        # 2. Dollar Amount
        # 3. Donor note
        # ----------------------------------------------------------------------
        for symbol in init['currency']:
            if symbol in line:
                schat = {}
                schat['dname']  = text[i-1]
                schat['amount'] = text[i]
                schat['dnote']  = text[i+1]

                super_chats.append(schat)

        # ----------------------------------------------------------------------
        # 
        # ----------------------------------------------------------------------


    # --------------------------------------------------------------------------
    # Consolidate
    # --------------------------------------------------------------------------
    shownotes_data = {}
    shownotes_data['super_chats'] = super_chats

    # --------------------------------------------------------------------------
    # Finish
    # --------------------------------------------------------------------------
    return shownotes_data

# ------------------------------------------------------------------------------
# Any iterable can be a list of delimited items; extract the unique list of them
# ------------------------------------------------------------------------------
def get_delimited_lex(items, delimiter=","):
    full_list = []
    for item in items:
        if item:
            elements = [x.strip() for x in str(item).split(delimiter)]
            full_list.extend(elements)
    counts = pd.Series(full_list).value_counts()
    return counts

# ------------------------------------------------------------------------------
# Run sequence:
# 1 command line arguments
# 2 start clock
# 3 initialization function
# 4 main
# 5 stop clock
# 6 display elapsed time
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    args = cli()
    start_time = datetime.utcnow()
    init = initialize(args)
    main(args, init)
    end_time     = datetime.utcnow()
    elapsed_time = end_time - start_time
    print("Elapsed time: " + str(elapsed_time))

