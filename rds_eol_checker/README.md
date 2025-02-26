# AWS RDS End-of-Support (EOS) Notification Script

## Overview
This Python script fetches all RDS instances across AWS regions, determines their engine versions, and checks against predefined end-of-support (EOS) dates. It generates an HTML table highlighting instances that are approaching EOS and sends email notifications via AWS Simple Email Service (SES).

## Features
- Fetches RDS instances from all AWS regions.
- Extracts engine versions and maps them to predefined EOS dates.
- Identifies instances whose EOS is within the next 12 months.
- Highlights instances with EOS within 3 months in red.
- Sends formatted email notifications via AWS SES.
- Extracts contact email from instance tags (if available) to dynamically populate recipient lists.

## Prerequisites
1. Install required Python packages:
   ```sh
   pip install boto3 tabulate
   ```
2. Configure AWS credentials using `aws configure` or set up an appropriate IAM role.
3. Verify your sender email in AWS SES.
4. Ensure recipient emails are verified (if in AWS SES sandbox mode).

## Environment Variables
- `ENV`: Specifies the environment (e.g., `Production`, `Staging`).
- `SENDER_EMAIL`: The verified email address used for sending notifications.
- `AWS_REGION`: The AWS region where SES is configured.

## How It Works
1. **Fetch RDS Instances**: Queries all AWS regions for RDS instances and retrieves engine versions.
2. **Determine EOS Dates**: Checks the engine version against predefined EOS mappings.
3. **Generate Report**: Filters instances with EOS within 12 months and highlights those expiring in the next 3 months.
4. **Send Email Notification**: Formats the data into an HTML table and sends it via AWS SES.

## Usage
Run the script manually:
```sh
python rds_eol_checker.py
```

Schedule it as a cron job for periodic checks:
```sh
0 9 * * 1 python /path/to/rds_eol_checker.py  # Runs every Monday at 9 AM
```

## AWS IAM Permissions
Ensure the AWS IAM role or user executing this script has the following permissions:
```json
{
    "Effect": "Allow",
    "Action": [
        "rds:DescribeDBInstances",
        "rds:ListTagsForResource",
        "ses:SendEmail",
        "ec2:DescribeRegions"
    ],
    "Resource": "*"
}
```

## Customization
- Modify the `MYSQL_EOL`, `POSTGRES_EOL`, `AURORA_MYSQL_EOL`, and `AURORA_POSTGRES_EOL` dictionaries to update EOS dates.
- Update the email template in `send_email_with_table()` for custom formatting.

## Troubleshooting
- **Email not sent?** Ensure SES is set up correctly, and recipient emails are verified.
- **Instances missing?** Verify that the AWS credentials have `rds:DescribeDBInstances` access.
- **Incorrect EOS dates?** Check the `*_EOL` dictionaries for outdated values.

## License
This script is provided "as-is" without any warranty. Modify and use it as needed.

## Author
Rahul Chaudhary