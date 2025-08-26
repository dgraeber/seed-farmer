# Dependency Resolution Workflow

This sequence diagram shows how Seed-Farmer resolves and orders module dependencies for deployment.

```mermaid
sequenceDiagram
    participant DeployCmd as Deployment Commands
    participant DepUtils as Deploy Utils
    participant Manifest as Deployment Manifest
    participant ModuleGraph as Module Graph
    participant Validator as Dependency Validator

    DeployCmd->>DepUtils: resolve_dependencies(manifest)
    DepUtils->>Manifest: get all module groups
    Manifest-->>DepUtils: groups list
    
    loop For each group
        DepUtils->>Manifest: get modules in group
        Manifest-->>DepUtils: modules list
        
        loop For each module
            DepUtils->>DepUtils: extract module dependencies            
            DepUtils->>ModuleGraph: add_module(module)
            DepUtils->>ModuleGraph: add_dependencies(module, deps)
        end
    end
    
    DepUtils->>Validator: validate_dependencies(graph)
    Validator->>Validator: check for circular dependencies
    
    alt Circular dependency found
        Validator-->>DepUtils: CircularDependencyError
        DepUtils-->>DeployCmd: Error: Circular dependency
    else No circular dependencies
        Validator-->>DepUtils: validation passed
        
        DepUtils->>ModuleGraph: topological_sort()
        ModuleGraph->>ModuleGraph: Kahn's algorithm
        ModuleGraph-->>DepUtils: ordered module list
        
        DepUtils->>DepUtils: group_modules_by_level()
        Note over DepUtils: Group modules that can<br/>be deployed in parallel
        
        DepUtils-->>DeployCmd: deployment order
    end
```

## Dependency Types

### Explicit Dependencies
- `dependsOn` field in module manifest
- Direct module-to-module relationships

### Implicit Dependencies  
- Parameter references (`${module.output}`)
- Data file references from other modules
- Cross-module resource dependencies

### Deployment Levels
```
Level 0: [ModuleA, ModuleB]     # No dependencies - parallel
Level 1: [ModuleC]              # Depends on A,B - sequential  
Level 2: [ModuleD, ModuleE]     # Depends on C - parallel
```

## Error Handling
- **Circular Dependencies**: Detected and reported before deployment
- **Missing Dependencies**: Validated during graph construction
- **Invalid References**: Caught during parameter resolution
