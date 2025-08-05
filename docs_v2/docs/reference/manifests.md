# Manifests

Seed-Farmer uses manifests to define deployments and modules. This page explains the format and structure of these manifests.

## Deployment Manifest

The deployment manifest is the top-level manifest that defines the deployment, including groups of modules and target account mappings.

### Structure

```yaml
name: examples
nameGenerator:
  prefix: myprefix
  suffix:
    valueFrom:
        envVariable: SUFFIX_ENV_VARIABLE
toolchainRegion: us-west-2
forceDependencyRedeploy: False
archiveSecret: example-archive-credentials-modules
groups:
  - name: optionals
    path: manifests-multi/examples/optional-modules.yaml
    concurrency: 2
  - name: optionals-2
    path: manifests-multi/examples/optional-modules-2.yaml
targetAccountMappings:
  - alias: primary
    accountId:
      valueFrom:
        envVariable: PRIMARY_ACCOUNT
    default: true
    codebuildImage: XXXXXXXXXXXX.dkr.ecr.us-east-1.amazonaws.com/aws-codeseeder/code-build-base:5.5.0
    runtimeOverrides:
      python: "3.13"
    npmMirror: https://registry.npmjs.org/
    npmMirrorSecret: /something/aws-addf-mirror-credentials
    pypiMirror: https://pypi.python.org/simple
    pypiMirrorSecret: /something/aws-addf-mirror-mirror-credentials
    rolePrefix: /
    policyPrefix: /
    parametersGlobal:
      dockerCredentialsSecret: nameofsecret
      permissionsBoundaryName: policyname
    regionMappings:
      - region: us-east-2
        default: true
        codebuildImage: XXXXXXXXXXXX.dkr.ecr.us-east-1.amazonaws.com/aws-codeseeder/code-build-base:4.4.0
        runtimeOverrides:
          python: "3.13"
        npmMirror: https://registry.npmjs.org/
        npmMirrorSecret: /something/aws-addf-mirror-credentials
        pypiMirror: https://pypi.python.org/simple
        pypiMirrorSecret: /something/aws-addf-mirror-credentials
        parametersRegional:
          dockerCredentialsSecret: nameofsecret
          permissionsBoundaryName: policyname
          vpcId: vpc-XXXXXXXXX
          publicSubnetIds:
            - subnet-XXXXXXXXX
            - subnet-XXXXXXXXX
          privateSubnetIds:
            - subnet-XXXXXXXXX
            - subnet-XXXXXXXXX
          isolatedSubnetIds:
            - subnet-XXXXXXXXX
            - subnet-XXXXXXXXX
          securityGroupsId:
            - sg-XXXXXXXXX
        network: 
          vpcId:
            valueFrom:
              parameterValue: vpcId
          privateSubnetIds:
            valueFrom:
              parameterValue: privateSubnetIds
          securityGroupIds:
            valueFrom:
              parameterValue: securityGroupIds
  - alias: secondary
    accountId: 123456789012
    regionMappings:
      - region: us-west-2
        parametersRegional:
          dockerCredentialsSecret: nameofsecret
          permissionsBoundaryName: policyname
      - region: us-east-2
        default: true
```

### Fields

#### Top-Level Fields

- **name**: The name of your deployment. There can be only one deployment with this name in a project. Cannot be used with `nameGenerator`.
- **nameGenerator**: Supports dynamically generating a deployment name by concatenation of prefix and suffix. Cannot be used with `name`.
  - **prefix**: The prefix string of the name
  - **suffix**: The suffix string of the name
- **toolchainRegion**: The designated region that the toolchain is created in
- **forceDependencyRedeploy**: A boolean that tells Seed-Farmer to redeploy ALL dependency modules. Default is `False`.
- **archiveSecret**: Name of a secret in SecretsManager that contains the credentials to access a private HTTPS archive for the modules.
- **groups**: The relative path to the module manifests that define each module in the group. This sequential order is preserved in deployment, and reversed in destroy.
  - **name**: The name of the group
  - **path**: The relative path to the module manifest
  - **concurrency**: Limit the number of concurrent CodeBuild jobs that run. Default is the number of modules in the group.

#### Target Account Mappings

- **alias**: The logical name for an account, referenced by module manifests
- **accountId**: The account ID tied to the alias. This parameter also supports environment variables.
- **default**: Designates this mapping as the default account for all modules unless otherwise specified.
- **codebuildImage**: A custom build image to use
- **runtimeOverrides**: Runtime versions for the CodeBuild environment
- **npmMirror**: The NPM registry mirror to use
- **npmMirrorSecret**: The AWS SecretManager to use when setting the mirror
- **pypiMirror**: The Pypi mirror to use
- **pypiMirrorSecret**: The AWS SecretManager to use when setting the mirror
- **rolePrefix**: IAM path prefix to use with Seed-Farmer roles
- **policyPrefix**: IAM path prefix to use with Seed-Farmer policies
- **parametersGlobal**: Parameters that apply to all region mappings unless otherwise overridden at the region level
  - **dockerCredentialsSecret**: Secret containing Docker credentials
  - **permissionsBoundaryName**: The name of the permissions boundary policy to apply to all module-specific roles created
- **regionMappings**: Section to define region-specific configurations for the defined account
  - **region**: The region name
  - **default**: Designates this mapping as the default region for all modules unless otherwise specified.
  - **codebuildImage**: A custom build image to use
  - **runtimeOverrides**: Runtime versions for the CodeBuild environment
  - **npmMirror**: The NPM registry mirror to use
  - **npmMirrorSecret**: The AWS SecretManager to use when setting the mirror
  - **pypiMirror**: The Pypi mirror to use
  - **pypiMirrorSecret**: The AWS SecretManager to use when setting the mirror
  - **rolePrefix**: IAM path prefix to use with Seed-Farmer roles
  - **policyPrefix**: IAM path prefix to use with Seed-Farmer policies
  - **parametersRegional**: Parameters that apply to all region mappings unless otherwise overridden at the region level
    - **dockerCredentialsSecret**: Secret containing Docker credentials
    - **permissionsBoundaryName**: The name of the permissions boundary policy to apply to all module-specific roles created
    - Any other parameter in this list is NOT a named parameter and is solely for the use of lookup in module manifests or the network object
  - **network**: This section indicates to Seed-Farmer and AWS CodeSeeder that the CodeBuild Project should be run in a VPC on Private Subnets.
    - **vpcId**: The VPC ID the CodeBuild Project should be associated to
    - **privateSubnetIds**: The private subnets the CodeBuild Project should be associated to
    - **securityGroupIds**: The Security Groups the CodeBuild Project should be associated to (limit of 5)

### Network Configuration for Regions

The network configuration for regions can be defined using:

- Hardcoded values
- Regional parameters
- AWS SSM parameters
- Environment variables

#### Hardcoded Value Support for Network

```yaml
network: 
  vpcId: vpc-XXXXXXXXX    
  privateSubnetIds:
    - subnet-XXXXXXXXX
    - subnet-XXXXXXXXX
  securityGroupsIds:
    - sg-XXXXXXXXX
```

#### Regional Parameters Support for Network

```yaml
network: 
  vpcId:
    valueFrom:
      parameterValue: vpcId
  privateSubnetIds:
    valueFrom:
      parameterValue: privateSubnetIds
  securityGroupIds:
    valueFrom:
      parameterValue: securityGroupIds
```

#### AWS SSM Parameters Support for Network

```yaml
network: 
  vpcId: 
    valueFrom:
      parameterStore: /idf/testing/vpcid
  privateSubnetIds:
    valueFrom:
      parameterStore: /idf/testing/privatesubnets
  securityGroupIds:
    valueFrom:
      parameterStore: /idf/testing/securitygroups
```

#### Environment Variable Support for Network

```yaml
network: 
  vpcId: 
    valueFrom:
      envVariable: VPCID
  privateSubnetIds:
    valueFrom:
      envVariable: PRIVATESUBNETS
  securityGroupIds:
    valueFrom:
      envVariable: SECURITYGROUPS
```

### Dependency Management

Seed-Farmer has a shared-responsibility model for dependency management of modules. It includes guardrails to:

- Prevent deletion of modules that have downstream modules dependent on them
- Prevent circular references of modules

However, it is up to the end user to be aware of and manage the relationships between modules to assess the impact of changes to modules via redeployment.

#### Force Dependency Redeploy

When a module changes (is redeployed), downstream modules that are dependent on it may need to consume those changes. The `forceDependencyRedeploy` flag in the deployment manifest tells Seed-Farmer to force a redeploy of all modules impacted by the redeploy of another module.

!!! warning
    This is an indiscriminate feature that is not granular enough to detect what is causing a redeploy, only that one needs to occur. Any change to a module will trigger a redeploy of that module and all downstream modules that depend on it, even if the underlying logic or artifact has not changed.

## Module Manifest

The module manifest is referred to by the deployment manifest and defines the information the CLI needs to deploy a module or a group of modules - as defined by the group. Each entry in the module manifest is deployed in parallel and ordering is not preserved.

### Structure

```yaml
name: networking
path: modules/optionals/networking/
targetAccount: primary
parameters:
  - name: internet-accessible
    value: true
---
name: buckets
path: modules/optionals/buckets
targetAccount: secondary
targetRegion: us-west-2
codebuildImage: XXXXXXXXXXXX.dkr.ecr.us-east-1.amazonaws.com/aws-codeseeder/code-build-base:3.3.0
runtimeOverrides:
  python: "3.13"
npmMirror: https://registry.npmjs.org/
npmMirrorSecret: /something/aws-addf-mirror-credentials
pypiMirror: https://pypi.python.org/simple
pypiMirrorSecret: /something/aws-addf-mirror-credentials
parameters:
  - name: encryption-type
    value: SSE
  - name: some-name
    valueFrom:
      moduleMetadata:
        group: optionals
        name: networking
        key: VpcId
dataFiles:
  - filePath: data/test2.txt
  - filePath: test1.txt
  - filePath: git::https://github.com/awslabs/idf-modules.git//modules/storage/buckets/deployspec.yaml?ref=release/1.0.0&depth=1
  - filePath: archive::https://github.com/awslabs/idf-modules/archive/refs/tags/v1.6.0.tar.gz?module=modules/storage/buckets/deployspec.yaml
```

### Fields

- **name**: The name of the module. This name must be unique in the group of the deployment.
- **path**: The relative path to the module code in the project, or a Git repository URL, or a release archive URL.
- **targetAccount**: The alias of the account from the deployment manifest mappings.
- **targetRegion**: The name of the region to deploy to - this overrides any mappings.
- **codebuildImage**: A custom build image to use.
- **runtimeOverrides**: Runtime versions for the CodeBuild environment.
- **npmMirror**: The NPM registry mirror to use.
- **npmMirrorSecret**: The AWS SecretManager to use when setting the mirror.
- **pypiMirror**: The Pypi mirror to use.
- **pypiMirrorSecret**: The AWS SecretManager to use when setting the mirror.
- **parameters**: The parameters to pass to the module.
- **dataFiles**: Additional files to add to the bundle that are outside of the module code.

### Git Repository References

You can reference a module from a Git repository using the Terraform semantic:

```yaml
name: networking
path: git::https://github.com/awslabs/idf-modules.git//modules/network/basic-cdk?ref=release/1.0.0&depth=1
targetAccount: secondary
parameters:
  - name: internet-accessible
    value: true
```

### Archive References

You can reference a module from an archive over HTTPS:

```yaml
name: networking
path: archive::https://github.com/awslabs/idf-modules/archive/refs/tags/v1.6.0.tar.gz?module=modules/network/basic-cdk
targetAccount: secondary
parameters:
  - name: internet-accessible
    value: true
```

### Data Files

The `dataFile` support for modules is intended to take files located outside of the module code and package them as if they were a part of the module. This is useful for data files that are shared amongst multiple modules or are dynamic and can change over time.

!!! warning
    If you deploy with data files sourced from a local filesystem, you MUST provide those same files in order to update the module(s) at a later time. Seed-Farmer persists the bundled code with data files, but for destroy ONLY.

## Parameters

Parameters are defined in the module manifests as key/value pairs. On deployment, values are serialized to JSON and passed to the module's CodeBuild execution as environment variables.

### Types of Parameters

#### User-Defined

Simple key/value pairs passed in as strings:

```yaml
parameters:
  - name: glue-db-suffix
    value: vsidata
  - name: rosbag-bagfile-table-suffix
    value: Rosbag-BagFile-Metadata
```

#### Environment Variables

Values from environment variables:

```yaml
parameters:
  - name: vpc-id
    valueFrom:
      envVariable: ENV_VPC_ID
```

#### Module Metadata

Values from other modules:

```yaml
parameters:
  - name: vpc-id
    valueFrom:
      moduleMetadata:
        group: optionals
        name: networking
        key: VpcId
```

#### Global and Regional Parameters

Values from global or regional parameters defined in the deployment manifest:

```yaml
parameters:
  - name: vpc-id
    valueFrom:
      parameterValue: vpcId
```

#### AWS SSM Parameter

Values from AWS SSM Parameter Store:

```yaml
parameters:
  - name: vpc-id
    valueFrom:
      parameterStore: my-vpc-id
```

#### AWS Secrets Manager

Values from AWS Secrets Manager:

```yaml
parameters:
  - name: vpc-id
    valueFrom:
      secretsManager: my-secret-vpc-id
```

### Parameters in AWS CodeSeeder

CodeBuild environment variables that are set via AWS CodeSeeder are made known to the module using a naming convention based off the parameter's key. Parameter keys are converted from "PascalCase", "camelCase", or "kebab-case" to all upper "SNAKE_CASE" and prefixed with "<<project>>_PARAMETER_".

For example, if the name of your project is "MY_APP":

```
* someKey will become environment variable MYAPP_PARAMETER_SOME_KEY
* SomeKey will become environment variable MYAPP_PARAMETER_SOME_KEY
* some-key will become environment variable MYAPP_PARAMETER_SOME_KEY
* some_key will become environment variable MYAPP_PARAMETER_SOME_KEY
* somekey will become environment variable MYAPP_PARAMETER_SOMEKEY
```

## Universal Environment Variable Replacement in Manifests

As of Seed-Farmer version 3.5.0, there is support for dynamic replacement of values with environment variables in manifests. Any string within your manifests that has a designated pattern will automatically be resolved. If you have an environment variable named `SOMEKEY` that is defined, you can reference it in your manifests via wrapping it in `${}` --> for example `${SOMEKEY}`.

Additionally, it is possible to disable environment variable replacement in module input parameters using `disableEnvVarResolution: True` for cases such as when input parameter is a script.

Example:

```yaml
name: dummy
path: git::https://github.com/awslabs/idf-modules.git//modules/dummy/blank?ref=release/1.2.0
targetAccount: primary
targetRegion: us-east-1
parameters:
  - name: test
    value: hiyooo
  - name: myparamkey
    valueFrom:
      parameterStore: /idf/${SOMEKEY}/somekey
  - name: test2
    value: ${SOMEKEY}
  - name: param-no-env-resolution
    disableEnvVarResolution: True
    value:
      - |
        export VAR=test
        echo "${VAR}"
```

!!! warning
    We do not recommend using this in the `name` field of manifests as any value that is referenced by downstream manifests MUST align.
