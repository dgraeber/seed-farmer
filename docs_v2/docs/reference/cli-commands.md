# CLI Commands

This page provides a comprehensive reference for all Seed-Farmer CLI commands, including their options and usage examples.

## Global Options

These options can be used with any command:

- `--help`: Show help message and exit
- `--version`: Show version and exit
- `--debug`: Enable debug logging
- `--profile`: AWS profile to use
- `--region`: AWS region to use

## Bootstrap Commands

### bootstrap toolchain

Bootstrap a toolchain account with the necessary IAM roles and permissions.

```bash
seedfarmer bootstrap toolchain \
  --project PROJECT_NAME \
  --trusted-principal PRINCIPAL_ARN \
  [--permissions-boundary BOUNDARY_ARN] \
  [--as-target] \
  [--synth] \
  [--profile PROFILE] \
  [--region REGION] \
  [--qualifier QUALIFIER] \
  [--role-prefix ROLE_PREFIX] \
  [--policy-prefix POLICY_PREFIX] \
  [--policy-arn POLICY_ARN]
```

#### Required Parameters

- `--project` (`-p`): Project identifier
- `--trusted-principal` (`-t`): ARN of principals trusted to assume the toolchain role (can be used multiple times)

#### Optional Parameters

- `--permissions-boundary` (`-b`): ARN of a managed policy to set as the permissions boundary on the toolchain role
- `--as-target`: Also bootstrap the account as a target account
- `--synth`: Synthesize a CloudFormation template only (do not deploy)
- `--profile`: AWS profile to use
- `--region`: AWS region to use
- `--qualifier`: A qualifier to append to the toolchain role (alpha-numeric, max 6 characters)
- `--role-prefix`: An IAM path prefix to use with the Seed-Farmer roles
- `--policy-prefix`: An IAM path prefix to use with the Seed-Farmer policies
- `--policy-arn` (`-pa`): ARN of existing policy to attach to the target role (can be used multiple times)

### bootstrap target

Bootstrap a target account with the necessary IAM roles and permissions.

```bash
seedfarmer bootstrap target \
  --project PROJECT_NAME \
  --toolchain-account ACCOUNT_ID \
  [--permissions-boundary BOUNDARY_ARN] \
  [--synth] \
  [--profile PROFILE] \
  [--region REGION] \
  [--qualifier QUALIFIER] \
  [--role-prefix ROLE_PREFIX] \
  [--policy-arn POLICY_ARN]
```

#### Required Parameters

- `--project` (`-p`): Project identifier
- `--toolchain-account` (`-t`): Account ID of the toolchain account trusted to assume the target account's deployment role

#### Optional Parameters

- `--permissions-boundary` (`-b`): ARN of a managed policy to set as the permissions boundary on the target role
- `--synth`: Synthesize a CloudFormation template only (do not deploy)
- `--profile`: AWS profile to use
- `--region`: AWS region to use
- `--qualifier`: A qualifier to append to the target role (alpha-numeric, max 6 characters)
- `--role-prefix`: An IAM path prefix to use with the Seed-Farmer roles
- `--policy-arn` (`-pa`): ARN of existing policy to attach to the target role (can be used multiple times)

## Deployment Commands

### apply

Apply a deployment manifest to deploy modules.

```bash
seedfarmer apply MANIFEST_PATH \
  [--env-file ENV_FILE] \
  [--project PROJECT] \
  [--toolchain-region REGION] \
  [--profile PROFILE] \
  [--region REGION] \
  [--qualifier QUALIFIER] \
  [--role-prefix ROLE_PREFIX] \
  [--policy-prefix POLICY_PREFIX] \
  [--policy-arn POLICY_ARN] \
  [--local]
```

#### Required Parameters

- `MANIFEST_PATH`: Path to the deployment manifest file

#### Optional Parameters

- `--env-file`: Path to a file containing environment variables
- `--project`: Project identifier (overrides the one in the manifest)
- `--toolchain-region`: Region for the toolchain account (overrides the one in the manifest)
- `--profile`: AWS profile to use
- `--region`: AWS region to use
- `--qualifier`: A qualifier to append to the roles (alpha-numeric, max 6 characters)
- `--role-prefix`: An IAM path prefix to use with the Seed-Farmer roles
- `--policy-prefix`: An IAM path prefix to use with the Seed-Farmer policies
- `--policy-arn` (`-pa`): ARN of existing policy to attach to the target role (can be used multiple times)
- `--local`: Execute deployment locally using Docker instead of AWS CodeBuild (development only, single account/region)

### destroy

Destroy a deployment.

```bash
seedfarmer destroy DEPLOYMENT_NAME \
  [--env-file ENV_FILE] \
  [--project PROJECT] \
  [--toolchain-region REGION] \
  [--profile PROFILE] \
  [--region REGION] \
  [--qualifier QUALIFIER] \
  [--role-prefix ROLE_PREFIX] \
  [--policy-prefix POLICY_PREFIX] \
  [--policy-arn POLICY_ARN] \
  [--local]
```

#### Required Parameters

- `DEPLOYMENT_NAME`: Name of the deployment to destroy

#### Optional Parameters

- `--env-file`: Path to a file containing environment variables
- `--project`: Project identifier
- `--toolchain-region`: Region for the toolchain account
- `--profile`: AWS profile to use
- `--region`: AWS region to use
- `--qualifier`: A qualifier to append to the roles (alpha-numeric, max 6 characters)
- `--role-prefix`: An IAM path prefix to use with the Seed-Farmer roles
- `--policy-prefix`: An IAM path prefix to use with the Seed-Farmer policies
- `--policy-arn` (`-pa`): ARN of existing policy to attach to the target role (can be used multiple times)
- `--local`: Execute destruction locally using Docker instead of AWS CodeBuild (development only, single account/region)

### list deployments

List all deployments in a project.

```bash
seedfarmer list deployments \
  [--project PROJECT] \
  [--toolchain-region REGION] \
  [--profile PROFILE] \
  [--region REGION] \
  [--qualifier QUALIFIER] \
  [--role-prefix ROLE_PREFIX]
```

#### Optional Parameters

- `--project`: Project identifier
- `--toolchain-region`: Region for the toolchain account
- `--profile`: AWS profile to use
- `--region`: AWS region to use
- `--qualifier`: A qualifier to append to the roles (alpha-numeric, max 6 characters)
- `--role-prefix`: An IAM path prefix to use with the Seed-Farmer roles

### list modules

List all modules in a deployment.

```bash
seedfarmer list modules DEPLOYMENT_NAME \
  [--project PROJECT] \
  [--toolchain-region REGION] \
  [--profile PROFILE] \
  [--region REGION] \
  [--qualifier QUALIFIER] \
  [--role-prefix ROLE_PREFIX]
```

#### Required Parameters

- `DEPLOYMENT_NAME`: Name of the deployment

#### Optional Parameters

- `--project`: Project identifier
- `--toolchain-region`: Region for the toolchain account
- `--profile`: AWS profile to use
- `--region`: AWS region to use
- `--qualifier`: A qualifier to append to the roles (alpha-numeric, max 6 characters)
- `--role-prefix`: An IAM path prefix to use with the Seed-Farmer roles

## Seedkit Commands

### seedkit deploy

Deploy a seedkit in the specified account and region.

```bash
seedfarmer seedkit deploy PROJECT_NAME \
  [--policy-arn POLICY_ARN] \
  [--deploy-codeartifact] \
  [--profile PROFILE] \
  [--region REGION] \
  [--vpc-id VPC_ID] \
  [--subnet-id SUBNET_ID] \
  [--sg-id SG_ID] \
  [--permissions-boundary-arn BOUNDARY_ARN] \
  [--synth] \
  [--debug]
```

#### Required Parameters

- `PROJECT_NAME`: Project identifier

#### Optional Parameters

- `--policy-arn`: ARN of existing policy to attach to the seedkit role
- `--deploy-codeartifact`: Deploy the optional CodeArtifact Domain and Repository (default: skip-codeartifact)
- `--profile`: AWS profile to use
- `--region`: AWS region to use
- `--vpc-id`: The VPC ID that the CodeBuild Project resides in (only 1)
- `--subnet-id`: A subnet that the CodeBuild Project resides in (can be used multiple times)
- `--sg-id`: A Security Group in the VPC that the CodeBuild Project can leverage (up to 5, can be used multiple times)
- `--permissions-boundary-arn` (`-b`): ARN of a Managed Policy to set as the Permission Boundary on the CodeBuild Role
- `--synth`: Synthesize seedkit template only. Do not deploy (default: no-synth)
- `--debug`: Enable detailed logging (default: no-debug)

### seedkit destroy

Destroy a seedkit in the specified account and region.

```bash
seedfarmer seedkit destroy PROJECT_NAME \
  [--profile PROFILE] \
  [--region REGION] \
  [--debug]
```

#### Required Parameters

- `PROJECT_NAME`: Project identifier

#### Optional Parameters

- `--profile`: AWS profile to use
- `--region`: AWS region to use
- `--debug`: Enable detailed logging (default: no-debug)

## Module Commands

### init module

Initialize a new module.

```bash
seedfarmer init module \
  --group GROUP_NAME \
  --module MODULE_NAME \
  [--path PATH]
```

#### Required Parameters

- `--group` (`-g`): Group name for the module
- `--module` (`-m`): Module name

#### Optional Parameters

- `--path`: Path to create the module in (default: modules/GROUP_NAME/MODULE_NAME)

### metadata add

Add metadata to a module. **This command can only be run within the deployspec execution context** (CodeBuild or local Docker container during module deployment).

```bash
seedfarmer metadata add \
  [--key KEY --value VALUE] \
  [--json JSON]
```

#### Optional Parameters

- `--key` (`-k`): Key for the metadata
- `--value` (`-v`): Value for the metadata
- `--json` (`-j`): JSON string to add as metadata

### metadata convert

Convert CDK output to Seed-Farmer metadata. **This command can only be run within the deployspec execution context** (CodeBuild or local Docker container during module deployment).

```bash
seedfarmer metadata convert \
  [--file FILE] \
  [--jq JQ_QUERY]
```

#### Optional Parameters

- `--file` (`-f`): Path to the CDK exports file (default: cdk-exports.json)
- `--jq` (`-jq`): JQ query to extract metadata from the CDK exports file

### metadata depmod

Get the fully resolved deployment name of the module. **This command can only be run within the deployspec execution context** (CodeBuild or local Docker container during module deployment).

```bash
seedfarmer metadata depmod
```

### metadata paramvalue

Get the parameter value based on the suffix. **This command can only be run within the deployspec execution context** (CodeBuild or local Docker container during module deployment).

```bash
seedfarmer metadata paramvalue \
  --suffix SUFFIX
```

#### Required Parameters

- `--suffix` (`-s`): Suffix of the parameter name

## Examples

### Bootstrap a Toolchain Account

```bash
seedfarmer bootstrap toolchain \
  --project myproject \
  --trusted-principal arn:aws:iam::123456789012:role/Admin \
  --as-target
```

### Bootstrap a Target Account

```bash
seedfarmer bootstrap target \
  --project myproject \
  --toolchain-account 123456789012
```

### Apply a Deployment

```bash
seedfarmer apply manifests/mydeployment/deployment.yaml \
  --env-file .env
```

### Apply a Local Deployment

```bash
seedfarmer apply manifests/mydeployment/deployment.yaml \
  --local \
  --env-file .env
```

### Destroy a Deployment

```bash
seedfarmer destroy mydeployment \
  --env-file .env
```

### Destroy a Local Deployment

```bash
seedfarmer destroy mydeployment \
  --local \
  --env-file .env
```

### Deploy Seedkit Manually

```bash
seedfarmer seedkit deploy myproject \
  --region us-east-1
```

### Deploy Seedkit with VPC Configuration

```bash
seedfarmer seedkit deploy myproject \
  --region us-east-1 \
  --vpc-id vpc-12345678 \
  --subnet-id subnet-abcd1234 \
  --sg-id sg-ijkl9012
```

### Destroy Seedkit

```bash
seedfarmer seedkit destroy myproject \
  --region us-east-1
```

### List Deployments

```bash
seedfarmer list deployments \
  --project myproject
```

### List Modules in a Deployment

```bash
seedfarmer list modules mydeployment \
  --project myproject
```

### Initialize a New Module

```bash
seedfarmer init module \
  --group mygroup \
  --module mymodule
```

### Add Metadata in a Deployspec

```bash
seedfarmer metadata add \
  --key VpcId \
  --value vpc-12345678
```

### Convert CDK Output to Metadata in a Deployspec

```bash
seedfarmer metadata convert
```

### Get Deployment Module Name in a Deployspec

```bash
export DEPMOD=$(seedfarmer metadata depmod)
```

### Get Parameter Value in a Deployspec

```bash
export DEPLOYMENT_NAME=$(seedfarmer metadata paramvalue -s DEPLOYMENT_NAME)
