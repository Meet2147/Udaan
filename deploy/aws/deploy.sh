#!/bin/bash
set -euo pipefail
export AWS_PAGER=""

REGION="ap-south-1"
PROJECT="udaan"
KEY_NAME="udaan-key"

VPC_ID=$(aws ec2 describe-vpcs --region "$REGION" --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text)
SUBNET_ID=$(aws ec2 describe-subnets --region "$REGION" --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[0].SubnetId" --output text)

if ! aws ec2 describe-key-pairs --region "$REGION" --key-names "$KEY_NAME" >/dev/null 2>&1; then
  aws ec2 create-key-pair --region "$REGION" --key-name "$KEY_NAME" --query "KeyMaterial" --output text > deploy/aws/$KEY_NAME.pem
  chmod 400 deploy/aws/$KEY_NAME.pem
fi

SG_ID=$(aws ec2 create-security-group --region "$REGION" --group-name "${PROJECT}-sg" --description "Udaan SG" --vpc-id "$VPC_ID" --query "GroupId" --output text 2>/dev/null || true)
if [ -z "$SG_ID" ] || [ "$SG_ID" = "None" ]; then
  SG_ID=$(aws ec2 describe-security-groups --region "$REGION" --filters "Name=group-name,Values=${PROJECT}-sg" "Name=vpc-id,Values=$VPC_ID" --query "SecurityGroups[0].GroupId" --output text)
fi

aws ec2 authorize-security-group-ingress --no-cli-pager --region "$REGION" --group-id "$SG_ID" --protocol tcp --port 22 --cidr 0.0.0.0/0 >/dev/null 2>&1 || true
aws ec2 authorize-security-group-ingress --no-cli-pager --region "$REGION" --group-id "$SG_ID" --protocol tcp --port 80 --cidr 0.0.0.0/0 >/dev/null 2>&1 || true
aws ec2 authorize-security-group-ingress --no-cli-pager --region "$REGION" --group-id "$SG_ID" --protocol tcp --port 443 --cidr 0.0.0.0/0 >/dev/null 2>&1 || true
aws ec2 authorize-security-group-ingress --no-cli-pager --region "$REGION" --group-id "$SG_ID" --protocol tcp --port 3000 --cidr 0.0.0.0/0 >/dev/null 2>&1 || true
aws ec2 authorize-security-group-ingress --no-cli-pager --region "$REGION" --group-id "$SG_ID" --protocol tcp --port 8000 --cidr 0.0.0.0/0 >/dev/null 2>&1 || true

AMI_ID=$(aws ssm get-parameter --region "$REGION" --name "/aws/service/canonical/ubuntu/server/22.04/stable/current/amd64/hvm/ebs-gp3/ami-id" --query "Parameter.Value" --output text 2>/dev/null || true)
if [ -z "$AMI_ID" ] || [ "$AMI_ID" = "None" ]; then
  AMI_ID=$(aws ssm get-parameter --region "$REGION" --name "/aws/service/canonical/ubuntu/server/22.04/stable/current/arm64/hvm/ebs-gp3/ami-id" --query "Parameter.Value" --output text 2>/dev/null || true)
fi
if [ -z "$AMI_ID" ] || [ "$AMI_ID" = "None" ]; then
  AMI_ID=$(aws ssm get-parameter --region "$REGION" --name "/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-6.1-x86_64" --query "Parameter.Value" --output text 2>/dev/null || true)
fi
if [ -z "$AMI_ID" ] || [ "$AMI_ID" = "None" ]; then
  echo "AMI lookup failed. Check SSM permissions or region."
  exit 1
fi

INSTANCE_ID=$(aws ec2 run-instances \
  --region "$REGION" \
  --image-id "$AMI_ID" \
  --instance-type "t3a.small" \
  --key-name "$KEY_NAME" \
  --security-group-ids "$SG_ID" \
  --subnet-id "$SUBNET_ID" \
  --user-data "file://deploy/aws/user-data.sh" \
  --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${PROJECT}-server}]" \
  --query "Instances[0].InstanceId" \
  --output text)

aws ec2 wait instance-running --region "$REGION" --instance-ids "$INSTANCE_ID"

ALLOC_ID=$(aws ec2 allocate-address --region "$REGION" --domain vpc --query "AllocationId" --output text)
aws ec2 associate-address --region "$REGION" --instance-id "$INSTANCE_ID" --allocation-id "$ALLOC_ID"

PUBLIC_IP=$(aws ec2 describe-addresses --region "$REGION" --allocation-ids "$ALLOC_ID" --query "Addresses[0].PublicIp" --output text)

echo "Instance ID: $INSTANCE_ID"
echo "Public IP: $PUBLIC_IP"
echo "SSH: ssh -i deploy/aws/$KEY_NAME.pem ubuntu@$PUBLIC_IP"
