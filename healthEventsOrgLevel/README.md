# AWS Health Event Notification Script

## Overview
This Python script fetches upcoming AWS Health events at an organization level using AWS Health API and sends an email notification with event details using AWS Simple Email Service (SES).

## Features
- Retrieves upcoming AWS Health events for an AWS Organization.
- Fetches affected AWS accounts and their corresponding affected resources.
- Formats the event details into an HTML email.
- Sends the email notification using AWS SES.

## Prerequisites
1. **AWS IAM Permissions:** The script requires AWS credentials with appropriate permissions to use:
   - `AWSHealthFullAccess` or specific `health:DescribeEventsForOrganization` permissions.
   - `ses:SendEmail` permission for AWS SES.
2. **AWS SDK for Python (boto3):** Ensure `boto3` is installed:
   ```sh
   pip install boto3
   ```
3. **Verified SES Email Address:** Ensure that the sender email (`SENDER_EMAIL`) is verified in AWS SES.
4. **AWS Credentials:** Configure AWS credentials using `aws configure` or environment variables.

## Configuration
Edit the script to set the required values:
- `SENDER_EMAIL`: The verified email address from which notifications will be sent.
- `RECIPIENT_EMAIL`: The email address to receive notifications.
- `AWS Region`: Update SES and AWS Health API regions if needed.

## How It Works
1. The script fetches upcoming AWS Health events affecting the organization.
2. It retrieves the affected AWS accounts for each event.
3. For each account, it fetches affected resources.
4. The data is structured into an HTML email format.
5. The email is sent using AWS SES.

## Running the Script
To execute the script:
```sh
python healthEventsOrgLevel.py
```

## Example Email Output
The email contains:
- **Event Type**: AWS service impacting event.
- **Service**: The AWS service affected.
- **Region**: The impacted region (or Global if applicable).
- **Start Time**: The scheduled start time of the event.
- **Description**: A brief event description.
- **Affected Resources**: List of impacted AWS resources.

## Error Handling
- If AWS Health API calls fail, errors are printed to the console.
- If SES fails to send an email, an error message is logged.

## Future Enhancements
- Add support for filtering events based on services or severity.
- Integrate with a notification service like Slack or Teams.
- Store and track past events in a database.

## License
This script is provided "as-is" without any warranty. Modify and use it as needed.

## Author
Rahul Chaudhary