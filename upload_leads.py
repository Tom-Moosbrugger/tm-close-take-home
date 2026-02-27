import argparse
import csv
from datetime import datetime

from closeio_api import Client
from utils import get_valid_emails, get_valid_phones, get_valid_address, get_valid_name

# provide ability to accept CLI arguments for filepath, API Key, date range
parser = argparse.ArgumentParser(description="Sample Python Script for writing files.")
parser.add_argument("file", help="Path to CSV file")
parser.add_argument("--api-key", "-k", required=True, help="Close API Key")
parser.add_argument("--start-date", "-s", required=True, help="Start date for grouping leads, format: YYYY-MM-DD")
parser.add_argument("--end-date", "-e", required=True, help="End date for grouping leads, format: YYYY-MM-DD")

args = parser.parse_args()

# enforce format for start and end day
try:
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date()
except ValueError:
    print("Dates must be in YYYY-MM-DD format.")
    exit(1)

# ensure start date doesn't come after end date
if start_date > end_date:
    print("start-date must be before or equal to end-date.")
    exit(1)


api = Client(args.api_key)
file = open(args.file, encoding="utf-8")
reader = csv.DictReader(file)

#TODO: use this function to get custom fields from CSV
def extract_custom_field_names(headers, prefix="custom."):
    """
    From CSV headers, return a set of custom field names (strings)
    for any header that starts with 'custom.'.
    """
    names = set()
    for h in headers or []:
        if not h:
            continue
        h = h.strip()
        if h.startswith(prefix):
            name = h[len(prefix):].strip()
            if name:
                names.add(name)
    return names

#TODO: create function to query Close API for custom field
def fetch_existing_custom_fields():
    pass

#TODO: create function to compare existing custom fields with CSV custom fields, 
#TODO: create new custom fields if required, and return dict with field names and ids
def create_custom_fields():
    pass

def create_lead(row):
    """
    Take a row of CSV data and transform it into an API-ready dict
    """
    row = {name: (value or "").strip() for name, value in row.items()}

    # skip rows that have no data
    if not any(row.values()): 
        return None
    
    # skip rows that don't have a company name, since we don't have a lead to associate them with
    lead_name = get_valid_name(row.get("Company"))
    if not lead_name:
        return None
    
    lead = {"name": lead_name}

    # only add list of addresses if we have a valid address
    addresses = get_valid_address(row.get("Company US State"))
    if addresses:
        lead["addresses"] = addresses

    contact = {}

    contact_name = get_valid_name(row.get("Contact Name"))
    if contact_name:
        contact["name"] = contact_name

    phones = get_valid_phones(row.get("Contact Phones"))
    if phones:
        contact["phones"] = phones

    emails = get_valid_emails(row.get("Contact Emails"))
    if emails:
        contact["emails"] = emails

    # only add list of contacts if we have a valid contact with data 
    # accept contacts with only one field to be inclusive and capture data
    if contact:
        lead["contacts"] = [contact]

    #TODO: populate custom field for date founded
    #TODO: populate custom field for revenue

    return lead

#TODO: find and/or create custom field ids with helper functions

# dict to store grouped-together leads
grouped_leads = {}

print("Reading file and grouping leads together...")
for row in reader:
    lead = create_lead(row)
    
    if not lead:
        continue
    
    company = lead["name"]

    if company not in grouped_leads:
        grouped_leads[company] = lead
    else:
        existing = grouped_leads[company]

        # if the row had a contact, add it to the list of contacts for the lead if not a duplicate
        if lead.get("contacts"):
            existing.setdefault("contacts", [])
            contact = lead["contacts"][0]
            if contact not in existing["contacts"]:
                existing["contacts"].append(contact)
        
        # if the row had an address, add it to the list of addresses for the lead if not a duplicate                
        if lead.get("addresses"):
            existing.setdefault("addresses", [])
            address = lead["addresses"][0]
            if address not in existing["addresses"]:
                existing["addresses"].append(address)
print("Finished grouping leads!")

success_count = 0
failed_count = 0

print("Uploading leads to Close API:")
for lead in grouped_leads.values():
    try:
        api.post("lead", lead)
        success_count += 1
        print(f"Created lead: {lead['name']}")
    except Exception as e:
        failed_count += 1
        print(f"Failed to create {lead['name']}: {e}")

print(f"\nSuccessfully created {success_count} of {len(grouped_leads)} possible leads.")
print(f"{failed_count} leads failed to upload.")
file.close()


#TODO: iterate through grouped_leads create state-level aggregates
#TODO: Use state-level aggregates to create new CSV


