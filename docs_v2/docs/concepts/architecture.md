# Architecture


# REWRITE ME!!!!
This page explains the overall architecture of Seed-Farmer, including how it integrates with AWS CodeSeeder and AWS CodeBuild to deploy modules securely.

## Overview

Seed-Farmer does not create its own deployments directly. Instead, it acts as a broker between your module code and the AWS Cloud via AWS CodeSeeder. This architecture allows for secure, repeatable deployments across multiple AWS accounts and regions.

## Security Model

Seed-Farmer uses a least-privilege security model with the following components:

- **Toolchain Role**: Created in the toolchain account and trusted by specified principals
- **Deployment Role**: Created in each target account and trusted by the toolchain role
- **Module-Specific Roles**: Created for each module with only the permissions needed for that module

This security model ensures that each component has only the permissions it needs to perform its specific tasks.

## Multi-Account Architecture

Seed-Farmer leverages IAM roles and assumes the proper role for deployment of modules. The architecture involves two main account types:

- **Toolchain Account**: The primary account that stores deployment metadata and coordinates deployments
- **Target Account(s)**: The account(s) where modules are actually deployed

![Multi-Account Architecture](../static/seedfarmer-architecture_transparent.png)

The deployment process follows these steps:

1. Invoke the Seed-Farmer CLI with a role that can assume the toolchain role
2. Seed-Farmer, via the toolchain role, reads/writes deployment metadata with AWS Systems Manager
3. Seed-Farmer's toolchain role assumes the deployment role in all target accounts to fetch module metadata
4. Seed-Farmer, via the deployment role in the target account, initiates module deployment
5. Seed-Farmer, via the deployment role, interacts with S3 for bundle references
6. Seed-Farmer, via the deployment role, attaches the module role to the AWS Codebuild job specification
7. Seed-Farmer, via the deployment role, starts the AWS Codebuild job to deploy
8. The module role interacts with the AWS Services as defined by the module being deployed 


## DEREK FIX ME


## Seed-Farmer Seedkit

AWS CodeSeeder is an open-source tool that Seed-Farmer uses to securely deploy modules in AWS CodeBuild. Seed-Farmer checks if a seedkit is deployed in every account/region mapping defined in the deployment manifest and deploys it if not found.

### Updating the Seed-Farmer Seedkit

The seedkit has a known naming convention of `aws-codeseeder-<project name>` as a CloudFormation stack name. For example, the name of the seedkit stack for a project named `addf` would be `aws-codeseeder-addf`.

To update the seedkit, you can either:

- Delete the CloudFormation template in that account/region mapping and let Seed-Farmer redeploy it during the next deployment
- Use the Seed-Farmer CLI commands to deploy it manually (this must occur in each deployment account)

!!! warning
    Deleting the seedkit stack deletes the AWS CodeBuild project and the entire history. Existing Seed-Farmer deployments (the modules deployed) will be unaffected and continue to run as before, but you will lose the build job history.



## State Management

Seed-Farmer stores deployment state in AWS Systems Manager Parameter Store. This includes:

- Deployment metadata
- Module metadata
- Module outputs

This state management allows Seed-Farmer to track what has been deployed and detect changes that require redeployment.

## Dependency Management

Seed-Farmer has a shared-responsibility model for dependency management of modules. It includes guardrails to:

- Prevent deletion of modules that have downstream modules dependent on them
- Prevent circular references of modules

However, it is up to the end user to be aware of and manage the relationships between modules to assess the impact of changes to modules via redeployment.

### Force Dependency Redeploy

When a module changes (is redeployed), downstream modules that are dependent on it may need to consume those changes. The `forceDependencyRedeploy` flag in the deployment manifest tells Seed-Farmer to force a redeploy of all modules impacted by the redeploy of another module.

!!! warning
    This is an indiscriminate feature that is not granular enough to detect what is causing a redeploy, only that one needs to occur. Any change to a module will trigger a redeploy of that module and all downstream modules that depend on it, even if the underlying logic or artifact has not changed.

## Conclusion

The Seed-Farmer architecture provides a secure, flexible, and scalable way to deploy infrastructure across multiple AWS accounts and regions. By leveraging AWS CodeSeeder and AWS CodeBuild, it ensures that deployments are repeatable, auditable, and follow the principle of least privilege.
