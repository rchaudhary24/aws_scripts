import boto3
import logging
import os

# AWS Clients
ENV = os.getenv('ENV')
health_client = boto3.client('health', region_name="us-east-1")
ses_client = boto3.client('ses', region_name='ap-southeast-2')  # Change if needed

# SES Configurations
SENDER_EMAIL = ""  # Replace with verified SES sender email
DEFAULT_RECIPIENT_EMAIL = ""  # Default recipient email

SUBJECT = f"AWS RDS {ENV} Account - LifeCycle Event"

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_rds_lifecycle_events():
    """Fetch upcoming AWS RDS Planned Lifecycle events."""
    response = health_client.describe_events(
        filter={"eventStatusCodes": ["upcoming"], "eventTypeCodes": ["AWS_RDS_PLANNED_LIFECYCLE_EVENT"]}
    )
    return response.get("events", [])

def get_affected_entities(event_arn):
    """Fetch affected resources for a given event."""
    response = health_client.describe_affected_entities(filter={"eventArns": [event_arn]})
    return [entity["entityValue"] for entity in response.get("entities", [])]

def get_event_description(event_arn):
    """Fetch detailed event description separately."""
    try:
        response = health_client.describe_event_details(eventArns=[event_arn])
        if response.get("successfulSet"):
            description_text = response["successfulSet"][0]["eventDescription"].get("latestDescription", "No details provided")
            return "<p><b>Event Description:</b></p><p>" + description_text.replace("\n", "<br>") + "</p>"
    except Exception as e:
        print(f"Error fetching event description: {e}")
    return "<p><b>Event Description:</b> No details provided.</p>"

def get_resource_tags(resource_arn, region):
    """Fetch the 'contact' tag for an RDS resource."""
    contact = "N/A"

    # Create RDS client for the region
    rds_client = boto3.client('rds', region_name=region)

    if ":rds:" in resource_arn:
        try:
            response = rds_client.list_tags_for_resource(ResourceName=resource_arn)
            tags = {tag['Key'].lower(): tag['Value'] for tag in response.get('TagList', [])}
            contact = tags.get("contact", "N/A")  # Fetch "contact" tag
        except Exception as e:
            print(f"Error fetching RDS tags for {resource_arn}: {e}")

    return contact

def format_html_message(events):
    """Format the AWS RDS events data into an HTML email, adding contacts to recipient list."""
    if not events:
        return "<p>No upcoming AWS RDS Planned Lifecycle Events.</p>", []  # Ensure two values are always returned

    distinct_contacts = set()
    event_descriptions = []
    table_header = """
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
        <thead>
            <tr>
                <th>Event</th>
                <th>Service</th>
                <th>Region</th>
                <th>Start Time</th>
                <th>Affected Resource</th>
                <th>Contact</th>
            </tr>
        </thead>
        <tbody>
    """
    
    table_rows = []

    for event in events:
        event_arn = event["arn"]
        event_region = event.get('region', 'us-east-1')  # Default to us-east-1 if missing
        affected_resources = get_affected_entities(event_arn)
        event_description = get_event_description(event_arn)  # Fetch event description
        event_descriptions.append(event_description)  # Store descriptions separately

        for resource in affected_resources:
            contact = get_resource_tags(resource, event_region)  # Get RDS contact tag

            # Add contact email to recipient list (if valid)
            if "@" in contact and "." in contact:
                distinct_contacts.add(contact)

            table_row = f"""
            <tr>
                <td>{event['eventTypeCode']}</td>
                <td>{event['service']}</td>
                <td>{event_region}</td>
                <td>{event.get('startTime', 'Unknown')}</td>
                <td>{resource}</td>
                <td>{contact}</td>
            </tr>
            """
            table_rows.append(table_row)

    table_footer = "</tbody></table>"
    description_section = "".join(event_descriptions)

    return description_section + table_header + "".join(table_rows) + table_footer, list(distinct_contacts)

def send_email(subject, body_html, recipient_list):
    """Send HTML email using AWS SES with multiple recipients."""
    try:
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': recipient_list},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': body_html}},
            }
        )
        print(f"Email sent! Message ID: {response['MessageId']} to {recipient_list}")
    except Exception as e:
        print(f"Error sending email: {e}")

def lambda_handler(event, context):
    events = get_rds_lifecycle_events()
    html_message, contact_list = format_html_message(events)

    # Add default recipient if no contacts found
    if not contact_list:
        contact_list.append(DEFAULT_RECIPIENT_EMAIL)

    send_email(SUBJECT, html_message, contact_list)

if __name__ == "__main__":
    lambda_handler([], [])
