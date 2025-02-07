import configparser
import pathlib
import re
from datetime import timezone

import boto3
from botocore.exceptions import NoCredentialsError

AWS_REGION_NAME = "us-east-2"


# Function to prompt for input with a default value
def prompt_input(prompt, default_value=""):
    user_input = input(f"{prompt} (Default: {default_value}): ").strip()
    return user_input if user_input else default_value


# Check for required tools (AWS CLI equivalent setup)
try:
    boto3.setup_default_session()
except NoCredentialsError:
    print("AWS credentials not found. Please configure them first. Aborting.")
    exit(1)

# Prompt for AWS profile name
aws_profile = prompt_input("Enter your AWS profile name", "default")

# Set up the session with the specified profile
session = boto3.Session(profile_name=aws_profile, region_name=AWS_REGION_NAME)
iam_client = session.client("iam")
sts_client = session.client("sts")

# Fetch MFA devices
print("Fetching MFA devices...")


mfa_device_list = iam_client.list_mfa_devices()
mfa_devices = [
    device
    for device in mfa_device_list["MFADevices"]
    if re.match(r"^arn:aws:iam::[0-9]+:mfa/", device["SerialNumber"])
]

if not mfa_devices:
    print(
        "No compatible MFA devices found. Please set up a non-U2F MFA device for your IAM user."
    )

    exit(1)
elif len(mfa_devices) == 1:
    mfa_arn = mfa_devices[0]["SerialNumber"]

    print(f"Using MFA device: {mfa_arn}")
else:
    print("Select an MFA device:")

    for idx, device in enumerate(mfa_devices, start=1):
        print(f"{idx}) {device['SerialNumber']}")

    device_number = int(prompt_input("Enter the number of your MFA device"))
    mfa_arn = mfa_devices[device_number - 1]["SerialNumber"]
    print(f"Using MFA device: {mfa_arn}")

# Input MFA code
token_code = prompt_input("Enter your MFA code")

# Get temporary credentials
print("Fetching temporary credentials...")

max_duration_seconds = 129600  # 36 hours

creds = sts_client.get_session_token(
    SerialNumber=mfa_arn, TokenCode=token_code, DurationSeconds=max_duration_seconds
)["Credentials"]

# Prompt for a new profile name
default_mfa_profile = f"{aws_profile}-mfa"
mfa_profile = prompt_input("Enter a name for the new profile", default_mfa_profile)

# Read in the AWS credentials file
config = configparser.ConfigParser()
config.read(pathlib.Path("~/.aws/credentials").expanduser())

# Set values for `mfa` profile
config[mfa_profile] = {}
config[mfa_profile]["aws_access_key_id"] = creds["AccessKeyId"]
config[mfa_profile]["aws_secret_access_key"] = creds["SecretAccessKey"]
config[mfa_profile]["aws_session_token"] = creds["SessionToken"]
config[mfa_profile]["region"] = session.region_name

# Write the updated credentials file
with open(pathlib.Path("~/.aws/credentials").expanduser(), "w") as fp:
    config.write(fp)

# Get expiration time
expiration = creds["Expiration"].replace(tzinfo=timezone.utc)
expiration_local = expiration.astimezone()

# Final message
print("\nSuccess! Temporary credentials have been set up.")
print("---------------------------------------------")
print(f"Profile name: {mfa_profile}")
print(f"Expiration  : {expiration_local}\n")
print("To use these credentials:")
print(f"1. For specific commands: aws s3 ls --profile {mfa_profile}")
print(f"2. For this session: export AWS_PROFILE={mfa_profile}\n")
print("Remember to renew your credentials before they expire.")
