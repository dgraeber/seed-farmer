#!/usr/bin/env python3
"""
Alternative CDK App using AWS Cognito for more sophisticated authentication
"""

import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_cognito as cognito,
    aws_lambda as lambda_,
    aws_apigateway as apigateway,
    aws_iam as iam,
    CfnOutput,
    RemovalPolicy,
    Duration
)
import os

class MkDocsCognitoStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Configuration
        team_name = "seed-farmer-team"
        site_name = "seed-farmer-docs"
        
        # Cognito User Pool
        user_pool = cognito.UserPool(
            self, "UserPool",
            user_pool_name=f"{site_name}-users",
            sign_in_aliases=cognito.SignInAliases(email=True),
            auto_verify=cognito.AutoVerifiedAttrs(email=True),
            password_policy=cognito.PasswordPolicy(
                min_length=8,
                require_lowercase=True,
                require_uppercase=True,
                require_digits=True,
                require_symbols=False
            ),
            account_recovery=cognito.AccountRecovery.EMAIL_ONLY,
            removal_policy=RemovalPolicy.DESTROY
        )
        
        # Cognito User Pool Client
        user_pool_client = cognito.UserPoolClient(
            self, "UserPoolClient",
            user_pool=user_pool,
            generate_secret=True,
            auth_flows=cognito.AuthFlow(
                user_password=True,
                user_srp=True
            ),
            o_auth=cognito.OAuthSettings(
                flows=cognito.OAuthFlows(authorization_code_grant=True),
                scopes=[cognito.OAuthScope.OPENID, cognito.OAuthScope.EMAIL],
                callback_urls=["https://example.com/callback"]  # Will be updated after CloudFront
            )
        )
        
        # S3 bucket for hosting static content
        bucket = s3.Bucket(
            self, "DocsBucket",
            bucket_name=f"{site_name}-{self.account}-{self.region}",
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioned=True
        )
        
        # Lambda function for Cognito authentication
        auth_lambda = lambda_.Function(
            self, "CognitoAuthFunction",
            runtime=lambda_.Runtime.PYTHON_3_9,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_cognito_auth_code()),
            timeout=Duration.seconds(30),
            environment={
                "USER_POOL_ID": user_pool.user_pool_id,
                "CLIENT_ID": user_pool_client.user_pool_client_id,
                "BUCKET_NAME": bucket.bucket_name
            }
        )
        
        # Grant Lambda permissions to Cognito and S3
        user_pool.grant(auth_lambda, "cognito-idp:AdminInitiateAuth", "cognito-idp:AdminGetUser")
        bucket.grant_read(auth_lambda)
        
        # API Gateway for authentication endpoint
        api = apigateway.RestApi(
            self, "AuthAPI",
            rest_api_name=f"{site_name}-auth",
            description="Authentication API for MkDocs site",
            default_cors_preflight_options=apigateway.CorsOptions(
                allow_origins=apigateway.Cors.ALL_ORIGINS,
                allow_methods=apigateway.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "Authorization"]
            )
        )
        
        # API Gateway integration
        auth_integration = apigateway.LambdaIntegration(auth_lambda)
        api.root.add_method("POST", auth_integration)
        
        # Origin Access Control for CloudFront
        oac = cloudfront.OriginAccessControl(
            self, "OAC",
            description=f"OAC for {site_name}",
            origin_access_control_origin_type=cloudfront.OriginAccessControlOriginType.S3,
            signing_behavior=cloudfront.OriginAccessControlSigningBehavior.ALWAYS,
            signing_protocol=cloudfront.OriginAccessControlSigningProtocol.SIGV4
        )
        
        # CloudFront distribution
        distribution = cloudfront.Distribution(
            self, "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3Origin(
                    bucket,
                    origin_access_control=oac
                ),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED
            ),
            additional_behaviors={
                "/auth/*": cloudfront.BehaviorOptions(
                    origin=origins.RestApiOrigin(api),
                    viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                    cache_policy=cloudfront.CachePolicy.CACHING_DISABLED,
                    allowed_methods=cloudfront.AllowedMethods.ALLOW_ALL
                )
            },
            default_root_object="login.html",
            comment=f"CloudFront distribution for {site_name}",
            price_class=cloudfront.PriceClass.PRICE_CLASS_100
        )
        
        # Grant CloudFront access to S3 bucket
        bucket.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                principals=[iam.ServicePrincipal("cloudfront.amazonaws.com")],
                actions=["s3:GetObject"],
                resources=[f"{bucket.bucket_arn}/*"],
                conditions={
                    "StringEquals": {
                        "AWS:SourceArn": f"arn:aws:cloudfront::{self.account}:distribution/{distribution.distribution_id}"
                    }
                }
            )
        )
        
        # Deploy MkDocs site to S3 (if site directory exists)
        site_path = "/home/dgraeber/workplace/seed-group/seed-farmer/docs_v2/site"
        if os.path.exists(site_path):
            s3deploy.BucketDeployment(
                self, "DeployDocs",
                sources=[
                    s3deploy.Source.asset(site_path),
                    s3deploy.Source.asset("./auth-assets")  # Login page assets
                ],
                destination_bucket=bucket,
                distribution=distribution,
                distribution_paths=["/*"]
            )
        
        # Outputs
        CfnOutput(self, "UserPoolId", value=user_pool.user_pool_id)
        CfnOutput(self, "UserPoolClientId", value=user_pool_client.user_pool_client_id)
        CfnOutput(self, "BucketName", value=bucket.bucket_name)
        CfnOutput(self, "DistributionDomainName", value=distribution.distribution_domain_name)
        CfnOutput(self, "SiteURL", value=f"https://{distribution.distribution_domain_name}")
        CfnOutput(self, "AuthAPIURL", value=api.url)
    
    def _get_cognito_auth_code(self) -> str:
        """Returns the Lambda function code for Cognito authentication"""
        return """
import json
import boto3
import os
from botocore.exceptions import ClientError

cognito = boto3.client('cognito-idp')
s3 = boto3.client('s3')

USER_POOL_ID = os.environ['USER_POOL_ID']
CLIENT_ID = os.environ['CLIENT_ID']
BUCKET_NAME = os.environ['BUCKET_NAME']

def handler(event, context):
    try:
        body = json.loads(event['body'])
        username = body.get('username')
        password = body.get('password')
        
        if not username or not password:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Username and password required'})
            }
        
        # Authenticate with Cognito
        response = cognito.admin_initiate_auth(
            UserPoolId=USER_POOL_ID,
            ClientId=CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': username,
                'PASSWORD': password
            }
        )
        
        # Generate signed URLs for S3 objects (simplified approach)
        # In production, you'd want to implement proper session management
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'message': 'Authentication successful',
                'token': response['AuthenticationResult']['AccessToken']
            })
        }
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'NotAuthorizedException':
            return {
                'statusCode': 401,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Invalid credentials'})
            }
        else:
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Authentication failed'})
            }
    
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
"""

# Uncomment to use Cognito version instead of Basic Auth
# app = cdk.App()
# MkDocsCognitoStack(app, "MkDocsCognitoStack")
# app.synth()
