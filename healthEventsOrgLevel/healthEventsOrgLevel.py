import boto3
import json
from datetime import datetime, timezone

# AWS Clients
health_client = boto3.client('health', region_name="us-east-1")
ses_client = boto3.client('ses', region_name='ap-southeast-2')  # Change if necessary

SENDER_EMAIL = ""  # Replace with your verified sender email
RECIPIENT_EMAIL = ""  # Replace with recipient email

def get_organization_events():
    """Fetch upcoming AWS Health events at the organization level."""
    response = health_client.describe_events_for_organization(
        filter={"eventStatusCodes": ["upcoming"]}
    )
    return response.get("events", [])

def get_affected_accounts(event_arn):
    """Fetch affected AWS accounts for a given event."""
    response = health_client.describe_affected_accounts_for_organization(
        eventArn=event_arn
    )
    return response.get("affectedAccounts", [])

def get_affected_entities(event_arn, account_id):
    """Fetch affected resources for a given event and account."""
    response = health_client.describe_affected_entities_for_organization(
        organizationEntityFilters=[{"eventArn": event_arn, "awsAccountId": account_id}]
    )
    return [entity["entityValue"] for entity in response.get("entities", [])]

def format_html_message(events):
    """Format the email message in HTML, grouping by account."""
    if not events:
        return "<p>No upcoming AWS Health events.</p>"

    account_events = {}

    # Organize events per account
    for event in events:
        event_arn = event["arn"]
        affected_accounts = get_affected_accounts(event_arn)

        for account_id in affected_accounts:
            if account_id not in account_events:
                account_events[account_id] = []

            affected_resources = get_affected_entities(event_arn, account_id)
            resources_list = ', '.join(affected_resources) if affected_resources else "None"

            account_events[account_id].append({
                "EventTypeCode": event["eventTypeCode"],
                "Service": event["service"],
                "Region": event.get("region", "Global"),
                "StartTime": event.get("startTime", "Unknown"),
                "Description": event.get("eventDescription", "No details provided"),
                "AffectedResources": resources_list
            })

    # Generate HTML tables per account
    html_body = "<h2>AWS Health Dashboard - Upcoming Events</h2>"

    for account_id, event_list in account_events.items():
        html_body += f"<h3>Affected Account: {account_id}</h3>"
        html_body += """
        <table border="1" cellpadding="5" cellspacing="0" style="border-collapse: collapse; width: 100%;">
            <thead>
                <tr>
                    <th>Event</th>
                    <th>Service</th>
                    <th>Region</th>
                    <th>Start Time</th>
                    <th>Description</th>
                    <th>Affected Resources</th>
                </tr>
            </thead>
            <tbody>
        """

        for event in event_list:
            html_body += f"""
            <tr>
                <td>{event['EventTypeCode']}</td>
                <td>{event['Service']}</td>
                <td>{event['Region']}</td>
                <td>{event['StartTime']}</td>
                <td>{event['Description']}</td>
                <td>{event['AffectedResources']}</td>
            </tr>
            """

        html_body += "</tbody></table><br>"

    return html_body

def send_email(subject, body_html):
    """Send HTML email using SES."""
    try:
        response = ses_client.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [RECIPIENT_EMAIL]},
            Message={
                'Subject': {'Data': subject},
                'Body': {'Html': {'Data': body_html}},
            }
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    events = get_organization_events()
    html_message = format_html_message(events)
    send_email("AWS Health Dashboard - Organizational Events", html_message)

if __name__ == "__main__":
    main()
