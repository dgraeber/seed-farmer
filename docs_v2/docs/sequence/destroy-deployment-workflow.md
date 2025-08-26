# Destroy Deployment Workflow

This sequence diagram shows the process when running `seedfarmer destroy deployment-name`.

```mermaid
sequenceDiagram
    participant User as User
    participant CLI as CLI Main
    participant DestroyCmd as Destroy Command
    participant DeployCmd as Deployment Commands
    participant MetadataMgr as Metadata Manager
    participant DepResolver as Dependency Resolver
    participant ModuleDestroy as Module Destroyer
    participant AWS as AWS Services

    User->>CLI: seedfarmer destroy my-deployment --profile prod
    CLI->>CLI: load_dotenv_files()
    CLI->>DestroyCmd: destroy(deployment_name, ...)
    
    DestroyCmd->>DeployCmd: destroy()
    DeployCmd->>MetadataMgr: get_deployed_deployment_manifest()
    MetadataMgr->>AWS: retrieve stored manifest from S3/SSM
    AWS-->>MetadataMgr: deployment manifest
    MetadataMgr-->>DeployCmd: DeploymentManifest
    
    alt No deployed manifest found
        DeployCmd-->>DestroyCmd: Nothing to destroy
        DestroyCmd-->>CLI: No deployment found
        CLI-->>User: Deployment not found
    else Manifest found
        DeployCmd->>DepResolver: resolve_dependencies()
        DepResolver->>DepResolver: build dependency graph
        DepResolver->>DepResolver: reverse topological sort
        DepResolver-->>DeployCmd: reverse ordered module list
        
        DeployCmd->>DeployCmd: load_parameter_values()
        
        loop For each module group (reverse order)
            DeployCmd->>ModuleDestroy: destroy_modules_in_group()
            
            loop For each module in group (reverse order)
                ModuleDestroy->>ModuleDestroy: create ModuleDeployObject
                ModuleDestroy->>ModuleDestroy: DeployModuleFactory.create()
                ModuleDestroy->>ModuleDestroy: destroy_module()
                ModuleDestroy->>AWS: delete CloudFormation stacks
                ModuleDestroy->>AWS: cleanup resources
                AWS-->>ModuleDestroy: destruction result
            end
            
            ModuleDestroy-->>DeployCmd: group destruction status
        end
        
        DeployCmd->>MetadataMgr: remove_deployed_deployment_manifest()
        MetadataMgr->>AWS: delete stored manifest
        
        alt remove_seedkit flag set
            DeployCmd->>AWS: delete SeedKit CloudFormation stack
            Note over DeployCmd,AWS: WARNING: Removes SeedKit for ALL deployments
        end
        
        DeployCmd-->>DestroyCmd: destruction complete
    end
    
    DestroyCmd-->>CLI: success/failure
    CLI-->>User: destruction status
```

## Key Differences from Apply

1. **Reverse Order**: Modules destroyed in reverse dependency order
2. **Stored Manifest**: Uses previously deployed manifest, not source manifest
3. **Resource Cleanup**: Explicitly deletes CloudFormation stacks and resources
4. **Metadata Cleanup**: Removes deployment tracking metadata
5. **Optional SeedKit Removal**: Can remove shared SeedKit infrastructure
