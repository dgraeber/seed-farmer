# Bundle Management Workflow

This sequence diagram shows how Seed-Farmer manages module bundles for optimization and caching.

```mermaid
sequenceDiagram
    participant Deploy as Module Deploy
    participant BundleSupport as Bundle Support
    participant Checksum as Checksum Calculator
    participant S3 as S3 Bucket
    participant SSM as SSM Parameter Store
    participant CodeBuild as CodeBuild

    Deploy->>Checksum: calculate_module_md5()
    Checksum->>Checksum: hash deployspec content
    Checksum->>Checksum: hash module source files
    Checksum->>Checksum: hash parameter values
    Checksum-->>Deploy: module_md5_hash

    Deploy->>BundleSupport: check_bundle_exists_in_sf()
    BundleSupport->>S3: check bundle path
    Note over S3: s3://{bucket}/{deployment}/{group}/{module}/bundle.zip
    
    alt Bundle exists in S3
        S3-->>BundleSupport: bundle found
        BundleSupport->>SSM: get_stored_md5()
        Note over SSM: /sf/{project}/{deployment}/{group}-{module}/md5
        SSM-->>BundleSupport: stored_md5
        
        alt MD5 matches current
            BundleSupport-->>Deploy: use existing bundle
            Deploy->>S3: download bundle
            Deploy->>Deploy: extract and deploy
        else MD5 mismatch
            BundleSupport-->>Deploy: bundle outdated
            Deploy->>Deploy: trigger_new_build()
        end
        
    else No bundle exists
        BundleSupport-->>Deploy: no bundle found
        Deploy->>Deploy: trigger_new_build()
    end
    
    alt New build required
        Deploy->>CodeBuild: start_build()
        CodeBuild->>CodeBuild: execute deployspec
        CodeBuild->>CodeBuild: create deployment artifacts
        
        CodeBuild->>BundleSupport: create_bundle()
        BundleSupport->>BundleSupport: zip artifacts
        BundleSupport->>S3: upload bundle
        
        CodeBuild->>SSM: store_module_metadata()
        Note over SSM: Store MD5, deployment info, timestamps
        SSM->>SSM: put_parameter(/sf/{project}/{deployment}/{group}-{module}/md5)
        SSM->>SSM: put_parameter(/sf/{project}/{deployment}/{group}-{module}/metadata)
        
        CodeBuild->>Deploy: deploy artifacts to AWS
        Deploy-->>Deploy: deployment complete
    end
```

## Bundle Lifecycle

1. **MD5 Calculation**: Hash of deployspec + source + parameters
2. **Bundle Check**: Verify if bundle exists and is current
3. **Cache Hit**: Use existing bundle if MD5 matches
4. **Cache Miss**: Build new bundle and update metadata
5. **Storage**: Upload bundle to S3 and metadata to SSM
