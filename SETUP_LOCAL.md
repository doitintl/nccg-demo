# Local Setup Guide for Menu Maestro

This guide provides detailed instructions for setting up and running Menu Maestro locally.

## Prerequisites

- Python 3.9 or higher
- AWS account with access to Amazon Bedrock
- AWS CLI installed and configured

## Step 1: Clone the Repository

```bash
git clone <repository-url>
cd menu-maestro
```

## Step 2: Set Up Environment Variables

1. Create a `.env` file from the example:
   ```bash
   cp .env.example .env
   ```

2. Edit the `.env` file with your AWS credentials and settings:
   ```
   # Environment
   ENVIRONMENT=local

   # AWS Configuration
   AWS_REGION=us-east-1
   AWS_ACCESS_KEY_ID=your_access_key_id
   AWS_SECRET_ACCESS_KEY=your_secret_access_key

   # Bedrock Configuration
   BEDROCK_MODEL_ID=us.amazon.nova-pro-v1:0

   # Storage Configuration
   USE_S3=false
   S3_BUCKET=menu-maestro-images
   ```

## Step 3: Set Up Python Environment

### Option 1: Using the Script

1. Make the run script executable:
   ```bash
   chmod +x scripts/run_local.sh
   ```

2. Run the script (it will create a virtual environment and install dependencies):
   ```bash
   ./scripts/run_local.sh
   ```

### Option 2: Manual Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

2. Activate the virtual environment:
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r app/requirements.txt
   ```

4. Run the application:
   ```bash
   cd app
   streamlit run app.py
   ```

## Step 4: Access the Application

Open your browser and navigate to:
```
http://localhost:8501
```

## Step 5: Using the Application

1. **Enter a dish description**:
   - Type a brief description of your dish (e.g., "Grilled Salmon with Asparagus")

2. **Upload an image**:
   - Click "Browse files" to upload an image of your dish
   - Supported formats: JPG, JPEG, PNG

3. **Select spice level**:
   - Use the slider to select the spice level of your dish

4. **Generate description**:
   - Click "Generate Menu Description"
   - Wait for the AI agents to analyze your image and generate content

5. **Review results**:
   - View the refined dish name
   - Read the generated description
   - Check the validation status
   - Review dietary information and allergens
   - Explore the detailed analysis (if expanded)

6. **Provide feedback**:
   - Enter feedback in the text area
   - Click "Submit Feedback & Regenerate" to get an improved description

## Troubleshooting

### Common Issues

1. **AWS Credentials Not Found**:
   - Ensure your AWS credentials are properly configured in `~/.aws/credentials` or in the `.env` file
   - Run `aws sts get-caller-identity` to verify your credentials are working

2. **Bedrock Access Issues**:
   - Verify your AWS account has access to Amazon Bedrock
   - Check that you've enabled the Nova Pro model in your AWS account
   - Ensure your IAM user has the necessary permissions to invoke Bedrock models

3. **Image Processing Issues**:
   - Ensure images are in JPG, JPEG, or PNG format
   - Check that images are not too large (keep under 5MB)
   - Verify that the image contains food items that can be recognized

4. **Python Environment Issues**:
   - Ensure you're using Python 3.9 or higher
   - Check that all dependencies are installed correctly
   - Try recreating the virtual environment if you encounter issues

### Checking Logs

If you encounter issues, check the Streamlit logs in the terminal where you ran the application. These logs often contain helpful error messages and stack traces.