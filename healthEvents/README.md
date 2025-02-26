# AWS Health Event Notification Script

## Overview
This Python script fetches upcoming AWS Health events, filters out RDS lifecycle events, and sends a formatted HTML email notification using AWS Simple Email Service (SES). The email includes an HTML table summarizing the events and details about affected resources.

## Features
- Fetches upcoming AWS Health events using AWS Health API.
- Filters out AWS RDS Planned Lifecycle Events.
- Retrieves affected entities and event descriptions.
- Extracts event-specific contacts from AWS Health tags.
- Formats event details into an HTML email.
- Sends notifications using AWS SES to relevant recipients.

## Prerequisites
### AWS Services Used
- **AWS Health API** (for fetching event details)
- **AWS SES** (for sending email notifications)
- **AWS Lambda** (if running the script as a serverless function)

### AWS Permissions Required
Ensure the IAM role or user running the script has the following permissions:
```json
{
    "Effect": "Allow",
    "Action": [
        "health:DescribeEvents",
        "health:DescribeAffectedEntities",
        "health:DescribeEventDetails",
        "ses:SendEmail",
        "ses:SendRawEmail"
    ],
    "Resource": "*"
}
```

## Installation & Setup
1. Install dependencies (if running locally):
   ```sh
   pip install boto3
   ```
2. Configure AWS credentials using environment variables or `~/.aws/credentials`.
3. Set up SES with a verified sender email.

## Configuration
### Environment Variables
- `ENV`: Deployment environment (used in email subject)
- `SENDER_EMAIL`: Verified AWS SES sender email
- `DEFAULT_RECIPIENT`: Default email recipient

### Modify Script for Customization
- Update `region_name` in `boto3.client('ses', region_name='ap-southeast-2')` if needed.
- Replace `SENDER_EMAIL` and `DEFAULT_RECIPIENT` with actual values.

## Usage
### Running Locally
```sh
python healthEvents.py
```

### Running as AWS Lambda
1. Zip and upload the script as a Lambda function.
2. Configure the Lambda function with appropriate IAM permissions and environment variables.
3. Set up a CloudWatch event trigger for periodic execution.

## Troubleshooting
- **SES Email Not Sent?**
  - Ensure the sender email is verified in AWS SES.
  - If in sandbox mode, verify recipient emails as well.
  - Check IAM permissions for `ses:SendEmail`.
- **AWS Health Events Not Found?**
  - Ensure AWS Health API is enabled for the account.
  - Check IAM permissions for `health:DescribeEvents`.

## License
This script is provided "as-is" without any warranty. Modify and use it as needed.

## Author
Rahul Chaudhary

