# AWS Lambda Deprecated Runtime Checker

## Overview
This Python script scans AWS Lambda functions across specified regions and identifies those using deprecated or soon-to-be deprecated runtimes. It generates an HTML report and optionally sends it via AWS Simple Email Service (SES).

## Features
- Retrieves all Lambda functions and their runtimes across multiple AWS regions.
- Identifies functions using deprecated or soon-to-be deprecated runtimes.
- Extracts metadata such as contact, team, and business unit from function tags.
- Generates an HTML report detailing affected functions.
- Sends an email notification with the report using AWS SES.

## Prerequisites
1. **AWS Credentials:** Configure AWS credentials using `aws configure` or set up IAM roles if running in AWS Lambda.
2. **Python Dependencies:** Install `boto3` using:
   ```sh
   pip install boto3
   ```
3. **AWS SES Setup:** Ensure that the sender email is verified in AWS SES for successful email delivery.
4. **Permissions:**
   - `AWSLambda_ReadOnlyAccess`
   - `SESSendEmail` (if email functionality is used)

## Configuration
- **Modify Regions:** Update the `regions` list in `lambda_handler()` to scan desired AWS regions.
- **Set Email Recipients:** Replace `recipient_email` and `sender_email` with valid email addresses.
- **Adjust Soon-to-Be Deprecated Runtimes:** Modify the `SOON_TO_BE_DEPRECATED` list as needed.

## Usage
### Run Locally
To execute the script from your local environment:
```sh
python lambda_deprecated_checker.py
```
### Deploy as AWS Lambda
- Package and upload the script to an AWS Lambda function.
- Configure Lambda execution role with the necessary IAM permissions.
- Set up an EventBridge rule to trigger the function periodically.

## Output
- **Console Output:** Displays identified deprecated Lambda functions.
- **HTML Report:** A formatted report detailing affected functions.
- **Email Notification:** Sends the report to the configured recipient via AWS SES.

## Example Output
A sample of the HTML report output:
```html
<table>
    <tr>
        <th>Function Name</th><th>Runtime</th><th>Region</th><th>Contact</th><th>Team</th><th>Business Unit</th><th>Deprecated Status</th>
    </tr>
    <tr>
        <td>MyLambdaFunction</td><td>python3.8</td><td>us-east-1</td><td>John Doe</td><td>DevOps</td><td>Engineering</td><td>Deprecated</td>
    </tr>
</table>
```

## License
This script is provided "as-is" without any warranty. Modify and use it as needed.

## Author
Rahul Chaudhary