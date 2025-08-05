# Guides

This section provides how-to guides for common tasks with Seed-Farmer. These guides are designed to help you accomplish specific goals and solve common problems.

## Local Deployments

The [Local Deployments](local-deployments.md) guide explains how to deploy Seed-Farmer projects locally for development and testing purposes. This is useful for testing changes before deploying to production environments.

## Project Development

The [Project Development](project-development.md) guide provides best practices and tips for developing projects with Seed-Farmer. This includes organizing your code, managing dependencies, and structuring your manifests.

## Common Tasks

### Creating a New Module

To create a new module, you can use the `seedfarmer init module` command:

```bash
seedfarmer init module -g mygroup -m mymodule
```

This will create a new module in the `modules/mygroup/mymodule` directory with the necessary files.

### Deploying a Project

To deploy a project, you can use the `seedfarmer apply` command:

```bash
seedfarmer apply manifests/mydeployment/deployment.yaml --env-file .env
```

This will deploy the modules defined in the deployment manifest.

### Destroying a Deployment

To destroy a deployment, you can use the `seedfarmer destroy` command:

```bash
seedfarmer destroy mydeployment --env-file .env
```

This will destroy all the modules in the deployment in the reverse order of their deployment.

## Advanced Topics

### Working with Multiple Accounts

Seed-Farmer supports deploying across multiple AWS accounts. The [Multi-Account Support](../concepts/multi-account.md) page explains how to configure and use this feature.

### Custom Module Development

For information on developing custom modules, see the [Module Development](../reference/module-development.md) reference.

### Troubleshooting

If you encounter issues with Seed-Farmer, check the [FAQ](../reference/faq.md) for common problems and solutions.
