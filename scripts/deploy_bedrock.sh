#!/bin/bash

# Change to the project root directory
cd "$(dirname "$0")/.."

# Create a zip file of the app code for the Lambda layer
echo "Creating app code zip for Lambda layer..."
zip -r app.zip app -x "app/__pycache__/*" "app/*/__pycache__/*"

# Create function zip file for the action group handler
echo "Creating action group handler zip file..."
mkdir -p infra/bedrock/action_groups/package
cp infra/bedrock/action_groups/handler.py infra/bedrock/action_groups/package/
cd infra/bedrock/action_groups/package
zip -r ../function.zip .
cd ../../../../..

# Apply Terraform configuration
echo "Applying Terraform configuration..."
cd infra/bedrock/terraform
terraform init
terraform apply -auto-approve

# Note: Since Terraform doesn't support Bedrock Agents directly,
# you'll need to create the agent and action groups manually using the AWS CLI
echo "Terraform deployment complete!"
echo "Now you need to create the Bedrock Agent and action groups manually using the AWS CLI or console."
echo "See the README.md for instructions."