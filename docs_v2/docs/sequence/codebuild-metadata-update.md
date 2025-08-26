# CodeBuild Metadata Update Workflow

This sequence diagram shows how CodeBuild processes update SSM metadata during remote deployments.

```mermaid
sequenceDiagram
    participant RemoteDeploy as Remote Deploy
    participant CodeBuildRemote as CodeBuild Remote
    participant CodeBuildProj as CodeBuild Project
    participant Container as Build Container
    parameter SSM as SSM Parameter Store
    participant CloudFormation as CloudFormation
    participant S3 as S3 Bucket

    RemoteDeploy->>CodeBuildRemote: start_build()
    CodeBuildRemote->>CodeBuildProj: create_project()
    CodeBuildRemote->>CodeBuildProj: start_build()
    
    Note over CodeBuildProj,Container: CodeBuild Container Execution
    
    CodeBuildProj->>Container: initialize build environment
    Container->>Container: set SEEDFARMER_* env vars
    Container->>Container: install dependencies
    
    Note over Container: Pre-Build Phase
    Container->>Container: calculate current MD5
    Container->>SSM: get existing metadata
    Container->>Container: compare MD5 hashes
    
    alt MD5 unchanged and force_update=false
        Container->>Container: skip build (optimization)
        Container->>SSM: update timestamp only
    else MD5 changed or force_update=true
        Note over Container: Build Phase
        Container->>Container: execute build commands
        Container->>Container: compile/package artifacts
        
        Note over Container: Deploy Phase  
        Container->>CloudFormation: deploy stack
        CloudFormation->>CloudFormation: create/update resources
        CloudFormation-->>Container: stack outputs
        
        Note over Container: Post-Deploy Metadata Update
        Container->>Container: extract stack outputs
        Container->>Container: prepare metadata payload
        
        Container->>SSM: put_parameter(md5)
        Note over SSM: /sf/{project}/{deployment}/{group}-{module}/md5
        
        Container->>SSM: put_parameter(metadata)
        Note over SSM: Store complete module metadata
        
        Container->>SSM: put_parameter(outputs)
        Note over SSM: Store CloudFormation outputs
        
        alt Bundle creation enabled
            Container->>Container: create deployment bundle
            Container->>S3: upload bundle.zip
            Note over S3: s3://{bucket}/{deployment}/{group}/{module}/
        end
    end
    
    Container->>Container: generate build report
    Container-->>CodeBuildProj: build complete
    
    CodeBuildProj->>CodeBuildRemote: build_status()
    CodeBuildRemote->>RemoteDeploy: poll build status
    
    loop Monitor build progress
        RemoteDeploy->>CodeBuildRemote: get_build_status()
        CodeBuildRemote->>CodeBuildProj: describe_build()
        CodeBuildProj-->>CodeBuildRemote: build_info
        CodeBuildRemote-->>RemoteDeploy: status update
    end
    
    CodeBuildRemote-->>RemoteDeploy: deployment complete
```

## Environment Variables in CodeBuild

### SeedFarmer Variables
```bash
SEEDFARMER_PROJECT_NAME=my-project
SEEDFARMER_DEPLOYMENT_NAME=prod
SEEDFARMER_MODULE_NAME=networking-vpc
SEEDFARMER_PARAMETER_VPC_CIDR=10.0.0.0/16
SEEDFARMER_HASH=abc123...
```

### AWS Variables
```bash
AWS_PARTITION=aws
AWS_DEFAULT_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012
```

## Metadata Update Timing

1. **Pre-Build**: Check existing MD5 for optimization
2. **Post-Deploy**: Update metadata after successful deployment
3. **On Failure**: Mark deployment as failed in metadata
4. **Bundle Upload**: Store artifacts for future optimization

## SSM Parameter Patterns

- **MD5**: `/sf/{project}/{deployment}/{group}-{module}/md5`
- **Metadata**: `/sf/{project}/{deployment}/{group}-{module}/metadata`  
- **Outputs**: `/sf/{project}/{deployment}/{group}-{module}/outputs`
- **Status**: `/sf/{project}/{deployment}/{group}-{module}/status`
