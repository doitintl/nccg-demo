# Troubleshooting Guide for Menu Maestro

## Common Issues and Solutions

### Import Errors

#### Error: "ImportError: attempted relative import beyond top-level package"

**Problem:**
```
ImportError: attempted relative import beyond top-level package
```

**Solution:**
This error occurs when you try to use relative imports (e.g., `from ..utils.bedrock import get_bedrock_client`) in a script that's not part of a proper Python package structure.

1. **Use the run.py entry point**:
   ```bash
   python run.py
   ```
   
   This script sets up the Python path correctly to allow absolute imports.

2. **Use absolute imports**:
   If you're modifying the code, use absolute imports:
   ```python
   # Instead of this:
   from ..utils.bedrock import get_bedrock_client
   
   # Use this:
   from app.utils.bedrock import get_bedrock_client
   ```

3. **Set PYTHONPATH environment variable**:
   ```bash
   export PYTHONPATH=$PYTHONPATH:/path/to/menu-maestro
   ```

### AWS Credentials Issues

#### Error: "botocore.exceptions.NoCredentialsError: Unable to locate credentials"

**Problem:**
```
botocore.exceptions.NoCredentialsError: Unable to locate credentials
```

**Solution:**
1. Make sure you have AWS credentials configured:
   ```bash
   aws configure
   ```

2. Check that your `.env` file contains valid credentials:
   ```
   AWS_ACCESS_KEY_ID=your_access_key_id
   AWS_SECRET_ACCESS_KEY=your_secret_access_key
   ```

3. Verify your credentials are working:
   ```bash
   aws sts get-caller-identity
   ```

### Bedrock Model Access Issues

#### Error: "An error occurred (AccessDeniedException) when calling the InvokeModel operation"

**Problem:**
```
An error occurred (AccessDeniedException) when calling the InvokeModel operation: You don't have access to the model
```

**Solution:**
1. Verify your AWS account has access to Amazon Bedrock
2. Check that you've enabled the Nova Pro model in your AWS account:
   - Go to AWS Console > Amazon Bedrock > Model access
   - Request access to the models you need
3. Ensure your IAM user/role has the necessary permissions:
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "bedrock:InvokeModel"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

### Streamlit Issues

#### Error: "ModuleNotFoundError: No module named 'streamlit'"

**Problem:**
```
ModuleNotFoundError: No module named 'streamlit'
```

**Solution:**
1. Make sure you've installed the requirements:
   ```bash
   pip install -r app/requirements.txt
   ```

2. Check that you're using the correct virtual environment:
   ```bash
   source venv/bin/activate
   ```

### Docker Issues

#### Error: "docker: Error response from daemon: Ports are not available"

**Problem:**
```
docker: Error response from daemon: Ports are not available: listen tcp 0.0.0.0:8501: bind: address already in use.
```

**Solution:**
1. Check if another Streamlit app is running:
   ```bash
   lsof -i :8501
   ```

2. Stop the process using the port:
   ```bash
   kill -9 <PID>
   ```

3. Use a different port in docker-compose.yml:
   ```yaml
   ports:
     - "8502:8501"
   ```

## Getting Help

If you encounter issues not covered in this guide:

1. Check the logs:
   ```bash
   cat ~/.streamlit/logs/streamlit_log.txt
   ```

2. Enable debug mode:
   ```bash
   streamlit run app.py --logger.level=debug
   ```

3. File an issue on the GitHub repository with:
   - A clear description of the problem
   - Steps to reproduce
   - Error messages and logs
   - Your environment details (OS, Python version, etc.)