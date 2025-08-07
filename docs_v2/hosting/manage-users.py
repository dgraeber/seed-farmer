#!/usr/bin/env python3
"""
Script to manage users in the Lambda@Edge authentication function
"""

import boto3
import json
import argparse
import getpass
import sys

def get_lambda_function():
    """Get the Lambda@Edge function"""
    cf = boto3.client('cloudformation', region_name='us-east-1')  # Lambda@Edge is always in us-east-1
    
    try:
        response = cf.describe_stacks(StackName='MkDocsHostingStack')
        # We need to find the Lambda function ARN from the stack resources
        resources = cf.describe_stack_resources(StackName='MkDocsHostingStack')
        
        lambda_arn = None
        for resource in resources['StackResources']:
            if resource['ResourceType'] == 'AWS::Lambda::Function' and 'Auth' in resource['LogicalResourceId']:
                lambda_arn = resource['PhysicalResourceId']
                break
        
        if not lambda_arn:
            print("❌ Could not find Lambda@Edge function")
            sys.exit(1)
            
        return lambda_arn
    except Exception as e:
        print(f"❌ Error finding Lambda function: {e}")
        sys.exit(1)

def get_current_users(function_name):
    """Extract current users from Lambda function code"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    try:
        response = lambda_client.get_function(FunctionName=function_name)
        code = response['Code']
        
        # Download and decode the function code
        import zipfile
        import io
        import urllib.request
        
        zip_response = urllib.request.urlopen(code['Location'])
        zip_data = zip_response.read()
        
        with zipfile.ZipFile(io.BytesIO(zip_data)) as zip_file:
            with zip_file.open('index.js') as js_file:
                js_content = js_file.read().decode('utf-8')
        
        # Extract users object (simple regex - could be improved)
        import re
        users_match = re.search(r'const users = \{([^}]+)\}', js_content)
        if users_match:
            users_str = users_match.group(1)
            # Parse the users (this is a simple implementation)
            users = {}
            for line in users_str.split('\n'):
                line = line.strip()
                if ':' in line and not line.startswith('//'):
                    parts = line.split(':')
                    if len(parts) >= 2:
                        username = parts[0].strip().strip("'\"")
                        password = parts[1].strip().strip("'\"").rstrip(',')
                        if username and password:
                            users[username] = password
            return users
        
        return {}
    except Exception as e:
        print(f"❌ Error reading current users: {e}")
        return {}

def update_lambda_function(function_name, users):
    """Update the Lambda function with new users"""
    lambda_client = boto3.client('lambda', region_name='us-east-1')
    
    # Generate the users object string
    users_str = "{\n"
    for username, password in users.items():
        users_str += f"    '{username}': '{password}',\n"
    users_str += "}"
    
    # Generate the complete function code
    function_code = f"""
const users = {users_str};

exports.handler = async (event) => {{
    const request = event.Records[0].cf.request;
    const headers = request.headers;
    
    // Check if Authorization header exists
    if (!headers.authorization) {{
        return {{
            status: '401',
            statusDescription: 'Unauthorized',
            headers: {{
                'www-authenticate': [{{
                    key: 'WWW-Authenticate',
                    value: 'Basic realm="Seed Farmer Documentation"'
                }}],
                'content-type': [{{
                    key: 'Content-Type',
                    value: 'text/html'
                }}]
            }},
            body: `
                <html>
                <head><title>401 Unauthorized</title></head>
                <body>
                    <h1>Unauthorized</h1>
                    <p>Please provide valid credentials to access the Seed Farmer documentation.</p>
                </body>
                </html>
            `
        }};
    }}
    
    // Parse Basic Auth header
    const authHeader = headers.authorization[0].value;
    const encoded = authHeader.split(' ')[1];
    const decoded = Buffer.from(encoded, 'base64').toString('utf-8');
    const [username, password] = decoded.split(':');
    
    // Validate credentials
    if (!users[username] || users[username] !== password) {{
        return {{
            status: '401',
            statusDescription: 'Unauthorized',
            headers: {{
                'www-authenticate': [{{
                    key: 'WWW-Authenticate',
                    value: 'Basic realm="Seed Farmer Documentation"'
                }}],
                'content-type': [{{
                    key: 'Content-Type',
                    value: 'text/html'
                }}]
            }},
            body: `
                <html>
                <head><title>401 Unauthorized</title></head>
                <body>
                    <h1>Unauthorized</h1>
                    <p>Invalid credentials. Please contact your team administrator.</p>
                </body>
                </html>
            `
        }};
    }}
    
    // Allow the request to proceed
    return request;
}};
"""
    
    try:
        # Update the function code
        response = lambda_client.update_function_code(
            FunctionName=function_name,
            ZipFile=create_zip_file(function_code)
        )
        
        print(f"✅ Lambda function updated successfully")
        print(f"🔄 New version: {response['Version']}")
        print("⏱️  Changes will take 5-10 minutes to propagate to CloudFront")
        
    except Exception as e:
        print(f"❌ Error updating Lambda function: {e}")
        sys.exit(1)

def create_zip_file(js_code):
    """Create a zip file containing the JavaScript code"""
    import zipfile
    import io
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        zip_file.writestr('index.js', js_code)
    
    return zip_buffer.getvalue()

def main():
    parser = argparse.ArgumentParser(description='Manage users for MkDocs site authentication')
    parser.add_argument('action', choices=['list', 'add', 'remove', 'update'], 
                       help='Action to perform')
    parser.add_argument('--username', help='Username for add/remove/update actions')
    parser.add_argument('--password', help='Password for add/update actions')
    
    args = parser.parse_args()
    
    # Get Lambda function
    function_name = get_lambda_function()
    print(f"📍 Working with Lambda function: {function_name}")
    
    # Get current users
    current_users = get_current_users(function_name)
    
    if args.action == 'list':
        print("\n👥 Current users:")
        if not current_users:
            print("   No users found")
        else:
            for username in current_users.keys():
                print(f"   - {username}")
    
    elif args.action == 'add':
        if not args.username:
            args.username = input("Enter username: ")
        
        if args.username in current_users:
            print(f"❌ User '{args.username}' already exists. Use 'update' to change password.")
            sys.exit(1)
        
        if not args.password:
            args.password = getpass.getpass("Enter password: ")
        
        current_users[args.username] = args.password
        update_lambda_function(function_name, current_users)
        print(f"✅ User '{args.username}' added successfully")
    
    elif args.action == 'remove':
        if not args.username:
            args.username = input("Enter username to remove: ")
        
        if args.username not in current_users:
            print(f"❌ User '{args.username}' not found")
            sys.exit(1)
        
        del current_users[args.username]
        update_lambda_function(function_name, current_users)
        print(f"✅ User '{args.username}' removed successfully")
    
    elif args.action == 'update':
        if not args.username:
            args.username = input("Enter username to update: ")
        
        if args.username not in current_users:
            print(f"❌ User '{args.username}' not found")
            sys.exit(1)
        
        if not args.password:
            args.password = getpass.getpass("Enter new password: ")
        
        current_users[args.username] = args.password
        update_lambda_function(function_name, current_users)
        print(f"✅ Password for '{args.username}' updated successfully")

if __name__ == "__main__":
    main()
