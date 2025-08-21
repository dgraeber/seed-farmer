# Quick Start Guide

This quick start guide will help you get up and running with Seed-Farmer quickly. It provides a step-by-step walkthrough of creating and deploying a simple project.

!!! note
    This is an abbreviated version of the deployment process. For a more detailed guide, see the [Deployment Guide](../guides/project-development.md).

## Prerequisites

Before you begin, make sure you have:

- Installed Seed-Farmer (see [Installation](installation.md))
- AWS credentials configured
- AWS CDK bootstrapped in your account/region

## Environment Setup

First, create a Python virtual environment and install Seed-Farmer:

```bash
uv tool install seed-farmer
```

Then, bootstrap your AWS CDK environment:

```bash
cdk bootstrap aws://123456789012/us-east-1
```

Replace `123456789012` with your AWS account ID and `us-east-1` with your preferred region.

## Bootstrap Your Account

Next, bootstrap your account for Seed-Farmer:

```bash
seedfarmer bootstrap toolchain \
--project exampleproj \
-t arn:aws:iam::123456789012:role/Admin \
--as-target
```

This command:

1. Sets up the toolchain account with the necessary IAM roles
2. Also bootstraps the account as a target account (`--as-target`)
3. Uses the project name `exampleproj`
4. Trusts the `Admin` role to assume the toolchain role

## Deploy a Sample Project

Now you can deploy a sample project:

```bash
mkdir mycodebase && cd mycodebase
git clone https://github.com/awslabs/seed-farmer.git
cd seed-farmer/examples/exampleproject
echo PRIMARY_ACCOUNT=123456789012 >> .env
seedfarmer apply manifests/examples/deployment.yaml --env-file .env
```

This will:

1. Clone the Seed-Farmer repository
2. Navigate to the example project
3. Create an environment file with your account ID
4. Deploy the example project using the deployment manifest

## Verify the Deployment

You can verify the deployment by checking the AWS resources created in your account, or by using the Seed-Farmer CLI:

```bash
seedfarmer list deployments
```

This will show all deployments in your project.

## Clean Up

To clean up the resources created by the deployment:

```bash
seedfarmer destroy examples --env-file .env
```

This will destroy all the modules in the deployment in the reverse order of their deployment.

## Next Steps

Now that you've deployed your first project with Seed-Farmer, you can:

- Learn how to [bootstrap](bootstrapping.md) multiple accounts
- Explore the [core concepts](../concepts/index.md) behind Seed-Farmer
- Learn how to [create your own modules](../guides//module-development.md)
- Check out the [guides](../guides/index.md) for common tasks
