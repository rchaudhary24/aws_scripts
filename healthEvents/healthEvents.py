import boto3
import json
import logging
import os

# AWS Clients
#session = boto3.Session(profile_name="AdminRole-526424395864")
ENV = os.getenv('ENV')
health_client = boto3.client('health', region_name="us-east-1")
ses_client = boto3.client('ses', region_name='ap-southeast-2')  # Change if needed

# SES Configurations
SENDER_EMAIL = "aws-alerts@symbio.global"  # Replace with verified SES sender email
DEFAULT_RECIPIENT = "symbio_core_cloud@mnfgroup.limited"  # Default recipient

SUBJECT = f"AWS {ENV} Health Dashboard - Upcoming Events"

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def get_upcoming_events():
    """Fetch upcoming AWS Health events and exclude RDS lifecycle events."""
    response = health_client.describe_events(
        filter={"eventStatusCodes": ["upcoming"]}
    )
    events = response.get("events", [])
    
    # Exclude RDS lifecycle maintenance events
    filtered_events = [event for event in events if not event["eventTypeCode"].startswith("AWS_RDS_PLANNED_LIFECYCLE_EVENT")]
    
    return filtered_events

def get_affected_entities(event_arn):
    """Fetch affected resources for a given event."""
    response = health_client.describe_affected_entities(
        filter={"eventArns": [event_arn]}
    )
    return [entity["entityValue"] for entity in response.get("entities", [])]

def get_event_description(event_arn):
    """Fetch detailed event description for a given event."""
    try:
        response = health_client.describe_event_details(
            eventArns=[event_arn]
        )
        if response.get("successfulSet"):
            return response["successfulSet"][0]["eventDescription"].get("latestDescription", "No details provided")
    except Exception as e:
        print(f"Error fetching event description: {e}")
    return "No details provided"

def get_event_tags(event_arn):
    """Fetch tags for a given event and extract the contact email."""
    try:
        response = health_client.describe_event_details(
            eventArns=[event_arn]
        )
        if response.get("successfulSet"):
            tags = response["successfulSet"][0].get("tags", {})
            return tags.get("contact", DEFAULT_RECIPIENT)  # Default to Rahul's email if not found
    except Exception as e:
        print(f"Error fetching event tags: {e}")
    return DEFAULT_RECIPIENT

def format_html_message(events):
    """Format the AWS Health events data into an HTML table and a separate event description section."""
    if not events:
        return "<p>No upcoming AWS RDS Planned Lifecycle Events.</p>", []  # Ensure two values are always returned

    message_body = """
    <p>Dear Team,</p>
    <p>Please find below the upcoming AWS Health events that may impact our infrastructure.</p>
    <p>Take necessary actions if required.</p>
    """

    # Table for events
    table_header = """
    <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
        <thead>
            <tr>
                <th>Event</th>
                <th>Service</th>
                <th>Region</th>
                <th>Start Time</th>
                <th>Affected Resources</th>
                <th>Contact</th>
            </tr>
        </thead>
        <tbody>
    """
    
    table_rows = []
    event_descriptions = []
    recipient_emails = {DEFAULT_RECIPIENT}  # Use a set to ensure unique emails

    for event in events:
        event_arn = event["arn"]
        affected_resources = get_affected_entities(event_arn)
        event_description = get_event_description(event_arn)  # Fetch description
        contact_email = get_event_tags(event_arn)  # Fetch "contact" tag

        recipient_emails.add(contact_email)  # Add unique contacts to recipient list

        # Handle cases where no affected resources are found
        if not affected_resources:
            affected_resources = ["None"]

        # Create table rows, each affected resource gets its own row
        for idx, resource in enumerate(affected_resources):
            table_row = f"""
            <tr>
                <td>{event['eventTypeCode'] if idx == 0 else ''}</td>
                <td>{event['service'] if idx == 0 else ''}</td>
                <td>{event.get('region', 'Global') if idx == 0 else ''}</td>
                <td>{event.get('startTime', 'Unknown') if idx == 0 else ''}</td>
                <td>{resource}</td>
                <td>{contact_email if idx == 0 else ''}</td>
            </tr>
            """
            table_rows.append(table_row)

        # Add event description separately
        event_descriptions.append(f"""
        <p><strong>--- Event ---</strong></p>
        <p><strong>Event Type:</strong> {event['eventTypeCode']}</p>
        <p><strong>Service:</strong> {event['service']}</p>
        <p><strong>Region:</strong> {event.get('region', 'Global')}</p>
        <p><strong>Start Time:</strong> {event.get('startTime', 'Unknown')}</p>
        <p><strong>Description:</strong> {event_description}</p>
        """)

    table_footer = "</tbody></table>"

    closing_message = """
    <p>For further details, please check the AWS Health Dashboard or reach out to the relevant contacts.</p>
    <p>Best Regards,<br>Cloud Platform Team</p>
    """

    # Combine everything
    return message_body + table_header + "".join(table_rows) + table_footer + "".join(event_descriptions) + closing_message, list(recipient_emails)

def send_email(subject, body_html, recipients):
    """Send HTML email using AWS SES."""
    try:
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': recipients},  # Send to all distinct recipients
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': body_html}},
            }
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
    except Exception as e:
        print(f"Error sending email: {e}")

def lambda_handler(event, context):
    events = get_upcoming_events()
    html_message, recipients = format_html_message(events)
    send_email(SUBJECT, html_message, recipients)

if __name__ == "__main__":
    lambda_handler([], [])
