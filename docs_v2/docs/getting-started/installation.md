# Installation

This guide will walk you through the process of installing Seed-Farmer and its dependencies.

## Prerequisites

Before installing Seed-Farmer, ensure you have the following prerequisites:

- Python 3.9 or later (preferably later)
- AWS CLI configured with appropriate credentials
- AWS CDK (for CDK-based modules)

## Installing Seed-Farmer

Seed-Farmer uses uv to install.  It is recommended to [install](https://docs.astral.sh/uv/getting-started/installation/) uv and use that as the primary installation tool. 

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```


### Using uv

Install Seed-Farmer as a tool.

```bash
uv tool install seed-farmer 

```
You can pin to a particular version by referring to the version in the install ( see the [pypi release history](https://pypi.org/project/seed-farmer/#history) )

### Using pip

Install Seed-Farmer is using pip:

```bash
uv pip install seed-farmer
```

### From Source

You can also install Seed-Farmer from source:

```bash
git clone https://github.com/awslabs/seed-farmer.git
cd seed-farmer
uv pip install -e .
```

## Verifying the Installation

To verify that Seed-Farmer is installed correctly, run:

```bash
seedfarmer --version
```

This should display the version of Seed-Farmer that you have installed.

## Setting Up Your Environment

### AWS Credentials

Seed-Farmer uses the AWS credentials configured in your environment. You can configure these using the AWS CLI:

```bash
aws configure
```

Alternatively, you can set the following environment variables:

```bash
export AWS_ACCESS_KEY_ID=your-access-key
export AWS_SECRET_ACCESS_KEY=your-secret-key
export AWS_REGION=your-region
```

### AWS CDK

If you're using CDK-based modules, you'll need to install the AWS CDK in each target account:

```bash
npm install -g aws-cdk
```

And bootstrap your AWS environment:

```bash
cdk bootstrap aws://ACCOUNT-NUMBER/REGION
```

Replace `ACCOUNT-NUMBER` with your AWS account number and `REGION` with your AWS region.

## Next Steps

Now that you have Seed-Farmer installed, you can:

- Follow the [Quick Start](quick-start.md) guide to deploy your first project
- Learn how to [bootstrap](bootstrapping.md) your AWS accounts for Seed-Farmer
- Explore the [core concepts](../concepts/index.md) behind Seed-Farmer
