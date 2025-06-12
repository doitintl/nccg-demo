# AWS Lambda Setup Guide for Menu Maestro

This guide provides detailed instructions for deploying Menu Maestro using AWS Lambda and API Gateway.

## Prerequisites

- AWS account with access to Amazon Bedrock
- AWS CLI installed and configured
- Terraform installed
- Basic knowledge of AWS services

## Step 1: Configure AWS CLI

If you haven't already configured the AWS CLI, run:

```bash
aws configure
```

Enter your AWS Access Key ID, Secret Access Key, default region, and output format.

## Step 2: Prepare for Deployment

1. Clone the repository (if you haven't already):
   ```bash
   git clone <repository-url>
   cd menu-maestro
   ```

2. Make the deployment script executable:
   ```bash
   chmod +x scripts/deploy_lambda.sh
   ```

## Step 3: (Optional) Configure Terraform Backend

For team environments or to maintain state between deployments, set up an S3 backend:

1. Create an S3 bucket for Terraform state:
   ```bash
   aws s3 mb s3://menu-maestro-terraform-state
   ```

2. Edit `infra/lambda/terraform/main.tf` to add:
   ```hcl
   terraform {
     backend "s3" {
       bucket = "menu-maestro-terraform-state"
       key    = "lambda/terraform.tfstate"
       region = "us-east-1"
     }
   }
   ```

## Step 4: Customize Deployment (Optional)

1. Edit `infra/lambda/terraform/variables.tf` to customize:
   - AWS region
   - Environment name
   - S3 bucket name

2. Create a `terraform.tfvars` file in `infra/lambda/terraform/` to override default values:
   ```
   aws_region = "us-east-1"
   environment = "dev"
   s3_bucket_name = "my-custom-menu-maestro-bucket"
   ```

## Step 5: Deploy the Infrastructure

Run the deployment script:

```bash
./scripts/deploy_lambda.sh
```

This script will:
1. Create a zip file of the app code for the Lambda layer
2. Create function zip files for each Lambda function
3. Initialize Terraform
4. Apply the Terraform configuration to create:
   - S3 bucket for image storage
   - Lambda functions
   - IAM roles and policies
   - API Gateway

## Step 6: Get the API Gateway URL

After deployment completes, get the API Gateway URL:

```bash
cd infra/lambda/terraform
terraform output api_gateway_url
```

## Step 7: Test the API

### Using curl

1. Convert an image to base64:
   ```bash
   # On Linux/macOS
   BASE64_IMAGE=$(base64 -i path/to/your/image.jpg)
   
   # On Windows (PowerShell)
   $BASE64_IMAGE = [Convert]::ToBase64String([IO.File]::ReadAllBytes("path\to\your\image.jpg"))
   ```

2. Send a request to the API:
   ```bash
   # On Linux/macOS
   curl -X POST https://<api-gateway-url>/menu-description \
     -H "Content-Type: application/json" \
     -d "{\"dish_name\": \"Grilled Salmon with Asparagus\", \"image\": \"$BASE64_IMAGE\", \"spice_level\": \"Medium\"}"
   
   # On Windows (PowerShell)
   $body = @{
     dish_name = "Grilled Salmon with Asparagus"
     image = $BASE64_IMAGE
     spice_level = "Medium"
   } | ConvertTo-Json
   
   Invoke-RestMethod -Uri "https://<api-gateway-url>/menu-description" -Method Post -Body $body -ContentType "application/json"
   ```

### Using Postman

1. Open Postman
2. Create a new POST request to `https://<api-gateway-url>/menu-description`
3. Set the Content-Type header to `application/json`
4. In the Body tab, select "raw" and "JSON"
5. Enter the request body:
   ```json
   {
     "dish_name": "Grilled Salmon with Asparagus",
     "image": "<base64-encoded-image>",
     "spice_level": "Medium"
   }
   ```
6. Send the request

## Step 8: Create a Simple Web Frontend (Optional)

For a simple web frontend to interact with your API:

1. Create an HTML file named `index.html`:
   ```html
   <!DOCTYPE html>
   <html>
   <head>
     <title>Menu Maestro</title>
     <style>
       body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
       .container { display: flex; gap: 20px; }
       .input-section, .output-section { flex: 1; }
       textarea { width: 100%; height: 100px; }
       img { max-width: 100%; }
       .tag { background-color: #e6f3e6; color: #2e7d32; padding: 3px 8px; border-radius: 12px; margin-right: 6px; }
     </style>
   </head>
   <body>
     <h1>Menu Maestro</h1>
     
     <div class="container">
       <div class="input-section">
         <h2>Input</h2>
         <div>
           <label for="dish-name">Dish Description:</label>
           <input type="text" id="dish-name" placeholder="Enter dish description">
         </div>
         <div>
           <label for="spice-level">Spice Level:</label>
           <select id="spice-level">
             <option value="No Spice">No Spice</option>
             <option value="Mild">Mild</option>
             <option value="Medium" selected>Medium</option>
             <option value="Spicy">Spicy</option>
             <option value="Very Spicy">Very Spicy</option>
             <option value="Extremely Hot">Extremely Hot</option>
           </select>
         </div>
         <div>
           <label for="image-upload">Dish Image:</label>
           <input type="file" id="image-upload" accept="image/jpeg,image/png">
         </div>
         <div id="image-preview"></div>
         <button id="generate-btn">Generate Description</button>
       </div>
       
       <div class="output-section">
         <h2>Output</h2>
         <div id="loading" style="display: none;">Processing...</div>
         <div id="result" style="display: none;">
           <h3 id="refined-name"></h3>
           <p id="description"></p>
           
           <h4>Dietary Information</h4>
           <div id="allergens"></div>
           <div id="dietary-tags"></div>
           
           <h4>Feedback</h4>
           <textarea id="feedback" placeholder="Provide feedback to improve the description"></textarea>
           <button id="feedback-btn">Submit Feedback</button>
         </div>
       </div>
     </div>
     
     <script>
       const apiUrl = 'https://<api-gateway-url>/menu-description';
       
       document.getElementById('image-upload').addEventListener('change', function(event) {
         const file = event.target.files[0];
         if (file) {
           const reader = new FileReader();
           reader.onload = function(e) {
             const img = document.createElement('img');
             img.src = e.target.result;
             document.getElementById('image-preview').innerHTML = '';
             document.getElementById('image-preview').appendChild(img);
           };
           reader.readAsDataURL(file);
         }
       });
       
       document.getElementById('generate-btn').addEventListener('click', async function() {
         const dishName = document.getElementById('dish-name').value;
         const spiceLevel = document.getElementById('spice-level').value;
         const fileInput = document.getElementById('image-upload');
         
         if (!dishName || !fileInput.files[0]) {
           alert('Please enter a dish description and upload an image');
           return;
         }
         
         document.getElementById('loading').style.display = 'block';
         document.getElementById('result').style.display = 'none';
         
         try {
           const file = fileInput.files[0];
           const base64Image = await fileToBase64(file);
           const imageData = base64Image.split(',')[1]; // Remove data URL prefix
           
           const response = await fetch(apiUrl, {
             method: 'POST',
             headers: {
               'Content-Type': 'application/json'
             },
             body: JSON.stringify({
               dish_name: dishName,
               image: imageData,
               spice_level: spiceLevel
             })
           });
           
           const result = await response.json();
           
           // Display results
           document.getElementById('refined-name').textContent = result.refined_name;
           document.getElementById('description').textContent = result.generated_description;
           
           // Display allergens
           const allergensDiv = document.getElementById('allergens');
           if (result.dietary_analysis.allergens && result.dietary_analysis.allergens.length > 0) {
             allergensDiv.innerHTML = '<p><strong>Allergens:</strong> ' + result.dietary_analysis.allergens.join(', ') + '</p>';
           } else {
             allergensDiv.innerHTML = '<p><strong>Allergens:</strong> None detected</p>';
           }
           
           // Display dietary tags
           const tagsDiv = document.getElementById('dietary-tags');
           if (result.dietary_analysis.tags && result.dietary_analysis.tags.length > 0) {
             tagsDiv.innerHTML = '<p><strong>Dietary Tags:</strong> ' + 
               result.dietary_analysis.tags.map(tag => `<span class="tag">${tag}</span>`).join(' ') + '</p>';
           } else {
             tagsDiv.innerHTML = '<p><strong>Dietary Tags:</strong> None</p>';
           }
           
           document.getElementById('loading').style.display = 'none';
           document.getElementById('result').style.display = 'block';
         } catch (error) {
           console.error('Error:', error);
           alert('An error occurred. Please try again.');
           document.getElementById('loading').style.display = 'none';
         }
       });
       
       function fileToBase64(file) {
         return new Promise((resolve, reject) => {
           const reader = new FileReader();
           reader.readAsDataURL(file);
           reader.onload = () => resolve(reader.result);
           reader.onerror = error => reject(error);
         });
       }
     </script>
   </body>
   </html>
   ```

2. Replace `<api-gateway-url>` with your actual API Gateway URL

3. Open the HTML file in a web browser to use the interface

## Step 9: Clean Up Resources (When No Longer Needed)

To avoid incurring charges, clean up resources when you're done:

```bash
cd infra/lambda/terraform
terraform destroy
```

## Troubleshooting

### Common Issues

1. **Terraform Errors**:
   - Check that you have the correct AWS credentials configured
   - Ensure you have sufficient permissions to create resources
   - Look for error messages in the Terraform output

2. **Lambda Deployment Failures**:
   - Check CloudWatch Logs for detailed error messages
   - Verify that your Lambda function has the correct permissions
   - Ensure your Lambda function timeout is sufficient (30 seconds or more)

3. **API Gateway Issues**:
   - Check that the API Gateway is properly configured
   - Verify that the Lambda integration is set up correctly
   - Check that CORS is configured if you're calling from a web browser

4. **Bedrock Access Issues**:
   - Verify your AWS account has access to Amazon Bedrock
   - Check that you've enabled the Nova Pro model in your AWS account
   - Ensure your IAM role has the necessary permissions

### Checking Logs

To view Lambda function logs:

1. Go to the AWS Console > CloudWatch > Log Groups
2. Find the log group for your Lambda function (e.g., `/aws/lambda/menu-maestro-orchestrator`)
3. Click on the log group to view log streams
4. Click on a log stream to view detailed logs