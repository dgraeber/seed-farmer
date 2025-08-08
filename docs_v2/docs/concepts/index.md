# Core Concepts

This section explains the core concepts behind Seed-Farmer, providing a deeper understanding of how the system works.

## Architecture

The [Architecture](architecture.md) page explains the overall architecture of Seed-Farmer, including how it integrates with AWS CodeSeeder and AWS CodeBuild to deploy modules securely.

## Multi-Account Support

Seed-Farmer is designed to work across multiple AWS accounts. The [Multi-Account Support](multi-account.md) page explains how Seed-Farmer manages deployments across toolchain and target accounts, including IAM role assumption and permissions management.

## Key Components

### Project

A project in Seed-Farmer has a direct one-to-one relationship with an AWS CodeBuild project. You can have multiple projects in an account, and they are isolated from one another (no project can use artifacts from another project).

### Deployment

A deployment represents all the modules leveraging AWS resources in one or many accounts. It is metadata that gives isolation from other deployments in the same project.

### Group

A group represents all modules that can be deployed concurrently. No module in a group can have a dependency on another module in the same group. Seed-Farmer keeps track of the ordering of groups for deployment and reverses the ordering of the groups for destruction.

### Module

A module is what gets deployed. It is represented by code. A module can be deployed multiple times in the same deployment as long as it has a unique logical name.


![Project Definition](../static/project-definition_transparent.png)

## Dependency Management

Seed-Farmer manages dependencies between modules, ensuring that modules are deployed in the correct order. Modules can reference outputs from other modules, allowing for complex deployment scenarios.

## Metadata Sharing

Modules can export metadata for use by dependent modules. This allows for information sharing between modules, such as resource IDs, endpoints, and other configuration values.

## Parameter System

Seed-Farmer has a sophisticated parameter system that supports various parameter sources, including:

- User-defined parameters
- Module metadata references
- Global and regional parameters
- Environment variables
- AWS SSM Parameter Store values
- AWS Secrets Manager values

## Security

Seed-Farmer is designed with security in mind, using least-privilege IAM roles and permissions boundaries to ensure that deployments have only the permissions they need.
