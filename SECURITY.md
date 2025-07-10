# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 1.0.x   | :white_check_mark: |
| < 1.0   | :x:                |

## Reporting a Vulnerability

We take the security of MCP Nautobot Server seriously. If you discover a security vulnerability, please follow these steps:

1. **DO NOT** open a public issue
2. Email the maintainers at: security@[maintainer-domain].com
3. Include the following information:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

### What to Expect

- Acknowledgment within 48 hours
- Regular updates on the progress
- Credit in the security advisory (unless you prefer to remain anonymous)

### Security Best Practices

When using MCP Nautobot Server:

1. **API Tokens**:
   - Never commit tokens to version control
   - Use environment variables or secure vaults
   - Rotate tokens regularly
   - Use tokens with minimal required permissions

2. **Network Security**:
   - Always use HTTPS for Nautobot connections
   - Verify SSL certificates in production
   - Use VPN or private networks when possible

3. **Access Control**:
   - Limit MCP server access to authorized users
   - Use read-only tokens when write access isn't needed
   - Monitor API usage for anomalies

4. **Data Protection**:
   - Be cautious about exposing network topology
   - Sanitize logs before sharing
   - Encrypt sensitive data at rest

### Known Security Considerations

- Rate limiting is implemented but can be configured
- API responses may contain sensitive network information
- Cached data should be secured appropriately

## Responsible Disclosure

We believe in responsible disclosure and will:
- Work with you to understand and validate the issue
- Patch the vulnerability in a timely manner
- Release a security advisory when appropriate
- Credit researchers who report valid vulnerabilities

Thank you for helping keep MCP Nautobot Server secure!