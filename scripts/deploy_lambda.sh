#!/bin/bash

# Change to the project root directory
cd "$(dirname "$0")/.."

# Create a zip file of the app code for the Lambda layer
echo "Creating app code zip for Lambda layer..."
zip -r app.zip app -x "app/__pycache__/*" "app/*/__pycache__/*"

# Create function zip files for each Lambda function
echo "Creating function zip files..."

# Orchestrator function
mkdir -p infra/lambda/functions/orchestrator/package
cp infra/lambda/functions/orchestrator/lambda_function.py infra/lambda/functions/orchestrator/package/
cd infra/lambda/functions/orchestrator/package
zip -r ../function.zip .
cd ../../../../..

# Apply Terraform configuration
echo "Applying Terraform configuration..."
cd infra/lambda/terraform
terraform init
terraform apply -auto-approve

echo "Deployment complete!"