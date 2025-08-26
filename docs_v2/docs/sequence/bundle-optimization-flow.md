# Bundle Optimization Flow

This diagram shows how Seed-Farmer optimizes deployments using prebuilt bundles stored in S3.

```mermaid
sequenceDiagram
    participant Deploy as DeployModule
    participant BundleSupport as BundleSupport
    participant S3 as S3 Bucket
    participant SessionMgr as SessionManager
    participant Executor as Build Executor

    Deploy->>Deploy: _prebuilt_bundle_check()
    
    alt SeedFarmer bucket configured
        Deploy->>SessionMgr: get_deployment_session()
        SessionMgr-->>Deploy: AWS session
        
        Deploy->>BundleSupport: check_bundle_exists_in_sf()
        BundleSupport->>S3: check bundle path exists
        Note over BundleSupport,S3: Path: {deployment}/{group}/{module}/bundle.zip
        
        alt Bundle exists in S3
            S3-->>BundleSupport: bundle found
            BundleSupport-->>Deploy: bundle path
            Deploy->>Deploy: use_prebuilt_bundle()
            Deploy->>S3: download bundle
            S3-->>Deploy: bundle content
            Deploy->>Deploy: extract and deploy
            Deploy-->>Deploy: deployment complete (fast path)
            
        else Bundle not found
            BundleSupport-->>Deploy: None
            Deploy->>Executor: execute_full_build()
            Executor->>Executor: run build commands
            Executor->>Executor: create deployment artifacts
            Executor->>S3: upload new bundle (optional)
            Executor->>Executor: deploy artifacts
            Executor-->>Deploy: deployment complete (full build)
        end
        
    else No SeedFarmer bucket
        Deploy->>Executor: execute_full_build()
        Executor->>Executor: run build commands
        Executor->>Executor: deploy artifacts
        Executor-->>Deploy: deployment complete (full build)
    end
```

## Bundle Strategy Benefits

1. **Performance**: Avoids rebuilding unchanged modules
2. **Consistency**: Ensures same artifacts across environments  
3. **Efficiency**: Reduces CodeBuild usage and costs
4. **Reliability**: Pre-validated bundles reduce deployment failures

## Bundle Path Structure
```
s3://{seedfarmer-bucket}/{deployment}/{group}/{module}/bundle.zip
```

The bundle contains:
- Built artifacts (compiled code, dependencies)
- CloudFormation/CDK templates
- Deployment metadata
- Module-specific assets
