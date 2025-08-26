# Sequence Diagrams


## Local vs Remote Deployment Flow

This diagram shows the detailed execution flow for both local and remote deployment strategies.

```mermaid
sequenceDiagram
    participant User as User
    participant CLI as CLI Apply
    participant DeployCmd as DeploymentCommands
    participant Factory as DeployModuleFactory
    participant Local as DeployLocalModule
    participant Remote as DeployRemoteModule
    participant CBLocal as CodeBuildLocal
    participant CBRemote as CodeBuildRemote
    participant AWS as AWS Services

    User->>CLI: seedfarmer apply manifest.yaml
    CLI->>DeployCmd: apply()
    
    DeployCmd->>DeployCmd: process_deployment_manifest()
    DeployCmd->>DeployCmd: resolve dependencies
    
    loop For each module
        DeployCmd->>Factory: create(ModuleDeployObject)
        
        alt Local Deployment (--local flag)
            Factory-->>DeployCmd: DeployLocalModule
            DeployCmd->>Local: deploy_module()
            
            Local->>Local: _env_vars() - set environment
            Local->>Local: _prebuilt_bundle_check()
            
            alt Prebuilt bundle exists
                Local->>AWS: download bundle from S3
                Local->>Local: extract and use bundle
            else No prebuilt bundle
                Local->>CBLocal: execute_deployspec()
                CBLocal->>CBLocal: run build phase commands
                CBLocal->>CBLocal: run deploy phase commands
                CBLocal->>AWS: deploy CloudFormation/CDK
                CBLocal-->>Local: execution result
            end
            
            Local-->>DeployCmd: ModuleDeploymentResponse
            
        else Remote Deployment (default)
            Factory-->>DeployCmd: DeployRemoteModule
            DeployCmd->>Remote: deploy_module()
            
            Remote->>Remote: _env_vars() - set environment
            Remote->>Remote: _prebuilt_bundle_check()
            
            alt Prebuilt bundle exists
                Remote->>AWS: use existing bundle
            else No prebuilt bundle
                Remote->>CBRemote: create_codebuild_project()
                Remote->>AWS: create CodeBuild project
                Remote->>CBRemote: start_build()
                CBRemote->>AWS: start CodeBuild execution
                
                loop Monitor build
                    Remote->>AWS: get build status
                    AWS-->>Remote: build progress
                end
                
                CBRemote-->>Remote: build completion
            end
            
            Remote-->>DeployCmd: ModuleDeploymentResponse
        end
    end
    
    DeployCmd-->>CLI: deployment complete
    CLI-->>User: success/failure status
```

### Key Differences

#### Local Deployment
- Executes deployspec commands directly on local machine
- Uses local AWS credentials/session
- Faster for development and testing
- Limited by local environment capabilities

#### Remote Deployment  
- Creates isolated CodeBuild projects
- Uses SeedFarmer toolchain roles
- Better for production deployments
- Provides build isolation and consistent environment
- Supports complex build requirements and custom images
