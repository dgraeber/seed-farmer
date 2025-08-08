#!/usr/bin/env python3
"""
CDK App for hosting MkDocs site on S3 with CloudFront and Lambda@Edge authentication
"""

import aws_cdk as cdk
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_cloudfront as cloudfront,
    aws_cloudfront_origins as origins,
    aws_lambda as lambda_,
    aws_iam as iam,
    CfnOutput,
    RemovalPolicy,
    Duration
)
import os

class MkDocsHostingStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        
        # Configuration
        team_name = "seed-farmer-team"
        site_name = "seed-farmer-docs"
        
        # S3 bucket for hosting static content
        bucket = s3.Bucket(
            self, "dgraeberaws-seedfarmer-docsv2",
            bucket_name=f"{site_name}-{self.account}-{self.region}",
            public_read_access=False,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
            versioned=True
        )
        
        # Lambda@Edge function for Basic Auth
        auth_function = lambda_.Function(
            self, "AuthFunction",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_auth_function_code()),
            timeout=Duration.seconds(5),
            memory_size=128,
            description="Basic Auth for MkDocs site"
        )
        
        # Lambda@Edge function for URL rewriting (to handle MkDocs routing)
        url_rewrite_function = lambda_.Function(
            self, "UrlRewriteFunction",
            runtime=lambda_.Runtime.NODEJS_18_X,
            handler="index.handler",
            code=lambda_.Code.from_inline(self._get_url_rewrite_function_code()),
            timeout=Duration.seconds(5),
            memory_size=128,
            description="URL rewriting for MkDocs routing"
        )

        # CloudFront distribution
        distribution = cloudfront.Distribution(
            self, "Distribution",
            default_behavior=cloudfront.BehaviorOptions(
                origin=origins.S3BucketOrigin.with_origin_access_control(bucket),
                viewer_protocol_policy=cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
                cache_policy=cloudfront.CachePolicy.CACHING_OPTIMIZED,
                edge_lambdas=[
                    cloudfront.EdgeLambda(
                        function_version=auth_function.current_version,
                        event_type=cloudfront.LambdaEdgeEventType.VIEWER_REQUEST
                    ),
                    cloudfront.EdgeLambda(
                        function_version=url_rewrite_function.current_version,
                        event_type=cloudfront.LambdaEdgeEventType.ORIGIN_REQUEST
                    )
                ]
            ),
            default_root_object="index.html",
            error_responses=[
                # Handle 403 errors (S3 returns 403 for missing files)
                cloudfront.ErrorResponse(
                    http_status=403,
                    response_http_status=404,
                    response_page_path="/404.html",
                    ttl=Duration.minutes(5)
                ),
                # Handle 404 errors
                cloudfront.ErrorResponse(
                    http_status=404,
                    response_http_status=404,
                    response_page_path="/404.html",
                    ttl=Duration.minutes(5)
                )
            ],
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
                sources=[s3deploy.Source.asset(site_path)],
                destination_bucket=bucket,
                distribution=distribution,
                distribution_paths=["/*"]
            )
        
        # Outputs
        CfnOutput(
            self, "BucketName",
            value=bucket.bucket_name,
            description="S3 bucket name for docs"
        )
        
        CfnOutput(
            self, "DistributionDomainName",
            value=distribution.distribution_domain_name,
            description="CloudFront distribution domain name"
        )
        
        CfnOutput(
            self, "DistributionId",
            value=distribution.distribution_id,
            description="CloudFront distribution ID"
        )
        
        CfnOutput(
            self, "SiteURL",
            value=f"https://{distribution.distribution_domain_name}",
            description="Complete site URL"
        )
    
    def _get_url_rewrite_function_code(self) -> str:
        """Returns the Lambda@Edge function code for URL rewriting"""
        return """
exports.handler = async (event) => {
    const request = event.Records[0].cf.request;
    const uri = request.uri;
    
    // If the URI ends with a slash, append index.html
    if (uri.endsWith('/')) {
        request.uri = uri + 'index.html';
    }
    // If the URI doesn't have an extension and doesn't end with a slash, 
    // assume it's a directory and append /index.html
    else if (!uri.includes('.') && !uri.endsWith('/')) {
        request.uri = uri + '/index.html';
    }
    
    return request;
};
"""

    def _get_auth_function_code(self) -> str:
        """Returns the Lambda@Edge function code for Basic Auth"""
        return """
const users = {
    // Add your team members here: 'username': 'password'
    'admin': 'dgrabs',
    'viewer1': 'Thepassword1!',
    'viewer2': 'Thepassword2!'
};

exports.handler = async (event) => {
    const request = event.Records[0].cf.request;
    const headers = request.headers;
    
    // Check if Authorization header exists
    if (!headers.authorization) {
        return {
            status: '401',
            statusDescription: 'Unauthorized',
            headers: {
                'www-authenticate': [{
                    key: 'WWW-Authenticate',
                    value: 'Basic realm="Seed Farmer Documentation - V2"'
                }],
                'content-type': [{
                    key: 'Content-Type',
                    value: 'text/html'
                }]
            },
            body: `
                <html>
                <head><title>401 Unauthorized</title></head>
                <body>
                    <h1>Unauthorized</h1>
                    <p>Please provide valid credentials to access the Seed Farmer documentation.</p>
                </body>
                </html>
            `
        };
    }
    
    // Parse Basic Auth header
    const authHeader = headers.authorization[0].value;
    const encoded = authHeader.split(' ')[1];
    const decoded = Buffer.from(encoded, 'base64').toString('utf-8');
    const [username, password] = decoded.split(':');
    
    // Validate credentials
    if (!users[username] || users[username] !== password) {
        return {
            status: '401',
            statusDescription: 'Unauthorized',
            headers: {
                'www-authenticate': [{
                    key: 'WWW-Authenticate',
                    value: 'Basic realm="Seed Farmer Documentation"'
                }],
                'content-type': [{
                    key: 'Content-Type',
                    value: 'text/html'
                }]
            },
            body: `
                <html>
                <head><title>401 Unauthorized</title></head>
                <body>
                    <h1>Unauthorized</h1>
                    <p>Invalid credentials. Please contact your team administrator.</p>
                </body>
                </html>
            `
        };
    }
    
    // Allow the request to proceed
    return request;
};
"""

app = cdk.App()
MkDocsHostingStack(app, "MkDocsHostingStack",
    env=cdk.Environment(
        account=os.getenv('CDK_DEFAULT_ACCOUNT'),
        region=os.getenv('CDK_DEFAULT_REGION', 'us-east-1')  # Lambda@Edge requires us-east-1
    )
)

app.synth()
