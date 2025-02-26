import boto3
from botocore.exceptions import NoCredentialsError, ClientError

#session = boto3.Session(profile_name="AdminRole-526424395864")

# AWS Lambda Supported and Deprecated Runtimes - https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html
SUPPORTED_RUNTIMES = [
    "nodejs22.x", "nodejs20.x", "nodejs18.x",
    "python3.13", "python3.12", "python3.11", "python3.10", "python3.9",
    "java21", "java17", "java11",
    ".NET 8", "ruby3.3", "ruby3.2"
]

DEPRECATED_RUNTIMES = [
    ".NET 6", "python3.8", "nodejs16.x", ".NET 7 (container only)", "java8", "go1.x",
    "OS-only Runtime", "ruby2.7", "nodejs14.x", "python3.7", "dotnetcore3.1", "nodejs12.x",
    "python3.6", ".NET 5 (container only)", "dotnetcore2.1", "nodejs10.x", "ruby2.5",
    "python2.7", "nodejs8.10", "nodejs4.3", "nodejs4.3-edge", "nodejs6.10",
    "dotnetcore1.0", "dotnetcore2.0", "nodejs0.10"
]

SOON_TO_BE_DEPRECATED = [
    "python3.9", "java8"  # Add any runtime set to deprecate in the next 6 months
]

def get_lambda_functions(region):
    """Fetch all Lambda functions in a region and their details."""
    client = boto3.client("lambda", region_name=region)
    deprecated_list = []
    soon_deprecated_list = []
    
    paginator = client.get_paginator("list_functions")
    for page in paginator.paginate():
        for function in page["Functions"]:
            function_name = function["FunctionName"]
            function_arn = function["FunctionArn"]
            runtime = function.get("Runtime", "Unknown")

            # Fetch tags: contact, team, business unit
            contact, team, business_unit = get_lambda_tags(client, function_arn)

            if runtime in DEPRECATED_RUNTIMES:
                deprecated_list.append((function_name, runtime, region, contact, team, business_unit, "Deprecated"))
            elif runtime in SOON_TO_BE_DEPRECATED:
                soon_deprecated_list.append((function_name, runtime, region, contact, team, business_unit, "Soon to be Deprecated"))

    return deprecated_list, soon_deprecated_list

def get_lambda_tags(client, function_arn):
    """Fetches 'contact', 'team', and 'businessunit' tags for a Lambda function."""
    try:
        response = client.list_tags(Resource=function_arn)
        tags = response.get("Tags", {})

        contact = tags.get("contact") or tags.get("mnfgroup:contact") or "N/A"
        team = tags.get("team") or tags.get("mnfgroup:team") or "N/A"
        business_unit = tags.get("businessunit") or "N/A"

        return contact, team, business_unit

    except ClientError as e:
        print(f"Error fetching tags for {function_arn}: {e}")
        return "N/A", "N/A", "N/A"

def generate_html_report(deprecated, soon_deprecated):
    """Generates an HTML report for deprecated and soon-to-be-deprecated Lambda functions."""
    html = """
    <html>
    <head>
        <style>
            table { width: 100%%; border-collapse: collapse; }
            th, td { border: 1px solid black; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
        </style>
    </head>
    <body>
        <h2>Attention: Deprecated AWS Lambda Runtimes Detected</h2>
        <p>The following Lambda functions are using deprecated or soon-to-be-deprecated runtimes. Please update them as soon as possible to ensure continued functionality and security.</p>
        <h3>Lambda Functions Using Deprecated Runtimes</h3>
        <table>
            <tr>
                <th>Function Name</th><th>Runtime</th><th>Region</th><th>Contact</th><th>Team</th><th>Business Unit</th><th>Deprecated Status</th>
            </tr>
    """
    for fn, rt, reg, contact, team, business_unit, status in deprecated:
        html += f"<tr><td>{fn}</td><td>{rt}</td><td>{reg}</td><td>{contact}</td><td>{team}</td><td>{business_unit}</td><td>{status}</td></tr>"

    html += """
        </table>
        <h3>Lambda Functions Using Soon-To-Be Deprecated Runtimes</h3>
        <table>
            <tr>
                <th>Function Name</th><th>Runtime</th><th>Region</th><th>Contact</th><th>Team</th><th>Business Unit</th><th>Deprecated Status</th>
            </tr>
    """
    for fn, rt, reg, contact, team, business_unit, status in soon_deprecated:
        html += f"<tr><td>{fn}</td><td>{rt}</td><td>{reg}</td><td>{contact}</td><td>{team}</td><td>{business_unit}</td><td>{status}</td></tr>"

    html += """
        </table>
        <p><strong>Action Required:</strong> Please update the deprecated Lambda functions to a supported runtime as soon as possible to avoid service disruptions.</p>
    </body>
    </html>
    """
    return html

def send_email(html_report, recipient_email, sender_email, region="ap-southeast-2"):
    """Sends the HTML report via AWS SES."""
    client = boto3.client("ses", region_name=region)

    try:
        response = client.send_email(
            Source=sender_email,
            Destination={"ToAddresses": [recipient_email]},
            Message={
                "Subject": {"Data": "AWS Lambda Deprecated Runtime Report"},
                "Body": {"Html": {"Data": html_report}},
            },
        )
        print(" Email sent successfully!")
    except NoCredentialsError:
        print(" AWS credentials not found!")
    except ClientError as e:
        print(f" Error sending email: {e}")

def lambda_handler(event, context):
    regions = ["ap-southeast-2", "ap-southeast-1","us-east-1"]  # Add required regions
    all_deprecated = []
    all_soon_deprecated = []

    for region in regions:
        print(f"🔍 Scanning region: {region} ...")
        deprecated, soon_deprecated = get_lambda_functions(region)
        all_deprecated.extend(deprecated)
        all_soon_deprecated.extend(soon_deprecated)

    if not all_deprecated and not all_soon_deprecated:
        print("\n No deprecated Lambda functions found.")
        return

    html_report = generate_html_report(all_deprecated, all_soon_deprecated)

    # Replace with actual email addresses
    recipient_email = "rahul.chaudhary@symbio.global"
    sender_email = "no-reply@symbio.global"
    send_email(html_report, recipient_email, sender_email)

if __name__ == "__main__":
    lambda_handler([], [])
