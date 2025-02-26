# AWS RDS Lifecycle Event Notification

## Overview
This script is designed to monitor upcoming AWS RDS Planned Lifecycle Events using AWS Health APIs and notify relevant stakeholders via AWS Simple Email Service (SES). It fetches affected RDS resources, retrieves contact information from resource tags, and sends an HTML-formatted email to relevant recipients.

## Features
- Fetches upcoming AWS RDS Planned Lifecycle Events.
- Retrieves affected resources and their associated contact tags.
- Formats the event details into an HTML email.
- Sends the notification to the appropriate recipients using AWS SES.

## Prerequisites
### AWS Services Used:
- **AWS Health API**: To fetch upcoming AWS RDS lifecycle events.
- **AWS SES**: To send email notifications.
- **AWS RDS API**: To fetch resource tags for contact information.

### Requirements:
- Python 3.x
- `boto3` library installed (`pip install boto3`).
- AWS credentials configured with the necessary permissions:
  - `health:DescribeEvents`
  - `health:DescribeAffectedEntities`
  - `health:DescribeEventDetails`
  - `rds:ListTagsForResource`
  - `ses:SendEmail`
- Verified sender email address in AWS SES.

## Environment Variables
- `ENV`: Specifies the environment (e.g., `production`, `staging`, `dev`).
- `SENDER_EMAIL`: AWS SES verified email for sending notifications.
- `DEFAULT_RECIPIENT_EMAIL`: Default email address if no contacts are found.

## Installation & Configuration
1. Install dependencies:
   ```sh
   pip install boto3
   ```
2. Set up AWS credentials (using `aws configure` or environment variables).
3. Update the script with the correct SES sender email and default recipient email.
4. Deploy the script as an AWS Lambda function or run it locally.

## Execution
### Running Locally:
```sh
python rds_lifecycle_events.py
```

### Running as AWS Lambda:
- Deploy the script as a Lambda function.
- Set up an event trigger (e.g., CloudWatch scheduled event) to invoke it periodically.

## How It Works
1. **Fetch RDS Lifecycle Events**: Queries AWS Health API for upcoming RDS lifecycle events.
2. **Retrieve Affected Resources**: Extracts impacted RDS instances from the event details.
3. **Fetch Resource Tags**: Checks for a `contact` tag in RDS resources to determine recipients.
4. **Format Email Notification**: Constructs an HTML-formatted email with event details.
5. **Send Email via AWS SES**: Sends notifications to identified contacts or a default recipient.

## Example Email Output
```
Subject: AWS RDS Production Account - LifeCycle Event

Body:
<h2>AWS RDS Planned Lifecycle Events</h2>
<table>
    <tr>
        <th>Event</th><th>Service</th><th>Region</th><th>Start Time</th><th>Affected Resource</th><th>Contact</th>
    </tr>
    <tr>
        <td>AWS_RDS_MAINTENANCE</td><td>rds</td><td>us-east-1</td><td>2025-03-10 12:00 UTC</td><td>rds-instance-1234</td><td>admin@example.com</td>
    </tr>
</table>
```

## Error Handling
- If no affected resources are found, an email stating "No upcoming AWS RDS Planned Lifecycle Events" is sent.
- If fetching event details or resource tags fails, the error is logged and a default recipient is notified.

## Customization
- Modify `get_resource_tags()` to fetch additional tags.
- Update `format_html_message()` to adjust the email structure.
- Change `DEFAULT_RECIPIENT_EMAIL` based on your organization's notification requirements.

## License
This script is released under the MIT License.