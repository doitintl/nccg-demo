#!/bin/bash

# Change to the project root directory
cd "$(dirname "$0")/.."

# Create a zip file of the app code for the Lambda layer
echo "Creating app code zip for Lambda layer..."
# First, clean up any existing zip
rm -f app.zip

# Create a temporary directory for the Lambda layer
mkdir -p lambda_layer_temp/python
echo "Copying only necessary files..."

# Copy only the essential Python files needed for the Lambda function
mkdir -p lambda_layer_temp/python/app
cp app/authenticator.py app/bedrock_utils.py app/config.py app/culinary_wordsmith.py app/dietary_detective.py app/side_item_analyzer.py app/storage.py app/visionary_chef.py lambda_layer_temp/python/app/
touch lambda_layer_temp/python/app/__init__.py

# Create a minimal requirements.txt for Lambda
cat > lambda_layer_temp/requirements.txt << EOL
boto3>=1.28.0
Pillow>=9.5.0
EOL

# Zip the Lambda layer with only the necessary files
cd lambda_layer_temp
zip -r ../app.zip python requirements.txt
cd ..

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

# Clean up temporary directory
echo "Cleaning up..."
cd ../../..
rm -rf lambda_layer_temp

echo "Deployment complete!"