# Seed-Farmer Documentation

Welcome to the official documentation for Seed-Farmer, a Python-based CI/CD library that leverages the GitOps paradigm to manage deployed code.

## What is Seed-Farmer?

Seed-Farmer is a tooling-agnostic deployment framework that supports AWS CDK, CloudFormation, Terraform, and other infrastructure-as-code tools. It uses declarative manifests to define deployable code modules and manages the state of deployed code, detecting and applying changes as needed.

Key features include:

- **Multi-Account Support**: Deploy across multiple AWS accounts with proper IAM role assumption
- **Dependency Management**: Modules can reference outputs from other modules
- **Metadata Sharing**: Modules can export metadata for use by dependent modules
- **Flexible Parameterization**: Support for various parameter sources including environment variables, AWS SSM Parameter Store, and AWS Secrets Manager
- **Security-Focused**: Least-privilege IAM roles and permissions boundaries
- **Tooling Agnosticism**: Support for various IaC tools (CDK, CloudFormation, Terraform)
- **GitOps Workflow**: Code-driven deployments with state management

## Core Concepts

Seed-Farmer organizes deployments using the following hierarchy:

- **Project**: Maps to an AWS CodeSeeder managed CodeBuild project
- **Deployment**: Represents all modules leveraging AWS resources in one or many accounts
- **Group**: Contains modules that can be deployed concurrently (no inter-dependencies)
- **Module**: The actual deployable unit of code

## Getting Started

To get started with Seed-Farmer, check out the following guides:

- [Installation](getting-started/installation.md): Install Seed-Farmer and its dependencies
- [Quick Start](getting-started/quick-start.md): Deploy your first project with Seed-Farmer
- [Bootstrapping](getting-started/bootstrapping.md): Set up your AWS accounts for Seed-Farmer

## Documentation Structure

This documentation is organized into the following sections:

- **Getting Started**: Installation and initial setup guides
- **Concepts**: Core concepts and architecture
- **Guides**: How-to guides for common tasks
- **Reference**: Detailed reference documentation for CLI commands, manifests, and module development
