from datetime import datetime
import re
from email_validator import validate_email, EmailNotValidError
import phonenumbers

# Dict for mapping state to correct format
STATE_MAP = {
    "New York": "NY",
    "California": "CA",
    "New Mexico": "NM",
    "Minnesota": "MN",
    "Delaware": "DE",
    # would include other states in full implementation...
}

# Normalize and validate company and contact names
def get_valid_name(name):
    if not name:
        return None
    
    parts = name.split()
    title_cased = []

    for part in parts:
        # perform simple transformation to Title Case
        title_cased.append(part.lower().title())

    return " ".join(title_cased)

# Normalize and validate phone numbers with the phonenumber library
def get_valid_phones(phones):
    if not phones:
        return None

    phone_objects = []

    # Check for multiple numbers by splitting with a newline char
    for raw_phone in phones.splitlines():
        phone = raw_phone
        if not phone:
            continue

        # Strip the number of unwanted chars, keeping only digits, +, and -
        phone = re.sub(r"[^0-9+\-]", "", phone)
        if not phone:
            continue

        # Require numbers to start with +
        if not phone.startswith("+"):
            continue

        try:
            # Use the parse method to clean and analyze the number
            parsed = phonenumbers.parse(phone, None)

            # Wanting to be inclusive, just check if the number is 'possible', i.e. has correct format and length
            if phonenumbers.is_possible_number(parsed):
                # Format the number so all of them follow the same convention
                normalized = phonenumbers.format_number(
                    parsed, phonenumbers.PhoneNumberFormat.E164
                )
                phone_objects.append(
                    {
                        "phone": normalized,
                        "type": "office",
                    }
                )
        except phonenumbers.NumberParseException:
            # If parsing fails, the number is invalid, so we skip it and continue
            continue

    return phone_objects

# Normalize and validate emails with the email-validator package library
def get_valid_emails(emails):
    if not emails:
        return None

    email_objects = []

    # check for multiple emails, which are separated with a semicolon
    for raw_email in emails.split(";"):
        email = raw_email
        if not email:
            continue

        try:
            # check that the email is valid (does not actually test if active, though!)
            validated = validate_email(email, check_deliverability=False)
            #  use library's internal normalization function to return a database-ready string
            normalized_email = validated.email
            email_objects.append({"email": normalized_email, "type": "office"})
        except EmailNotValidError:
            # If validating fails, email is invalid, so we skip it and continue
            continue

    return email_objects

# Normalize and validate addresses
def get_valid_address(state):
    if not state:
        return None

    # Map the full state name to its proper equivalent
    condensed_state = STATE_MAP.get(state)
    if not condensed_state:
        return None

    addresses = [
        {
            "label": "business",
            "state": condensed_state,
            "country": "US",
        }
    ]
    return addresses

# turn the inputted date into proper iso formatted string
def get_valid_date(date):
    if not date or len(date) != 10:
        return None

    try:
        parsed = datetime.strptime(date, "%d.%m.%Y")
        return parsed.date().isoformat()
    except ValueError:
        # If string is not in the correct format, it is invalid so we return None
        return None


def get_valid_revenue(revenue):
    if not revenue:
        return None

    normalized = re.sub(r"[,$]", "", revenue)

    try:
        return float(normalized)
    except ValueError:
        # If we can't parse the float, it is invalid, so we return None
        return None