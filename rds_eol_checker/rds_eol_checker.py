import boto3
import datetime
from tabulate import tabulate
from datetime import datetime as dt
import logging
import os

# Define AWS SES settings (Optional)
#session = boto3.Session(profile_name="AdminRole-526424395864")
ENV = os.getenv('ENV')
SENDER_EMAIL = ""  # Replace with your verified sender email
RECIPIENT_EMAILS = {""}  # Set to a set for uniqueness
AWS_REGION = "ap-southeast-2"  # Replace with your region
SUBJECT = f"AWS RDS {ENV} Account - End-of-Support Status"

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

from botocore.exceptions import ClientError
from urllib.parse import unquote

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# MySQL Standard Support End Dates (From AWS Docs)
MYSQL_EOL = {
    "5.7.44": "2025-03-01",
    "8.0.34": "2025-03-01",
    "8.0.35": "2025-03-01",
    "8.0.36": "2025-03-01",
    "8.0.37": "2025-09-01",
    "8.0.39": "2025-09-01",
    "8.0.40": "2026-03-01",
    "8.4.3": "2026-03-01",
}

# PostgreSQL Standard Support End Dates (Major and Minor Versions)
POSTGRES_EOL = {
    "16.5": "2026-03-01","16.4": "2025-09-01","16.3": "2025-09-01","16.2": "2025-03-31","16.1": "2025-03-31",
    "15.1": "2026-03-01","15.9": "2026-03-01","15.8": "2025-09-01","15.7": "2025-09-01","15.6": "2025-03-31","15.5": "2025-03-31","15.4": "2025-03-31",
    "14.15": "2026-03-01","14.14": "2026-03-01","14.13": "2025-09-01","14.12": "2025-09-01","14.11": "2025-03-31","14.1": "2025-03-31","14.9": "2025-03-31",
    "13.18": "2026-02-28","13.17": "2026-02-28","13.16": "2025-09-01","13.15": "2025-09-01","13.14": "2025-03-31","13.13": "2025-03-31","13.12": "2025-03-31","13.11": "2025-03-31",
    "12.22": "2025-02-28","12.21": "2025-02-28","12.2": "2025-02-28","12.19": "2025-02-28","12.18": "2025-02-28","12.17": "2025-02-28","12.16": "2025-02-28","12.15": "2025-02-28",
}
# Aurora MySQL Standard Support End Dates (Major and Minor Versions)
AURORA_MYSQL_EOL = {
    "5.7.mysql_aurora.2.12.2": "2024-10-31",
    "5.7.mysql_aurora.2.11.5": "2024-10-31",
    "5.7.mysql_aurora.2.11.2": "2024-10-31",
    "8.0.mysql_aurora.3.08.0": "2027:04:30",
    "8.0.mysql_aurora.3.07.0": "2027:04:30",
    "8.0.mysql_aurora.3.06.0": "2027:04:30",
    "8.0.mysql_aurora.3.05.2": "2027:04:30",
    "8.0.mysql_aurora.3.05.0": "2027:04:30",
    "8.0.mysql_aurora.3.04.0": "2027:04:30"
}

# Aurora PostgreSQL Standard Support End Dates (Major and Minor Versions)
AURORA_POSTGRES_EOL = {
    "16.6": "2026-05-31","16.4": "2026-05-01","16.3": "2025-10-01","16.2": "2025-10-01","16.1": "2025-10-01",
    "15.1": "2026-05-31","15.8": "2026-05-01","15.7": "2025-10-01","15.6": "2025-10-01","15.5": "2025-05-01","15.4": "2025-05-01","15.3": "2025-05-01","15.2": "2024-11-15",
    "14.15": "2026-05-31","14.13": "2026-05-01","14.12": "2025-10-01","14.11": "2025-10-01","14.1": "2025-05-01","14.9": "2025-05-01",
    "14.8": "2025-05-01","14.7": "2024-11-15","14.6": "2027-02-28","14.5": "2024-11-15","14.4": "2024-11-15","14.3": "2024-11-15",
    "13.18": "2026-02-28","13.16": "2026-02-28","13.15": "2025-10-01","13.14": "2025-10-01",
    "13.13": "2025-05-01","13.12": "2025-05-01","13.11": "2025-05-01","13.1": "2024-11-15","13.9": "2026-02-28","13.8": "2024-11-15","13.7": "2024-11-15",
    "12.22": "2025-02-28","12.2": "2025-02-28",
    "12.19": "2025-02-28","12.18": "2025-02-28","12.17": "2025-02-28","12.16": "2025-02-28","12.15": "2025-02-28","12.14": "2024-11-15","12.13": "2024-11-15","12.12": "2024-11-15","12.11": "2024-11-15","12.9": "2025-02-28"
}

# Function to fetch RDS instances across all AWS regions
def get_rds_instances():
    """Fetch all RDS instances, including their tags, and return their details."""
    client = boto3.client("ec2")
    regions = [region["RegionName"] for region in client.describe_regions()["Regions"]]

    rds_instances = []
    for region in regions:
        rds_client = boto3.client("rds", region_name=region)
        response = rds_client.describe_db_instances()

        for instance in response["DBInstances"]:
            instance_id = instance["DBInstanceIdentifier"]
            
            # Fetch instance tags
            tags_response = rds_client.list_tags_for_resource(
                ResourceName=instance["DBInstanceArn"]
            )
            tags = {tag["Key"]: tag["Value"] for tag in tags_response.get("TagList", [])}
            contact_email = tags.get("contact", "Unknown")  # Extract 'contact' tag

            # Store instance details
            rds_instances.append({
                "DBInstanceIdentifier": instance_id,
                "Engine": instance["Engine"],
                "EngineVersion": instance["EngineVersion"],  # Get full version (major + minor)
                "Region": region,
                "Contact": contact_email,  # Add contact tag
            })

            # Add contact to recipient list if it's a valid email
            if "@" in contact_email:
                RECIPIENT_EMAILS.add(contact_email)

    return rds_instances

# Function to get End-of-Support date for an engine/version
def get_eol(engine, version):
    """Return the end-of-support date for a given engine and version."""
    EOL_MAPPINGS = {
        "mysql": MYSQL_EOL,
        "postgres": POSTGRES_EOL,
        "aurora-mysql": AURORA_MYSQL_EOL,
        "aurora-postgresql": AURORA_POSTGRES_EOL,
    }
    return EOL_MAPPINGS.get(engine, {}).get(version, "Unknown")

# Function to create the table of instances with their engine version, EOL date, and contact
def create_rds_table(instances):
    """Create a formatted table of RDS instances with engine version, EOL date, and contact."""
    today = datetime.date.today()
    one_year_later = today + datetime.timedelta(days=365)  # 12 months from today
    table = []

    for instance in instances:
        engine = instance["Engine"]
        version = instance["EngineVersion"]
        region = instance["Region"]
        contact = instance["Contact"]

        # Get EOL date for each engine/version
        eos_date = get_eol(engine, version)

        # Normalize date format if necessary (e.g., 2027:04:30 -> 2027-04-30)
        if eos_date != "Unknown":
            eos_date = eos_date.replace(":", "-")  # Replace colon with dash if needed
            eos_date_dt = dt.strptime(eos_date, "%Y-%m-%d").date()
            
            # **Exclude instances whose EOS is more than 12 months away**
            if eos_date_dt > one_year_later:
                continue  # Skip this instance
            
            # Highlight EOL < 3 months in red
            if eos_date_dt < today + datetime.timedelta(days=90):
                eos_date = f"<span style='color:red;'>{eos_date}</span>"

        table.append([instance["DBInstanceIdentifier"], engine, version, eos_date, contact])

    return table

# Function to send email with table via SES
def send_email_with_table(table, recipient_emails):
    """Send the RDS table via AWS SES with an alert message and proper HTML formatting."""
    
    today = datetime.date.today()
    
    # Construct HTML table with proper formatting
    table_html = """
    <table border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse; width: 100%;">
        <thead>
            <tr style="background-color: #f2f2f2;">
                <th>DB Instance Identifier</th>
                <th>Engine</th>
                <th>Version</th>
                <th>End of Support Date</th>
                <th>Contact</th>
            </tr>
        </thead>
        <tbody>
    """
    
    for row in table:
        db_instance, engine, version, eos_date, contact = row
        
        # Convert EOS date to datetime object for comparison
        try:
            eos_date_dt = dt.strptime(eos_date, "%Y-%m-%d") if eos_date != "Unknown" else None
        except ValueError:
            eos_date_dt = None  # Handle invalid date formats
        
        # Check if EOS date is within 3 months
        if eos_date_dt and eos_date_dt.date() < today + datetime.timedelta(days=90):
            row_color = " style='color: red; font-weight: bold;'"  # Highlight in red
        else:
            row_color = ""

        table_html += f"""
            <tr>
                <td>{db_instance}</td>
                <td>{engine}</td>
                <td>{version}</td>
                <td{row_color}>{eos_date}</td>
                <td>{contact}</td>
            </tr>
        """

    table_html += """
        </tbody>
    </table>
    """

    # Email message body
    message_body = f"""
    <html>
    <body>
        <p><strong>Alert:</strong> The following AWS RDS instances are approaching their End-of-Support (EOS) date.</p>
        <p>Instances with EOS less than <strong>3 months</strong> are highlighted in <span style="color:red;">red</span>.</p>
        {table_html}
        <p><strong>Action Required:</strong> Please review these instances and plan necessary upgrades before the support ends.</p>
        <p>Regards,</p>
        <p><strong>CLoud Alerts</strong></p>
    </body>
    </html>
    """

    # Convert recipient set to list
    recipient_list = list(recipient_emails)

    # Create SES client
    ses_client = boto3.client("ses", region_name=AWS_REGION)

    # Send email
    response = ses_client.send_email(
        Source=SENDER_EMAIL,
        Destination={
            "ToAddresses": recipient_list,
        },
        Message={
            "Subject": {
                "Data": SUBJECT,
            },
            "Body": {
                "Html": {
                    "Data": message_body,
                },
            },
        },
    )

    print(f"Email sent! Message ID: {response['MessageId']}")




def lambda_handler(event, context):
    # Fetch RDS instances
    instances = get_rds_instances()

    # Create RDS table
    rds_table = create_rds_table(instances)
    
    if rds_table:  # Only send email if the list is not empty
        send_email_with_table(rds_table, RECIPIENT_EMAILS)  # Your function to send the email
    else:
        print("✅ No unsupported RDS instances found. Skipping email.")

    # Send the table via email to all collected recipients
    #send_email_with_table(rds_table, RECIPIENT_EMAILS)

if __name__ == "__main__":
    lambda_handler([], [])