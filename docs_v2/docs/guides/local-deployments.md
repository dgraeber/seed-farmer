# Local Deployments

This guide explains how to deploy Seed-Farmer projects locally using Docker for development and testing purposes. Local deployments provide a fast feedback loop for module development while maintaining consistency with remote deployments.

## What are Local Deployments?

Local deployments execute your module's deployspec using Docker containers on your local machine instead of AWS CodeBuild. This approach:

- **Speeds up development**: No need to wait for CodeBuild project startup
- **Reduces costs**: No CodeBuild charges during development
- **Maintains consistency**: Uses the same container images as remote deployments
- **Enables offline development**: Work without constant AWS connectivity

## Key Differences from Remote Deployments

| Aspect | Local Deployments | Remote Deployments |
|--------|------------------|-------------------|
| **Execution Environment** | Docker on local machine | AWS CodeBuild |
| **Account/Region Support** | Single account/region only | Multi-account/region |
| **Manifest Changes** | Automatic region override | Uses manifest as-is |
| **Performance** | Faster startup | Slower startup, better for production |
| **Cost** | No AWS charges | CodeBuild charges apply |
| **Networking** | Local machine network | AWS VPC (configurable) |

## Prerequisites

Before you can deploy locally, ensure you have:

### Required Software
- **Docker**: Must be installed and running on your local machine
- **Seed-Farmer**: Installed via pip (`pip install seed-farmer`)
- **AWS CLI**: Configured with appropriate credentials

### AWS Setup
- **AWS credentials**: Configured for the target account
- **AWS CDK bootstrap**: Completed in the target account/region
- **Seed-Farmer bootstrap**: Toolchain and target accounts bootstrapped
- **Seedkit infrastructure**: Deployed in the target account/region

### Docker Requirements

Local deployments require Docker to run CodeBuild-compatible container images:

```bash
# Verify Docker is installed and running
docker --version
docker info
```

**Supported Docker Images**:

- `public.ecr.aws/codebuild/amazonlinux2-x86_64-standard:5.0` 

!!! note "Image Support"
    Currently, local deployments only support the Amazon Linux 2 x86_64 standard image. Support for additional CodeBuild images will be added in future releases. The image used is driven by your deployment and module manifest configuration.

!!! note "Image Conversion"
    Seed-Farmer automatically converts AWS CodeBuild image references (e.g., `aws/codebuild/amazonlinux2-x86_64-standard:5.0`) to their public ECR equivalents for local use.

!!! info "CodeBuild Agent"
    Local deployments use Docker to simulate the AWS CodeBuild environment. For more information about CodeBuild's local execution capabilities, see the [AWS CodeBuild Agent documentation](https://docs.aws.amazon.com/codebuild/latest/userguide/use-codebuild-agent.html).

## Environment Setup

Seed-Farmer uses **uv** for Python environment management both locally and within Docker containers. Install Seed-Farmer using `uv`:

```bash
# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create a virtual environment and install Seed-Farmer
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install seed-farmer

# Or install as a tool (recommended)
uv tool install seed-farmer
```

During local deployment, the Docker container automatically:
- Creates a Python virtual environment using `uv`
- Installs the correct version of seed-farmer with `uv tool install`
- Manages all Python dependencies within the container using `uv`

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

## Single Account/Region Limitation

**Important**: Local deployments are limited to a **single AWS account and region**. This is a fundamental constraint of the local deployment architecture.

### Automatic Region Override

When using local deployments, Seed-Farmer automatically overrides all target regions in your manifests to use your current AWS session's region. This means:

- **No manifest changes required**: Your existing multi-region manifests work without modification
- **Automatic conversion**: All modules deploy to your session's region regardless of manifest settings
- **Simplified development**: Focus on module logic without worrying about region configuration

### Example Behavior

If your manifest specifies multiple regions:

```yaml
targetAccountMappings:
  - alias: primary
    accountId: 123456789012
    regionMappings:
      - region: us-east-1  # Will be overridden
      - region: us-west-2  # Will be overridden
      - region: eu-west-1  # Will be overridden
```

During local deployment, all modules will deploy to your current AWS session's region (e.g., `us-west-2` if that's your configured region).

## Seedkit Dependency

Local deployments **require the seedkit infrastructure** to be deployed in your target account and region, just like remote deployments. The seedkit provides essential services:

- **S3 bucket**: For storing deployment bundles and artifacts
- **IAM roles**: For module execution permissions
- **CloudWatch logs**: For deployment logging
- **Metadata storage**: For tracking deployment state

### Ensuring Seedkit is Available

The seedkit is automatically deployed during your first deployment (local or remote). To verify it exists:

```bash
# Check if seedkit stack exists
aws cloudformation describe-stacks --stack-name aws-codeseeder-myproject

```
If the seedkit is not deployed, seedfarmer will automatically deploy it on the first execution.

For more information about the seedkit, see [Seedkit Infrastructure](../concepts/architecture.md#seedkit-infrastructure).

## Local Deployment Process

### 1. Verify Prerequisites

Ensure Docker is running and AWS credentials are configured:

```bash
# Check Docker
docker info

# Check AWS credentials and region
aws sts get-caller-identity
aws configure get region
```

### 2. Enable Local Mode

Use the `--local` flag to enable local deployments:

```bash
seedfarmer apply manifests/examples/deployment.yaml --local --env-file .env
```

### 3. Local Deployment Flow

When you run a local deployment, Seed-Farmer:

1. **Creates a bundle**: Packages your module code and data files
2. **Starts Docker container**: Uses the specified CodeBuild image
3. **Mounts the bundle**: Makes your code available in the container
4. **Executes deployspec**: Runs your module's deployment commands
5. **Captures outputs**: Stores metadata and logs locally and in AWS
6. **Cleans up**: Removes temporary containers and files

### 4. Monitor Progress

Local deployments provide real-time output:

```bash
seedfarmer apply manifests/examples/deployment.yaml --local
# Output shows Docker container execution in real-time
# No need to check CloudWatch logs
```

### 5. Verify Deployment

Check your deployment status:

```bash
seedfarmer list deployments
seedfarmer list modules -d examples
```

### 6. Iterate and Test

Make changes to your modules and redeploy:

```bash
# Edit your module code
vim modules/mymodule/app.py

# Redeploy with local execution
seedfarmer apply manifests/examples/deployment.yaml --local
```

### 7. Clean Up

Destroy the deployment when finished:

```bash
seedfarmer destroy examples --local
```

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
