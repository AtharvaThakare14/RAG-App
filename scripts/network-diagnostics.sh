#!/bin/bash
# Simple Network Connectivity Check for RDS
# Usage: ./network-diagnostics.sh <environment> [aws-region] <project_name>

set -e

# Default values
AWS_REGION=${2}
PROJECT_NAME=${3}
ENV=$1

# Check if environment was provided
if [ -z "$ENV" ]; then
  echo "Error: Environment not specified"
  echo "Usage: $0 <environment> [aws-region]"
  echo "Example: $0 dev us-east-1"
  exit 1
fi

echo "Running network diagnostics for $PROJECT_NAME-$ENV in $AWS_REGION"

# Get RDS endpoint
echo "Getting RDS endpoint..."
DB_ENDPOINT=$(aws rds describe-db-instances \
  --db-instance-identifier "$PROJECT_NAME-$ENV-postgres" \
  --region "$AWS_REGION" \
  --query "DBInstances[0].Endpoint.Address" \
  --output text 2>/dev/null || echo "not-found")

if [ "$DB_ENDPOINT" == "not-found" ] || [ -z "$DB_ENDPOINT" ]; then
  echo "Error: RDS instance not found!"
  exit 1
fi

echo "RDS Endpoint: $DB_ENDPOINT"

# Get VPC ID
echo "Getting VPC ID..."
VPC_ID=$(aws ec2 describe-vpcs \
  --filters "Name=tag:Name,Values=$PROJECT_NAME-$ENV-vpc" \
  --region "$AWS_REGION" \
  --query "Vpcs[0].VpcId" \
  --output text)

if [ -z "$VPC_ID" ]; then
  echo "Error: VPC not found!"
  exit 1
fi

echo "VPC ID: $VPC_ID"

# Get Lambda SG
echo "Getting Lambda Security Group ID..."
LAMBDA_SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=tag:Name,Values=$PROJECT_NAME-$ENV-lambda-sg" \
  --region "$AWS_REGION" \
  --query "SecurityGroups[0].GroupId" \
  --output text)

echo "Lambda Security Group ID: $LAMBDA_SG_ID"

# Get DB SG
echo "Getting DB Security Group ID..."
DB_SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=tag:Name,Values=$PROJECT_NAME-$ENV-db-sg" \
  --region "$AWS_REGION" \
  --query "SecurityGroups[0].GroupId" \
  --output text)

echo "DB Security Group ID: $DB_SG_ID"

# Check DB SG inbound rules
echo -e "\nDB Security Group Inbound Rules:"
aws ec2 describe-security-group-rules \
  --filters "Name=group-id,Values=$DB_SG_ID" \
  --region "$AWS_REGION" \
  --query "SecurityGroupRules[?IsEgress==\`false\`].{Protocol:IpProtocol,FromPort:FromPort,ToPort:ToPort,Source:References[0].SecurityGroupId||CidrIpv4}" \
  --output table

# Check Lambda SG outbound rules
echo -e "\nLambda Security Group Outbound Rules:"
aws ec2 describe-security-group-rules \
  --filters "Name=group-id,Values=$LAMBDA_SG_ID" \
  --region "$AWS_REGION" \
  --query "SecurityGroupRules[?IsEgress==\`true\`].{Protocol:IpProtocol,FromPort:FromPort,ToPort:ToPort,Destination:References[0].SecurityGroupId||CidrIpv4}" \
  --output table

# Check DNS resolution from Lambda
LAMBDA_FUNCTION="${PROJECT_NAME}-${ENV}-db-init"
echo -e "\nChecking if Lambda function exists: $LAMBDA_FUNCTION"
if aws lambda get-function --function-name "$LAMBDA_FUNCTION" --region "$AWS_REGION" &> /dev/null; then
  echo "Lambda function found. Testing DNS resolution..."

  cat > dns_test.py << EOF
import json
import socket

def lambda_handler(event, context):
    try:
        hostname = "$DB_ENDPOINT"
        ip_address = socket.gethostbyname(hostname)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'hostname': hostname,
                'ip_address': ip_address,
                'result': 'success'
            })
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({
                'hostname': "$DB_ENDPOINT",
                'error': str(e),
                'result': 'failure'
            })
        }
EOF

  zip dns_test.zip dns_test.py

  echo "Updating Lambda with DNS test function..."
  aws lambda update-function-code \
    --function-name "$LAMBDA_FUNCTION" \
    --zip-file fileb://dns_test.zip \
    --region "$AWS_REGION"

  echo "Waiting for Lambda update..."
  sleep 5

  echo "Testing DNS resolution for $DB_ENDPOINT from Lambda..."
  aws lambda invoke \
    --function-name "$LAMBDA_FUNCTION" \
    --payload '{}' \
    --region "$AWS_REGION" \
    dns_result.json

  echo "DNS test result:"
  cat dns_result.json
  echo ""

  rm -f dns_test.py dns_test.zip

  echo "Restoring original Lambda function..."
  if aws s3 ls "s3://${PROJECT_NAME}-${ENV}-documents/lambda/db_init.zip" &> /dev/null; then
    aws s3 cp "s3://${PROJECT_NAME}-${ENV}-documents/lambda/db_init.zip" db_init.zip
    aws lambda update-function-code \
      --function-name "$LAMBDA_FUNCTION" \
      --zip-file fileb://db_init.zip \
      --region "$AWS_REGION"
    rm -f db_init.zip
  else
    echo "Original Lambda function code not found at s3://${PROJECT_NAME}-${ENV}-documents/lambda/db_init.zip"
    echo "You will need to manually restore the Lambda function."
  fi
else
  echo "Lambda function $LAMBDA_FUNCTION not found. Skipping DNS resolution test."
fi

# Check RDS status
echo -e "\nRDS Instance Status:"
aws rds describe-db-instances \
  --db-instance-identifier "$PROJECT_NAME-$ENV-postgres" \
  --region "$AWS_REGION" \
  --query "DBInstances[0].{Status:DBInstanceStatus,Identifier:DBInstanceIdentifier,Engine:Engine,VpcId:DBSubnetGroup.VpcId}" \
  --output table

# Summary
echo -e "\nConnectivity Check Summary:"
echo "1. RDS Endpoint: $DB_ENDPOINT"
echo "2. VPC ID: $VPC_ID"
echo "3. Lambda Security Group: $LAMBDA_SG_ID"
echo "4. DB Security Group: $DB_SG_ID"

echo -e "\nRecommendations:"
echo "1. Check the Secret Manager entry has the correct endpoint: $DB_ENDPOINT"
echo "2. Ensure DB Security Group allows inbound traffic from Lambda Security Group on port 5432"
echo "3. Ensure Lambda Security Group allows outbound traffic to DB Security Group on port 5432"
echo "4. Verify Lambda and RDS are in the same VPC ($VPC_ID)"
echo "5. Ensure the VPC has proper DNS resolution (enableDnsHostnames and enableDnsSupport)"
