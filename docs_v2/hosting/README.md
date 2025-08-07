# MkDocs Site Hosting with Team Authentication

This solution hosts your MkDocs site on AWS S3 with CloudFront distribution and Lambda@Edge authentication, providing secure team-only access without IP restrictions.

## Architecture

```
Internet → CloudFront → Lambda@Edge (Auth) → S3 Bucket
```

**Components:**
- **S3 Bucket**: Hosts static MkDocs site files
- **CloudFront**: CDN for fast global delivery
- **Lambda@Edge**: Basic HTTP authentication for team access
- **Origin Access Control**: Secures S3 bucket (no public access)

## Features

✅ **Team-based authentication** (not IP-based)  
✅ **Basic HTTP Auth** (username/password)  
✅ **Secure S3 hosting** (no public access)  
✅ **Global CDN** via CloudFront  
✅ **Easy user management** via CLI scripts  
✅ **Automatic deployments** and updates  

## Quick Start

### 1. Initial Deployment

```bash
# Deploy the infrastructure and site
./deploy.sh
```

This will:
- Install CDK dependencies
- Bootstrap CDK (if needed)
- Deploy S3 bucket, CloudFront, and Lambda@Edge
- Upload your MkDocs site

### 2. Manage Team Access

```bash
# List current users
python manage-users.py list

# Add a team member
python manage-users.py add --username john.doe

# Update a password
python manage-users.py update --username john.doe

# Remove a user
python manage-users.py remove --username john.doe
```

### 3. Update Site Content

```bash
# Update the site with latest content
./update-content.sh
```

This will:
- Build the latest MkDocs site
- Upload to S3
- Invalidate CloudFront cache

## User Management

### Adding Team Members

```bash
python manage-users.py add --username alice
# You'll be prompted for a password
```

### Default Users

The initial deployment includes these default users (⚠️ **Change these immediately**):
- `admin` / `your-secure-password-here`
- `team-member-1` / `another-secure-password`
- `team-member-2` / `yet-another-password`

### Security Best Practices

1. **Change default passwords immediately** after deployment
2. **Use strong passwords** (12+ characters, mixed case, numbers, symbols)
3. **Remove unused accounts** regularly
4. **Share credentials securely** (use password managers)

## Deployment Details

### Prerequisites

- AWS CLI configured with appropriate permissions
- Python 3.8+ with pip
- CDK CLI installed (`npm install -g aws-cdk`)

### Required AWS Permissions

Your AWS credentials need these permissions:
- CloudFormation (full access)
- S3 (create buckets, upload objects)
- CloudFront (create distributions)
- Lambda (create functions, update code)
- IAM (create roles for services)

### Costs

Estimated monthly costs for a team site:
- **S3 Storage**: ~$1-5 (depending on site size)
- **CloudFront**: ~$1-10 (depending on traffic)
- **Lambda@Edge**: ~$0.50-2 (per million requests)
- **Total**: ~$2.50-17/month

## Customization

### Changing Authentication Method

Edit `app.py` to modify the Lambda@Edge function:

1. **Custom realm name**: Change `'Basic realm="Your Team Name"'`
2. **Error pages**: Customize the HTML in the 401 responses
3. **Additional security**: Add IP restrictions, rate limiting, etc.

### Custom Domain

To use your own domain (e.g., `docs.yourcompany.com`):

1. Add Route 53 hosted zone
2. Request ACM certificate
3. Update the CloudFront distribution in `app.py`

### Advanced Authentication

For more sophisticated auth, consider:
- **AWS Cognito**: User pools with email verification
- **SAML/OIDC**: Integration with corporate identity providers
- **API Keys**: Token-based authentication for developers

## Troubleshooting

### Common Issues

**"Access Denied" errors:**
- Check that CloudFront has proper S3 permissions
- Verify Origin Access Control is configured

**Authentication not working:**
- Lambda@Edge changes take 5-10 minutes to propagate
- Check CloudWatch Logs in us-east-1 region

**Site not updating:**
- Run CloudFront invalidation: `./update-content.sh`
- Check S3 bucket contents

### Monitoring

- **CloudWatch Logs**: Lambda@Edge logs in us-east-1
- **CloudFront Metrics**: Request counts, error rates
- **S3 Access Logs**: Detailed access patterns

## Scripts Reference

| Script | Purpose |
|--------|---------|
| `deploy.sh` | Initial deployment of infrastructure |
| `update-content.sh` | Update site content and invalidate cache |
| `manage-users.py` | Add/remove/update user credentials |

## Security Considerations

### What This Protects Against
- ✅ Unauthorized public access
- ✅ Accidental exposure of internal docs
- ✅ Basic credential-based access control

### What This Doesn't Protect Against
- ❌ Advanced persistent threats
- ❌ Credential sharing/leakage
- ❌ Man-in-the-middle attacks (use HTTPS only)

### Recommendations
1. **Use HTTPS only** (enforced by CloudFront)
2. **Rotate passwords regularly**
3. **Monitor access logs** for suspicious activity
4. **Consider MFA** for highly sensitive content

## Cleanup

To remove all resources:

```bash
cdk destroy
```

This will delete:
- CloudFront distribution
- S3 bucket and contents
- Lambda@Edge function
- All associated IAM roles

---

## Support

For issues or questions:
1. Check CloudWatch Logs for Lambda@Edge errors
2. Verify AWS permissions and credentials
3. Review the CDK deployment logs
