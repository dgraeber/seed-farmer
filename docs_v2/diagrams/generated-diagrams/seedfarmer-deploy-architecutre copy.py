from diagrams import Diagram, Cluster, Edge
from diagrams.aws.general import General, User
from diagrams.aws.security import IAMRole, SecretsManager
from diagrams.aws.management import ParameterStore
from diagrams.aws.devtools import Codebuild
from diagrams.aws.storage import S3
from diagrams.aws.security import KeyManagementService as KMS

with Diagram("SeedFarmer Cross Account Deployments", show=False, direction="TB"):
    
    # End User
    user = User("End User")
    
    # Toolchain Account
    with Cluster("Toolchain Account"):
        toolchain_role = IAMRole("SeedFarmer Toolchain Role")
        toolchain_ssm = ParameterStore("SSM Parameters")
        toolchain_secrets = SecretsManager("Secrets Manager")
    
    # Deployment Accounts
    with Cluster("Deployment Accounts"):
        with Cluster("Account B"):
            deploy_role_b = IAMRole("SeedFarmer Deployment Role")
            codebuild_b = Codebuild("CodeBuild Project")
            s3_b = S3("S3 Bucket")
            ssm_b = ParameterStore("SSM Parameters")
            secrets_b = SecretsManager("Secrets Manager")
            kms_b = KMS("KMS")
        
        with Cluster("Account C"):
            deploy_role_c = IAMRole("SeedFarmer Deployment Role")
            codebuild_c = Codebuild("CodeBuild Project")
            s3_c = S3("S3 Bucket")
            ssm_c = ParameterStore("SSM Parameters")
            secrets_c = SecretsManager("Secrets Manager")
            kms_c = KMS("KMS")
    
    # Role assumption connections
    user >> Edge(label="1. Assumes", color="blue") >> toolchain_role
    toolchain_role >> Edge(label="2. Assumes", color="red") >> deploy_role_b
    toolchain_role >> Edge(label="3. Assumes", color="red") >> deploy_role_c
    
    
    # Toolchain account access
    toolchain_role >> Edge(label="Access", color="orange", style="dashed") >> toolchain_ssm
    toolchain_role >> Edge(label="Access", color="orange", style="dashed") >> toolchain_secrets
    
    # Account B access - Deployment Role can access CodeBuild, S3, and Secrets Manager
    deploy_role_b >> Edge(label="Starts", color="purple", style="dashed") >> codebuild_b
    deploy_role_b >> Edge(label="Access", color="purple", style="dashed") >> s3_b
    deploy_role_b >> Edge(label="Access", color="darkgreen", style="dotted") >> ssm_b
    
    
    # Account B - ONLY CodeBuild can access SSM
    codebuild_b >> Edge(label="Access", color="darkgreen", style="dotted") >> ssm_b
    codebuild_b >> Edge(label="Access", color="purple", style="dashed") >> secrets_b
    codebuild_b >> Edge(label="Access", color="purple", style="dashed") >> s3_b
    s3_b >> Edge(label="Uses", color="black", style="dashed") >> kms_b
    
    
    # Account C access - Deployment Role can access CodeBuild, S3, and Secrets Manager
    deploy_role_c >> Edge(label="Starts", color="brown", style="dashed") >> codebuild_c
    deploy_role_c >> Edge(label="Access", color="brown", style="dashed") >> s3_c
    deploy_role_c >> Edge(label="Access", color="darkred", style="dotted") >> ssm_c
    
    
    # Account C - ONLY CodeBuild can access SSM
    codebuild_c >> Edge(label="Access", color="darkred", style="dotted") >> ssm_c
    codebuild_c >> Edge(label="Access", color="brown", style="dashed") >> secrets_c
    codebuild_c >> Edge(label="Access", color="brown", style="dashed") >> s3_c
    s3_c >> Edge(label="Uses", color="black", style="dashed") >> kms_c
