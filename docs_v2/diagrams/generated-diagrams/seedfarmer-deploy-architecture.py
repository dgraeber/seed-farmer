from diagrams import Diagram, Cluster, Edge
from diagrams.aws.general import General, User
from diagrams.aws.security import IAMRole, SecretsManager
from diagrams.aws.management import ParameterStore
from diagrams.aws.devtools import Codebuild
from diagrams.aws.storage import S3
from diagrams.aws.security import KeyManagementService as KMS

def create_diagram(title, filename, output_format="png"):
    with Diagram(title, show=False, direction="TB", filename=filename, outformat=output_format):
        
        # End User
        user = User("End User / CICD Role")
        
        # Toolchain Account
        with Cluster("Toolchain Account"):
            with Cluster("us-east-1"):
                toolchain_role = IAMRole("SeedFarmer Toolchain Role")
                toolchain_ssm = ParameterStore("SSM Parameters")
                toolchain_secrets = SecretsManager("Secrets Manager")
        
        # Deployment Accounts
        with Cluster("Deployment Accounts"):
            with Cluster("Account A"):
                with Cluster("us-east-1"):
                    deploy_role_a = IAMRole("SeedFarmer Deployment Role")
                    codebuild_a = Codebuild("CodeBuild Project")
                    module_role_a = IAMRole("Module Role")
                    s3_a = S3("S3 Bucket")
                    ssm_a = ParameterStore("SSM Parameters")
                    secrets_a = SecretsManager("Secrets Manager")
                    kms_a = KMS("KMS")
            
            with Cluster("Account B"):
                with Cluster("us-west-2"):
                    deploy_role_b = IAMRole("SeedFarmer Deployment Role")
                    codebuild_b = Codebuild("CodeBuild Project")
                    module_role_b = IAMRole("Module Role")
                    s3_b = S3("S3 Bucket")
                    ssm_b = ParameterStore("SSM Parameters")
                    secrets_b = SecretsManager("Secrets Manager")
                    kms_b = KMS("KMS")
        
        # Role assumption connections
        user >> Edge(label="Assumes", color="red") >> toolchain_role
        toolchain_role >> Edge(label="Assumes", color="red", style="bold") >> deploy_role_a
        toolchain_role >> Edge(label="Assumes", color="red", style="bold") >> deploy_role_b
        
        # CodeBuild assumes Module Roles
        module_role_a >> Edge(label="Attached", color="red", style="bold") >> codebuild_a
        module_role_b >> Edge(label="Attached", color="red", style="bold") >> codebuild_b
        
        # Toolchain account access
        toolchain_role >> Edge(label="Access", color="purple", style="dashed") >> toolchain_ssm
        toolchain_role >> Edge(label="Access", color="purple", style="dashed") >> toolchain_secrets
        
        # Account A access - Deployment Role can access CodeBuild, S3, and Secrets Manager
        deploy_role_a >> Edge(label="Starts", color="purple", style="dashed") >> codebuild_a
        deploy_role_a >> Edge(label="Access", color="purple", style="dashed") >> s3_a
        deploy_role_a >> Edge(label="Access", color="purple", style="dashed") >> ssm_a
        
        # Account A - CodeBuild access
        codebuild_a >> Edge(label="Access", color="darkgreen", style="dashed") >> ssm_a
        codebuild_a >> Edge(label="Access", color="darkgreen", style="dashed") >> secrets_a
        codebuild_a >> Edge(label="Access", color="darkgreen", style="dashed") >> s3_a
        
        # Account A - Module Role access (for actual deployments)
        module_role_a >> Edge(label="Access", color="darkblue", style="dashed") >> s3_a
        module_role_a >> Edge(label="Access", color="darkblue", style="dashed") >> secrets_a
        
        s3_a >> Edge(label="Uses", color="black", style="dashed") >> kms_a
        
        # Account B access - Deployment Role can access CodeBuild, S3, and Secrets Manager
        deploy_role_b >> Edge(label="Starts", color="purple", style="dashed") >> codebuild_b
        deploy_role_b >> Edge(label="Access", color="purple", style="dashed") >> s3_b
        deploy_role_b >> Edge(label="Access", color="purple", style="dashed") >> ssm_b
        
        # Account B - CodeBuild access
        codebuild_b >> Edge(label="Access", color="darkgreen", style="dashed") >> ssm_b
        codebuild_b >> Edge(label="Access", color="darkgreen", style="dashed") >> secrets_b
        codebuild_b >> Edge(label="Access", color="darkgreen", style="dashed") >> s3_b
        
        # Account B - Module Role access (for actual deployments)
        module_role_b >> Edge(label="Access", color="darkblue", style="bold") >> s3_b
        module_role_b >> Edge(label="Access", color="darkblue", style="bold") >> secrets_b
        
        s3_b >> Edge(label="Uses", color="black", style="dashed") >> kms_b

# Generate both formats
create_diagram("SeedFarmer Cross Account Deployments", "seedfarmer_cross_account_deployments", "png")
create_diagram("SeedFarmer Cross Account Deployments", "seedfarmer_cross_account_deployments", "dot")
