# AWS Bedrock Agents Setup Guide for Menu Maestro

This guide provides detailed instructions for deploying Menu Maestro using AWS Bedrock Agents.

## Prerequisites

- AWS account with access to Amazon Bedrock and Bedrock Agents
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
   chmod +x scripts/deploy_bedrock.sh
   ```

## Step 3: Deploy the Infrastructure

Run the deployment script:

```bash
./scripts/deploy_bedrock.sh
```

This script will:
1. Create a zip file of the app code for the Lambda layer
2. Create a function zip file for the action group handler
3. Initialize Terraform
4. Apply the Terraform configuration to create:
   - S3 bucket for image storage
   - Lambda function for action groups
   - IAM roles and policies

## Step 4: Create the Bedrock Agent

Since Terraform doesn't directly support Bedrock Agents yet, you'll need to create the agent manually in the AWS Console:

1. **Go to the AWS Console**:
   - Navigate to Amazon Bedrock
   - Click on "Agents" in the left sidebar

2. **Create a new agent**:
   - Click "Create agent"
   - Enter basic details:
     - Name: MenuMaestro
     - Description: AI-powered menu description generator
     - IAM role: Create a new service role or use an existing role with Bedrock permissions
   - Click "Next"

3. **Select a foundation model**:
   - Choose "Amazon Nova Pro" from the dropdown
   - Click "Next"

4. **Configure agent instructions**:
   - Enter the following instructions:
     ```
     You are Menu Maestro, an AI system that generates comprehensive menu descriptions from food images. 
     
     Your workflow:
     1. Analyze the uploaded food image to identify ingredients, cooking methods, and presentation style
     2. Validate that the dish description matches what's visible in the image
     3. Identify potential allergens and dietary classifications
     4. Distinguish between main dish components and side items
     5. Generate an engaging menu description
     
     Always be helpful, accurate, and focused on creating appealing food descriptions.
     ```
   - Click "Next"

5. **Skip knowledge bases** (unless you want to add one)
   - Click "Next"

6. **Review and create**:
   - Review your agent configuration
   - Click "Create agent"

## Step 5: Add Action Groups to the Agent

After the agent is created, you need to add action groups:

### Action Group 1: Image Analysis

1. Click on your agent, then click "Add" in the Action groups section
2. Enter basic details:
   - Name: ImageAnalysis
   - Description: Analyzes food images to identify ingredients and cooking methods
   - Select "Create from scratch"
   - Click "Next"

3. Define the API schema:
   ```json
   {
     "openapi": "3.0.0",
     "info": {
       "title": "Image Analysis API",
       "version": "1.0.0"
     },
     "paths": {
       "/analyze-image": {
         "post": {
           "summary": "Analyze a food image",
           "operationId": "analyzeImage",
           "parameters": [
             {
               "name": "imageKey",
               "in": "query",
               "required": true,
               "schema": {
                 "type": "string"
               },
               "description": "S3 key of the uploaded image"
             },
             {
               "name": "dishName",
               "in": "query",
               "required": true,
               "schema": {
                 "type": "string"
               },
               "description": "Name or description of the dish"
             }
           ],
           "responses": {
             "200": {
               "description": "Successful analysis",
               "content": {
                 "application/json": {
                   "schema": {
                     "type": "object",
                     "properties": {
                       "items": {
                         "type": "array",
                         "items": {
                           "type": "object",
                           "properties": {
                             "item": {
                               "type": "string"
                             },
                             "confidence": {
                               "type": "number"
                             }
                           }
                         }
                       },
                       "cooking_style": {
                         "type": "string"
                       },
                       "presentation": {
                         "type": "string"
                       }
                     }
                   }
                 }
               }
             }
           }
         }
       }
     }
   }
   ```

4. Configure the Lambda function:
   - Select "AWS Lambda function"
   - Choose the region where you deployed your resources
   - Select the "menu-maestro-action-group-handler" function
   - Click "Next"

5. Review and create:
   - Review your action group configuration
   - Click "Create action group"

### Action Group 2: Dish Validation

Follow the same steps as above, but with these differences:

- Name: DishValidation
- Description: Validates that dish descriptions match visual evidence
- API Schema: (similar to above, with appropriate parameters and response schema)

### Action Group 3: Dietary Analysis

Follow the same steps as above, but with these differences:

- Name: DietaryAnalysis
- Description: Identifies allergens and dietary classifications
- API Schema: (similar to above, with appropriate parameters and response schema)

### Action Group 4: Side Item Analysis

Follow the same steps as above, but with these differences:

- Name: SideItemAnalysis
- Description: Distinguishes between main dish components and sides
- API Schema: (similar to above, with appropriate parameters and response schema)

### Action Group 5: Description Generation

Follow the same steps as above, but with these differences:

- Name: DescriptionGeneration
- Description: Generates engaging menu descriptions
- API Schema: (similar to above, with appropriate parameters and response schema)

## Step 6: Prepare the Agent

1. Click on your agent
2. Click "Prepare" in the top right
3. Wait for the preparation to complete (this may take a few minutes)

## Step 7: Create an Agent Alias

1. Click on your agent
2. Go to the "Aliases" tab
3. Click "Create alias"
4. Enter details:
   - Alias name: production
   - Description: Production version of Menu Maestro
   - Click "Create alias"

## Step 8: Test the Agent

### Using the AWS Console

1. Click on your agent
2. Go to the "Test" tab
3. Select your alias from the dropdown
4. Start a conversation with the agent:
   ```
   I have an image of a burger. Can you help me generate a menu description for it?
   ```
5. Follow the agent's instructions to upload an image and provide details

### Using the AWS SDK

```python
import boto3
import base64
import json

# Initialize the Bedrock Agent Runtime client
bedrock_agent_runtime = boto3.client('bedrock-agent-runtime')

# Read the image file
with open('path/to/your/image.jpg', 'rb') as image_file:
    image_bytes = image_file.read()
    base64_image = base64.b64encode(image_bytes).decode('utf-8')

# Start a conversation with the agent
response = bedrock_agent_runtime.invoke_agent(
    agentId='your-agent-id',
    agentAliasId='your-agent-alias-id',
    sessionId='unique-session-id',
    inputText='I have an image of a burger and want to generate a menu description for it.'
)

# Process the response
for event in response['completion']:
    if 'chunk' in event:
        print(event['chunk']['bytes'].decode('utf-8'), end='')

# Upload the image when prompted
response = bedrock_agent_runtime.invoke_agent(
    agentId='your-agent-id',
    agentAliasId='your-agent-alias-id',
    sessionId='unique-session-id',
    inputText=f'Here is the image: data:image/jpeg;base64,{base64_image}'
)

# Process the response
for event in response['completion']:
    if 'chunk' in event:
        print(event['chunk']['bytes'].decode('utf-8'), end='')
```

## Step 9: Create a Web Interface (Optional)

For a simple web interface to interact with your Bedrock Agent:

1. Create an HTML file named `index.html`:
   ```html
   <!DOCTYPE html>
   <html>
   <head>
     <title>Menu Maestro - Bedrock Agent</title>
     <style>
       body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
       .chat-container { border: 1px solid #ccc; border-radius: 5px; padding: 10px; height: 400px; overflow-y: auto; }
       .message { margin-bottom: 10px; padding: 8px; border-radius: 5px; }
       .user { background-color: #e3f2fd; text-align: right; }
       .agent { background-color: #f1f8e9; }
       .input-container { display: flex; margin-top: 10px; }
       #user-input { flex-grow: 1; padding: 8px; }
       button { padding: 8px 16px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer; }
       #file-upload { display: none; }
       .upload-btn { padding: 8px 16px; background-color: #2196F3; color: white; border: none; border-radius: 4px; cursor: pointer; margin-right: 10px; }
     </style>
   </head>
   <body>
     <h1>Menu Maestro - Bedrock Agent</h1>
     
     <div class="chat-container" id="chat-container"></div>
     
     <div class="input-container">
       <label class="upload-btn" for="file-upload">Upload Image</label>
       <input type="file" id="file-upload" accept="image/*">
       <input type="text" id="user-input" placeholder="Type your message...">
       <button id="send-btn">Send</button>
     </div>
     
     <script>
       // Replace with your API Gateway endpoint that proxies to the Bedrock Agent
       const API_ENDPOINT = 'https://your-api-gateway-url/agent';
       let sessionId = generateSessionId();
       
       document.getElementById('send-btn').addEventListener('click', sendMessage);
       document.getElementById('user-input').addEventListener('keypress', function(e) {
         if (e.key === 'Enter') sendMessage();
       });
       
       document.getElementById('file-upload').addEventListener('change', function(e) {
         if (e.target.files.length > 0) {
           const file = e.target.files[0];
           const reader = new FileReader();
           reader.onload = function() {
             const base64Image = reader.result.split(',')[1];
             document.getElementById('user-input').value = `Here's an image of my dish`;
             sendMessage(base64Image);
           };
           reader.readAsDataURL(file);
         }
       });
       
       function sendMessage(base64Image = null) {
         const userInput = document.getElementById('user-input').value.trim();
         if (!userInput && !base64Image) return;
         
         // Add user message to chat
         addMessageToChat(userInput, 'user');
         document.getElementById('user-input').value = '';
         
         // Prepare request body
         const requestBody = {
           agentId: 'your-agent-id',
           agentAliasId: 'your-agent-alias-id',
           sessionId: sessionId,
           inputText: userInput
         };
         
         if (base64Image) {
           requestBody.inputImage = base64Image;
         }
         
         // Send request to API
         fetch(API_ENDPOINT, {
           method: 'POST',
           headers: {
             'Content-Type': 'application/json'
           },
           body: JSON.stringify(requestBody)
         })
         .then(response => response.json())
         .then(data => {
           // Add agent response to chat
           addMessageToChat(data.response, 'agent');
         })
         .catch(error => {
           console.error('Error:', error);
           addMessageToChat('Sorry, an error occurred. Please try again.', 'agent');
         });
       }
       
       function addMessageToChat(message, sender) {
         const chatContainer = document.getElementById('chat-container');
         const messageElement = document.createElement('div');
         messageElement.classList.add('message', sender);
         messageElement.textContent = message;
         chatContainer.appendChild(messageElement);
         chatContainer.scrollTop = chatContainer.scrollHeight;
       }
       
       function generateSessionId() {
         return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
           const r = Math.random() * 16 | 0;
           const v = c === 'x' ? r : (r & 0x3 | 0x8);
           return v.toString(16);
         });
       }
       
       // Add welcome message
       addMessageToChat('Welcome to Menu Maestro! Upload an image of your dish or describe it to get started.', 'agent');
     </script>
   </body>
   </html>
   ```

2. You'll need to create an API Gateway endpoint that proxies requests to the Bedrock Agent Runtime API

## Step 10: Clean Up Resources (When No Longer Needed)

To avoid incurring charges, clean up resources when you're done:

1. Delete the Bedrock Agent:
   - Go to the AWS Console > Amazon Bedrock > Agents
   - Select your agent
   - Click "Delete"

2. Delete the infrastructure:
   ```bash
   cd infra/bedrock/terraform
   terraform destroy
   ```

## Troubleshooting

### Common Issues

1. **Agent Preparation Failures**:
   - Check that your action group API schemas are valid
   - Ensure your Lambda function has the correct permissions
   - Verify that the Lambda function is in the same region as your agent

2. **Lambda Function Issues**:
   - Check CloudWatch Logs for detailed error messages
   - Verify that your Lambda function has the correct permissions
   - Ensure your Lambda function timeout is sufficient (30 seconds or more)

3. **Bedrock Access Issues**:
   - Verify your AWS account has access to Amazon Bedrock and Bedrock Agents
   - Check that you've enabled the Nova Pro model in your AWS account
   - Ensure your IAM roles have the necessary permissions

4. **Image Processing Issues**:
   - Ensure images are in a supported format
   - Check that images are not too large
   - Verify that the image contains food items that can be recognized

### Checking Logs

To view Lambda function logs:

1. Go to the AWS Console > CloudWatch > Log Groups
2. Find the log group for your Lambda function (e.g., `/aws/lambda/menu-maestro-action-group-handler`)
3. Click on the log group to view log streams
4. Click on a log stream to view detailed logs

To view Bedrock Agent logs:

1. Go to the AWS Console > Amazon Bedrock > Agents
2. Click on your agent
3. Go to the "Monitoring" tab
4. View the metrics and logs for your agent