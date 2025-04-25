#!/bin/bash

AWS_REGION_NAME="us-east-2"

# Enable debug mode with a flag
DEBUG=false

# Debug logging function
debug_log() {
    if [ "$DEBUG" = true ]; then
        echo "[DEBUG] $1"
    fi
}

# Function to prompt for input with a default value
prompt_input() {
    local prompt="$1"
    local default_value="$2"

    read -p "$prompt (Default: $default_value): " user_input
    echo "${user_input:-$default_value}"
}

# Function to prompt for required input (no default)
prompt_required() {
    local prompt="$1"
    local input=""

    while [ -z "$input" ]; do
        read -p "$prompt: " input
    done

    echo $input
}

# Function to prompt for yes/no input
prompt_yes_no() {
    local prompt="$1"

    while true; do
        read -p "$prompt (y/n): " yn
        case $yn in
            [Yy]* ) return 0;;
            [Nn]* ) return 1;;
            * ) echo "Please answer yes or no.";;
        esac
    done
}

# Check for required tools
if ! command -v aws &> /dev/null; then
    echo "AWS CLI not found. Please install it first. Aborting."
    exit 1
fi

# Prompt for AWS profile name
aws_profile=$(prompt_input "Enter your AWS profile name" "default")
debug_log "Using AWS profile: $aws_profile"

# Set AWS profile and region
export AWS_PROFILE="$aws_profile"
export AWS_REGION="$AWS_REGION_NAME"
debug_log "Set AWS_PROFILE=$AWS_PROFILE and AWS_REGION=$AWS_REGION"

# Fetch MFA devices
echo "Fetching MFA devices..."

# First, get raw MFA device list for debugging
raw_mfa_list=$(aws iam list-mfa-devices --output json)
debug_log "Raw MFA device list: $raw_mfa_list"

# Now get filtered list with the query
mfa_device_list=$(aws iam list-mfa-devices --query "MFADevices[?contains(SerialNumber, 'arn:aws:iam:')].SerialNumber" --output text)
debug_log "Filtered MFA device list: $mfa_device_list"

# Try alternative query if nothing was found
if [ -z "$mfa_device_list" ]; then
    debug_log "No devices found with first query, trying without filter"
    mfa_device_list=$(aws iam list-mfa-devices --query "MFADevices[].SerialNumber" --output text)
    debug_log "All MFA devices: $mfa_device_list"
fi

# Check if we got any devices
if [ -z "$mfa_device_list" ]; then
    echo "No MFA devices found. Please set up an MFA device for your IAM user."
    exit 1
fi

# Create array of MFA devices
mfa_device_array=()
while read -r line; do
    if [ ! -z "$line" ]; then
        mfa_device_array+=("$line")
        debug_log "Added MFA device to array: $line"
    fi
done <<< "$mfa_device_list"

# Find out how many MFA devices we have
device_count=${#mfa_device_array[@]}
debug_log "Found $device_count MFA device(s)"

if [ $device_count -eq 0 ]; then
    echo "No MFA devices found in array. Please set up an MFA device for your IAM user."
    exit 1
elif [ $device_count -eq 1 ]; then
    mfa_arn="${mfa_device_array[0]}"
    echo "Using MFA device: $mfa_arn"
    debug_log "Selected single MFA device: $mfa_arn"
else
    echo "Select an MFA device:"

    for i in "${!mfa_device_array[@]}"; do
        echo "$((i+1))) ${mfa_device_array[$i]}"
    done

    device_number=$(prompt_input "Enter the number of your MFA device" "1")
    mfa_arn="${mfa_device_array[$((device_number-1))]}"
    echo "Using MFA device: $mfa_arn"
    debug_log "Selected MFA device #$device_number: $mfa_arn"
fi

# Input MFA code (required)
token_code=$(prompt_required "Enter your MFA code")
debug_log "MFA code entered (length: ${#token_code})"

# Validate MFA code format (should be 6 digits)
if ! [[ $token_code =~ ^[0-9]{6}$ ]]; then
    echo "Error: MFA code must be 6 digits. Aborting."
    exit 1
fi

# Get temporary credentials
echo "Fetching temporary credentials..."

max_duration_seconds=129600  # 36 hours
debug_log "Using max duration: $max_duration_seconds seconds"

# Get credentials
debug_log "Executing STS get-session-token with MFA ARN: $mfa_arn"

# Capture both output and exit status
set +e
creds_json=$(aws sts get-session-token \
    --serial-number "$mfa_arn" \
    --token-code "$token_code" \
    --duration-seconds $max_duration_seconds \
    --output json 2>&1)
sts_exit_code=$?
set -e

debug_log "STS command exit code: $sts_exit_code"
debug_log "Credentials JSON received (length: ${#creds_json})"

# Check if the STS command succeeded
if [ $sts_exit_code -ne 0 ]; then
    echo "Error: MFA validation failed"
    echo "Details: $creds_json"
    echo "Aborting."
    exit 1
fi

debug_log "Credentials JSON received (length: ${#creds_json})"

# Parse JSON output
# Parse using grep and sed
debug_log "Parsing credentials with grep/sed"
access_key=$(echo "$creds_json" | grep -o '"AccessKeyId": "[^"]*' | sed 's/"AccessKeyId": "//')
secret_key=$(echo "$creds_json" | grep -o '"SecretAccessKey": "[^"]*' | sed 's/"SecretAccessKey": "//')
session_token=$(echo "$creds_json" | grep -o '"SessionToken": "[^"]*' | sed 's/"SessionToken": "//')
expiration=$(echo "$creds_json" | grep -o '"Expiration": "[^"]*' | sed 's/"Expiration": "//')

debug_log "AccessKeyId (first 5 chars): ${access_key:0:5}..."
debug_log "SecretAccessKey (length): ${#secret_key}"
debug_log "SessionToken (length): ${#session_token}"
debug_log "Expiration: $expiration"

# Prompt for a new profile name
default_mfa_profile="${aws_profile}-mfa"
mfa_profile=$(prompt_input "Enter a name for the new profile" "$default_mfa_profile")
debug_log "Using profile name: $mfa_profile"

# Update the AWS credentials file
debug_log "Updating AWS credentials file"
aws configure set aws_access_key_id "$access_key" --profile "$mfa_profile"
aws configure set aws_secret_access_key "$secret_key" --profile "$mfa_profile"
aws configure set aws_session_token "$session_token" --profile "$mfa_profile"
aws configure set region "$AWS_REGION" --profile "$mfa_profile"

# Format expiration time for display
expiration_local=$(date -d "$expiration" '+%Y-%m-%d %H:%M:%S %Z' 2>/dev/null || echo "$expiration")
debug_log "Formatted expiration: $expiration_local"

# Final message
echo -e "\nSuccess! Temporary credentials have been set up."
echo "---------------------------------------------"
echo "Profile name: $mfa_profile"
echo "Expiration  : $expiration_local"
echo -e "\nTo use these credentials:"
echo "1. For specific commands: aws s3 ls --profile $mfa_profile"
echo "2. For this session: export AWS_PROFILE=$mfa_profile"
echo -e "\nRemember to renew your credentials before they expire."
