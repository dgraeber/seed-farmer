# Local Deployments

This guide explains how to deploy Seed-Farmer projects locally for development and testing purposes.

## Overview

Local deployments are useful for testing changes before deploying to production environments. Seed-Farmer supports local deployments through the same CLI commands used for remote deployments, but with a few additional considerations.

## Prerequisites

Before you can deploy locally, make sure you have:

- Installed Seed-Farmer (see [Installation](../getting-started/installation.md))
- AWS credentials configured for the target account(s)
- AWS CDK bootstrapped in the target account(s)/region(s)
- Bootstrapped the toolchain and target accounts (see [Bootstrapping](../getting-started/bootstrapping.md))

## Environment Setup

First, create a Python virtual environment and install Seed-Farmer:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install seed-farmer
```

## Environment Variables

Create an `.env` file to store environment variables needed for your deployment:

```bash
echo PRIMARY_ACCOUNT=123456789012 >> .env
echo SECONDARY_ACCOUNT=210987654321 >> .env
```

These environment variables can be referenced in your deployment manifest:

```yaml
targetAccountMappings:
  - alias: primary
    accountId:
      valueFrom:
        envVariable: PRIMARY_ACCOUNT
    default: true
  - alias: secondary
    accountId:
      valueFrom:
        envVariable: SECONDARY_ACCOUNT
```

## Local Deployment Process

### 1. Create or Clone a Project

Either create a new project or clone an existing one:

```bash
# Clone an example project
git clone https://github.com/awslabs/seed-farmer.git
cd seed-farmer/examples/exampleproject
```

### 2. Review the Deployment Manifest

Review the deployment manifest to understand what will be deployed:

```bash
cat manifests/examples/deployment.yaml
```

### 3. Apply the Deployment

Apply the deployment manifest to deploy the modules:

```bash
seedfarmer apply manifests/examples/deployment.yaml --env-file .env
```

This command will:

1. Read the deployment manifest
2. Resolve the target account mappings
3. Deploy the modules in the order specified in the manifest
4. Store the deployment state in AWS Systems Manager Parameter Store

### 4. Verify the Deployment

You can verify the deployment by checking the AWS resources created in your account, or by using the Seed-Farmer CLI:

```bash
seedfarmer list deployments
seedfarmer list modules examples
```

### 5. Make Changes

Make changes to your modules or manifests as needed. For example, you might:

- Modify a module's code
- Update a parameter in a module manifest
- Add a new module to the deployment

### 6. Redeploy

After making changes, redeploy the modules:

```bash
seedfarmer apply manifests/examples/deployment.yaml --env-file .env
```

Seed-Farmer will detect the changes and update the deployment accordingly.

### 7. Clean Up

When you're done testing, destroy the deployment:

```bash
seedfarmer destroy examples --env-file .env
```

This will destroy all the modules in the deployment in the reverse order of their deployment.

## Working with Local Modules

When developing modules locally, you can reference them in your module manifest using a relative path:

```yaml
name: networking
path: modules/optionals/networking/
targetAccount: primary
parameters:
  - name: internet-accessible
    value: true
```

This allows you to make changes to the module code and test them locally before committing them to a repository.

## Working with Remote Modules

You can also reference modules from remote repositories:

```yaml
name: networking
path: git::https://github.com/awslabs/idf-modules.git//modules/network/basic-cdk?ref=release/1.0.0&depth=1
targetAccount: primary
parameters:
  - name: internet-accessible
    value: true
```

This allows you to use modules from other repositories without having to clone them locally.

## Working with Data Files

You can include data files in your module deployment using the `dataFiles` field in the module manifest:

```yaml
name: networking
path: modules/optionals/networking/
targetAccount: primary
dataFiles:
  - filePath: data/test.txt
  - filePath: config/config.json
```

These files will be included in the module bundle and available to the module during deployment.

## Best Practices for Local Development

### Use a Development Environment

Use a separate AWS account for development and testing to avoid affecting production resources.

### Use Environment Variables

Store account IDs and other sensitive information in environment variables rather than hardcoding them in manifests.

### Test Changes Incrementally

Make small changes and test them incrementally rather than making many changes at once.

### Use Version Control

Use version control to track changes to your modules and manifests.

### Document Your Modules

Document your modules with a comprehensive README.md that describes the module, its inputs, and its outputs.

### Use Consistent Naming Conventions

Use consistent naming conventions for parameters and outputs to make it easier to understand your modules.

### Handle Errors Gracefully

Include error handling in your deployspec commands to ensure that failures are reported clearly.

## Troubleshooting

### Missing AWS Credentials

If you get an error about missing AWS credentials, make sure you have configured the AWS CLI with the appropriate credentials:

```bash
aws configure
```

### Missing AWS CDK Bootstrap

If you get an error about missing AWS CDK bootstrap, make sure you have bootstrapped AWS CDK in the target account/region:

```bash
cdk bootstrap aws://ACCOUNT-NUMBER/REGION
```

### Missing Seed-Farmer Bootstrap

If you get an error about missing Seed-Farmer bootstrap, make sure you have bootstrapped the toolchain and target accounts:

```bash
seedfarmer bootstrap toolchain --project myproject --trusted-principal arn:aws:iam::123456789012:role/Admin --as-target
```

### Module Deployment Failures

If a module fails to deploy, check the AWS CodeBuild logs for more information. You can also check the AWS CloudFormation console for stack deployment failures.

## Conclusion

Local deployments are a powerful way to test changes to your Seed-Farmer projects before deploying them to production environments. By following the steps in this guide, you can set up a local development environment and iterate on your modules quickly and safely.
