# Tom Moosbrugger: Close Take-Home Project

## Introduction

Welcome to the repository for my take-home project! In this repo, you will find my script for the Close take-home project.

This README will walk you through the logic of my approach, as well as describe the basic setup and instructions for running the script successfully.

I hope you have as much fun exploring it as I had making it.

## Script Logic

For those of you who aren't so technical, I want to provide a brief explanation of the logic in my script. This particular script is meant to accomplish two goals. I will go into each goal below, and walk you through how I approached it. 

Before that, though, a quick explanation of what a 'script' is. A script is a file you run on your computer that executes a set of instructions. These instructions can accomplish all sorts of things: make or delete folders/files, send messages, even start a game of tic-tac-toe. 

Conveniently, scripts can accept some user input, which allows us to extend their capabilities a little further. In this case, I've extended mine by allowing it to accept the following things:
- The path to a .csv file containing the leads you want to import
- Your API Key, which we need to upload information to your Close account
- A start date, in the form of YYYY-MM-DD 
- An end date, also in the form of YYYY-MM-DD 

The reasons for allowing these particular user inputs will be made clear in the explanations that follow!

### Goal 1: Upload lead data

The first goal of this script is to allow you to upload Lead data from a .csv file into your Close account, discarding invalid data.

As mentioned above, the script conveniently allows you to include a path to the .csv file that has your lead data. By using that path, I was able to open the file and read its contents, row by row.

The next step was to go through each row and extract the data we need. There are two complications here: first, a lead can have multiple rows of data in the .csv, because we want you to be able to provide multiple contacts for the same lead; and second, we want to discard invalid data.

To address the first complication, I created a place to store the leads from the .csv, which we'll call 'grouped_leads'. grouped_leads is like a temporary folder where we can store some information about each lead, like their name and contacts. Once I created grouped_leads, I went through each row of the .csv, examining and validating (more on that below) the data, and putting into a nice pretty format for when we store it in grouped_leads. Once we've processed a row of data and it's ready to be stored, I then checked grouped_leads to see if we already had a record for the lead we just processed. If we had NOT seen the lead, I created an entry for them in grouped_leads. If we HAD seen the lead, instead of creating a whole new entry, I added the relevant info from the current record to the entry we already saved.

Addressing the second complication happened as we examined each row. For each row of data, I came up with a set of rules for each column to determine what was 'valid' or 'invalid'. In general, I wanted to enforce some simple standards for what the data should look like, and I took cues from a sample .csv file to help define those standards. I also wanted to clean up the data so that it was in a viable format to be stored on Close. Overall, I took a pretty lenient approach, only throwing away data that was missing completely or egregiously/obviously incorrect. 

This is probably best illustrated with some examples, so here are a few:
- **Names**: trimmed leading/trailing whitespace, applied consistent title-casing (e.g., “Sample Name”), and discarded rows where the company or contact name was missing.
- **Emails**, Allowed multiple emails separated by ';', and validated each against standard email format rules (needs to have an @, domain, etc.).
- **Phone Numbers**, I allowed users to input multiple phone numbers by splitting them across lines, required a leading '+' country code, removed non-numeric characters except '+' and '-', and checked that the number met country-specific digit rules based on its country code.

Once the data was both validated and grouped together in our grouped_leads 'folder', the next step was to upload them to Close. Using the API Key you provide when you run the file, I connected to Close's server and send each record one at a time. If a record is rejected for any reason, the script informs you and shares the reason it happened, but continues uploading the other records. Once complete, it tells you how many records were successfully uploaded, and how many failed. 

### Goal 2: Create a new .csv with the provided Leads

The second goal of this script is to create a new .csv that filters and aggregates some of the data from the original .csv. More specifically, the idea is to produce a .csv file in which each row represents a state, and includes: the total number of leads in the state, the lead with the most revenue in the state, the total revenue of all leads in the state, and the median revenue of all the leads in the state. 

Given the time constraints of this exercise, I wasn't able to implement this goal. However, I still devised a simple approach for solving it, which I will outline below. 

The first step in addressing this was accepting some additional user input. The script allows you to enter a start- and end-date when you run it, with some simple checks to ensure they are in the right format (i.e. YYYY-MM-DD, and that start doesn't come after end). 

Since we already have the leads grouped together after completing goal 1, that makes the rest of this task relatively straightforward. We need a place to store details about the states, which we'll call state_revenues; this is like the grouped_leads 'folder' above. Once we have that it's a matter of going through each lead one by one and building the details of each state.

For each lead in grouped_leads, we check if they were founded in the date range provided. If so, we determine which state they are from, then check if the state is in state_revenues. If it is NOT, then we create an entry for it; each entry will have sub-entries that can keep track of the relevant data for that state: number of leads, total revenue, etc. If the entry already exists, we update those values with the data from the current lead. 

A consideration here: not all leads have state and revenue data. My intuition would be to discard any lead that doesn't have a state or revenue, since we can't put it with a state if we don't have one, and totals and medians don't really work with no entry. That would probably be how I would design it, but you could also set it up to let the user decide what to do with entries that have no states or revenues!

Either way, once we have our state_revenues 'folder', we can easily use it to go through each state one-by-one and add them as rows to a new .csv, which will save right in the same folder as your script. 

## How To Run This Script

In order to run this script, you will need to have a few things installed on your computer: `git`, `python 3`, and `virtualenv`. Once you have those installed, follow the instructions below.

### Setup

Open a terminal window and run the following commands:
1. `git clone https://github.com/Tom-Moosbrugger/tm-close-take-home.git`
2. `cd tm-close-take-home`
3. `virtualenv venv`
4. `. venv/bin/activate`
4. `pip install -r requirements.txt`

### Running the script

Once you have activated the virtual environment and installed the dependencies, you are ready to run the script.

The script requires the following arguments:
A path to the CSV file (positional argument)
A Close API key (--api-key or -k)
A start date (--start-date or -s)
An end date (--end-date or -e)

Dates must be provided in YYYY-MM-DD format. There is also a mock_data.csv file included for testing.

Format:
```bash
python upload-leads.py /path/to/your/file \
    --api-key YOUR_API_KEY \
    --start-date YYYY-MM-DD \
    --end-date YYYY-MM-DD
```

You can also use shorter flags for your key and dates, like this:
```bash
python upload_leads.py /path/to/your/file \
    --k YOUR_API_KEY \
    --s YYYY-MM-DD \
    --e YYYY-MM-DD
```

Example:
```bash
python upload_leads.py mock_data.csv \
    -k hook_poll_abc123xyz \
    --s 2023-01-01 \
    --e 2023-12-31
```