# Parameter Resolution Workflow

This sequence diagram shows how Seed-Farmer resolves parameters from various sources during deployment.

```mermaid
sequenceDiagram
    participant DeployCmd as Deployment Commands
    participant ParamCmd as Parameter Commands
    participant Manifest as Deployment Manifest
    participant SSM as AWS SSM
    parameter SecretsManager as AWS Secrets Manager
    participant ModuleOutput as Module Outputs
    participant EnvVars as Environment Variables

    DeployCmd->>ParamCmd: load_parameter_values(manifest)
    ParamCmd->>Manifest: get all modules with parameters
    Manifest-->>ParamCmd: modules list
    
    loop For each module
        ParamCmd->>ParamCmd: get module parameters
        
        loop For each parameter
            alt Parameter has valueFrom reference
                ParamCmd->>ParamCmd: parse valueFrom reference
                
                alt SSM Parameter reference
                    ParamCmd->>SSM: get_parameter(name)
                    SSM-->>ParamCmd: parameter value
                    
                else Secrets Manager reference
                    ParamCmd->>SecretsManager: get_secret_value(name)
                    SecretsManager-->>ParamCmd: secret value
                    
                else Module output reference
                    ParamCmd->>ModuleOutput: get_module_output(module, key)
                    ModuleOutput-->>ParamCmd: output value
                    
                else Environment variable reference
                    ParamCmd->>EnvVars: get_env_var(name)
                    EnvVars-->>ParamCmd: env value
                end
                
            else Direct parameter value
                ParamCmd->>ParamCmd: use literal value
            end
            
            ParamCmd->>ParamCmd: store resolved parameter
        end
    end
    
    ParamCmd->>ParamCmd: validate_all_parameters_resolved()
    
    alt Missing required parameters
        ParamCmd-->>DeployCmd: ParameterResolutionError
    else All parameters resolved
        ParamCmd->>ParamCmd: resolve_params_for_checksum()
        ParamCmd-->>DeployCmd: resolved parameters
    end
```

## Parameter Sources

### 1. Direct Values
```yaml
parameters:
  - name: vpc_cidr
    value: "10.0.0.0/16"
```

### 2. SSM Parameter Store
```yaml
parameters:
  - name: database_password
    valueFrom:
      parameterStore: /myapp/prod/db/password
```

### 3. Secrets Manager
```yaml
parameters:
  - name: api_key
    valueFrom:
      secretsManager: prod/api-keys
      secretsManagerKey: external_api_key
```

### 4. Module Outputs
```yaml
parameters:
  - name: vpc_id
    valueFrom:
      moduleMetadata:
        group: networking
        name: vpc
        key: VpcId
```

### 5. Environment Variables
```yaml
parameters:
  - name: environment
    valueFrom:
      envVariable: DEPLOYMENT_ENV
```

## Resolution Order
1. Environment variables (highest priority)
2. Module outputs (cross-module dependencies)
3. SSM Parameter Store
4. Secrets Manager
5. Direct values (lowest priority)
