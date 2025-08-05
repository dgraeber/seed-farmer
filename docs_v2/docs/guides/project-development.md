# Project Development

This guide provides best practices and tips for developing projects with Seed-Farmer. It covers organizing your code, managing dependencies, and structuring your manifests.

## Project Structure

A typical Seed-Farmer project has the following structure:

```
project-root/
├── .env                      # Environment variables
├── manifests/                # Deployment manifests
│   ├── dev/                  # Development environment
│   │   ├── deployment.yaml   # Deployment manifest
│   │   └── modules/          # Module manifests
│   │       ├── group1.yaml
│   │       └── group2.yaml
│   └── prod/                 # Production environment
│       ├── deployment.yaml
│       └── modules/
│           ├── group1.yaml
│           └── group2.yaml
├── modules/                  # Module code
│   ├── group1/
│   │   ├── module1/
│   │   │   ├── README.md
│   │   │   ├── deployspec.yaml
│   │   │   ├── modulestack.yaml
│   │   │   └── ...
│   │   └── module2/
│   │       ├── README.md
│   │       ├── deployspec.yaml
│   │       ├── modulestack.yaml
│   │       └── ...
│   └── group2/
│       └── ...
└── README.md                 # Project documentation
```

This structure separates the deployment manifests from the module code, allowing you to have different deployment configurations for different environments while reusing the same module code.

## Creating a New Project

To create a new project, follow these steps:

1. Create the project directory structure
2. Create the deployment manifests
3. Create the module manifests
4. Create the module code

### Creating the Project Directory Structure

```bash
mkdir -p myproject/{manifests/{dev,prod}/modules,modules}
cd myproject
```

### Creating the Deployment Manifests

Create a deployment manifest for each environment:

```bash
touch manifests/dev/deployment.yaml
touch manifests/prod/deployment.yaml
```

Edit the deployment manifests to define the deployment, including groups of modules and target account mappings. For example:

```yaml
# manifests/dev/deployment.yaml
name: dev
toolchainRegion: us-west-2
forceDependencyRedeploy: False
groups:
  - name: core
    path: manifests/dev/modules/core.yaml
  - name: services
    path: manifests/dev/modules/services.yaml
targetAccountMappings:
  - alias: primary
    accountId:
      valueFrom:
        envVariable: DEV_ACCOUNT
    default: true
    regionMappings:
      - region: us-east-1
        default: true
```

### Creating the Module Manifests

Create a module manifest for each group:

```bash
touch manifests/dev/modules/core.yaml
touch manifests/dev/modules/services.yaml
```

Edit the module manifests to define the modules in each group. For example:

```yaml
# manifests/dev/modules/core.yaml
name: networking
path: modules/core/networking/
targetAccount: primary
parameters:
  - name: internet-accessible
    value: true
---
name: security
path: modules/core/security/
targetAccount: primary
parameters:
  - name: enable-guardduty
    value: true
```

### Creating the Module Code

Create the module code for each module:

```bash
mkdir -p modules/core/{networking,security}
```

For each module, create the required files:

```bash
# Create networking module files
touch modules/core/networking/README.md
touch modules/core/networking/deployspec.yaml
touch modules/core/networking/modulestack.yaml

# Create security module files
touch modules/core/security/README.md
touch modules/core/security/deployspec.yaml
touch modules/core/security/modulestack.yaml
```

Alternatively, you can use the `seedfarmer init module` command to create the module structure:

```bash
seedfarmer init module -g core -m networking
seedfarmer init module -g core -m security
```

## Environment Variables

Create an `.env` file to store environment variables needed for your deployment:

```bash
echo DEV_ACCOUNT=123456789012 >> .env
echo PROD_ACCOUNT=210987654321 >> .env
```

These environment variables can be referenced in your deployment manifests:

```yaml
targetAccountMappings:
  - alias: primary
    accountId:
      valueFrom:
        envVariable: DEV_ACCOUNT
    default: true
```

## Managing Dependencies

Seed-Farmer manages dependencies between modules, ensuring that modules are deployed in the correct order. Modules can reference outputs from other modules, allowing for complex deployment scenarios.

### Defining Dependencies

Dependencies are defined implicitly through parameter references. For example:

```yaml
name: database
path: modules/services/database/
targetAccount: primary
parameters:
  - name: vpc-id
    valueFrom:
      moduleMetadata:
        group: core
        name: networking
        key: VpcId
```

In this example, the `database` module depends on the `networking` module because it references the `VpcId` output from the `networking` module.

### Dependency Resolution

Seed-Farmer resolves dependencies by:

1. Analyzing parameter references to determine dependencies between modules
2. Sorting modules based on their dependencies
3. Deploying modules in the correct order

### Circular Dependencies

Seed-Farmer prevents circular dependencies between modules. If a circular dependency is detected, Seed-Farmer will raise an error.

### Force Dependency Redeploy

When a module changes (is redeployed), downstream modules that are dependent on it may need to consume those changes. The `forceDependencyRedeploy` flag in the deployment manifest tells Seed-Farmer to force a redeploy of all modules impacted by the redeploy of another module.

```yaml
name: dev
toolchainRegion: us-west-2
forceDependencyRedeploy: True
groups:
  - name: core
    path: manifests/dev/modules/core.yaml
  - name: services
    path: manifests/dev/modules/services.yaml
```

!!! warning
    This is an indiscriminate feature that is not granular enough to detect what is causing a redeploy, only that one needs to occur. Any change to a module will trigger a redeploy of that module and all downstream modules that depend on it, even if the underlying logic or artifact has not changed.

## Multi-Environment Development

Seed-Farmer supports multi-environment development through separate deployment manifests for each environment. This allows you to have different configurations for different environments while reusing the same module code.

### Environment-Specific Manifests

Create separate deployment manifests for each environment:

```
manifests/
├── dev/
│   ├── deployment.yaml
│   └── modules/
│       ├── core.yaml
│       └── services.yaml
└── prod/
    ├── deployment.yaml
    └── modules/
        ├── core.yaml
        └── services.yaml
```

### Environment-Specific Parameters

Use environment-specific parameters in your module manifests:

```yaml
# manifests/dev/modules/core.yaml
name: networking
path: modules/core/networking/
targetAccount: primary
parameters:
  - name: internet-accessible
    value: true
  - name: vpc-cidr
    value: 10.0.0.0/16

# manifests/prod/modules/core.yaml
name: networking
path: modules/core/networking/
targetAccount: primary
parameters:
  - name: internet-accessible
    value: false
  - name: vpc-cidr
    value: 172.16.0.0/16
```

### Environment-Specific Account Mappings

Use environment-specific account mappings in your deployment manifests:

```yaml
# manifests/dev/deployment.yaml
targetAccountMappings:
  - alias: primary
    accountId:
      valueFrom:
        envVariable: DEV_ACCOUNT
    default: true

# manifests/prod/deployment.yaml
targetAccountMappings:
  - alias: primary
    accountId:
      valueFrom:
        envVariable: PROD_ACCOUNT
    default: true
```

## Working with Remote Modules

You can reference modules from remote repositories:

```yaml
name: networking
path: git::https://github.com/awslabs/idf-modules.git//modules/network/basic-cdk?ref=release/1.0.0&depth=1
targetAccount: primary
parameters:
  - name: internet-accessible
    value: true
```

This allows you to use modules from other repositories without having to clone them locally.

### Git Repository References

You can reference a module from a Git repository using the Terraform semantic:

```yaml
path: git::https://github.com/awslabs/idf-modules.git//modules/network/basic-cdk?ref=release/1.0.0&depth=1
```

### Archive References

You can reference a module from an archive over HTTPS:

```yaml
path: archive::https://github.com/awslabs/idf-modules/archive/refs/tags/v1.6.0.tar.gz?module=modules/network/basic-cdk
```

## Working with Data Files

You can include data files in your module deployment using the `dataFiles` field in the module manifest:

```yaml
name: networking
path: modules/core/networking/
targetAccount: primary
dataFiles:
  - filePath: data/test.txt
  - filePath: config/config.json
```

These files will be included in the module bundle and available to the module during deployment.

!!! warning
    If you deploy with data files sourced from a local filesystem, you MUST provide those same files in order to update the module(s) at a later time. Seed-Farmer persists the bundled code with data files, but for destroy ONLY.

## Best Practices

### Project Organization

- **Use a consistent directory structure**: Follow the recommended project structure to make it easier to navigate and understand your project.
- **Separate manifests by environment**: Create separate deployment manifests for each environment to manage environment-specific configurations.
- **Group related modules**: Group related modules together to make it easier to understand the relationships between them.

### Module Development

- **Use least-privilege permissions**: Define the minimum permissions required for your modules in the `modulestack.yaml` file.
- **Document your modules**: Provide a comprehensive README.md that describes the module, its inputs, and its outputs.
- **Use generic environment variables**: If your module is intended to be reused across different projects, set `publishGenericEnvVariables: true` in the deployspec.
- **Provide sample outputs**: Include sample outputs in your README.md to help users understand what to expect.
- **Use consistent naming conventions**: Use consistent naming conventions for parameters and outputs to make it easier for users to understand your module.
- **Handle errors gracefully**: Include error handling in your deployspec commands to ensure that failures are reported clearly.
- **Test your modules**: Test your modules in isolation before integrating them into a larger deployment.
- **Use the metadata CLI helper commands**: Use the metadata CLI helper commands to manage and manipulate metadata in your module deployments.
- **Optimize for reusability**: Design your modules to be reusable across different deployments and projects.

### Dependency Management

- **Be aware of dependencies**: Be aware of and manage the relationships between your modules to assess the impact of changes via redeployment.
- **Avoid circular dependencies**: Design your modules to avoid circular dependencies.
- **Use the forceDependencyRedeploy flag judiciously**: The `forceDependencyRedeploy` flag can cause unnecessary redeployments, so use it only when needed.

### Security

- **Use environment variables for sensitive information**: Store account IDs and other sensitive information in environment variables rather than hardcoding them in manifests.
- **Apply permissions boundaries**: Apply permissions boundaries to the toolchain and deployment roles to further restrict their permissions.
- **Use IAM path prefixes**: Use IAM path prefixes for the toolchain role, target account deployment roles, and policies to create logical separation.

### Deployment

- **Test changes incrementally**: Make small changes and test them incrementally rather than making many changes at once.
- **Use version control**: Use version control to track changes to your modules and manifests.
- **Document your deployments**: Document your deployments, including the modules deployed, their configurations, and any dependencies.

## Conclusion

By following the best practices and tips in this guide, you can develop Seed-Farmer projects that are well-organized, maintainable, and secure. The modular architecture of Seed-Farmer allows you to create reusable components that can be composed into complex deployments, while the dependency management system ensures that modules are deployed in the correct order.
