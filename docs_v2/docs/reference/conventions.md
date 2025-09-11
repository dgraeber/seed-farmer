# Standard Formats and Configurations


## Global Overrides
Seed-Farmer traditionally uses the [Environment Parameter](manifests.md)  as a means to get environment parameter at runtime to be declarative about the field requested:


A more recent feature was the use of Global Value Replace for manifests.  Any value in a manifest, when surrounded by `${}` can be replaced with the value of the referred to environment parameter if it exists.

```yaml
name: example
toolchainRegion: ${PREFERRED}
forceDependencyRedeploy: false
targetAccountMappings:
  - alias: production
    accountId: ${MYACCOUNTID}
```
In the above example, the `MYACCOUNTID` and `PREFERRED` will be replaced with the value of the environment parameter if it exist.

!!! warning "Not for Keys"
    This only works for values in the manifests, not keys.  
    
    If the environment parameter is not defined, the processing will error and stop.


## Archive Secrets
Coming Soon

## Mirror Secrets
Coming Soon
