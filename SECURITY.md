# Security Policy

## 🔒 Repository Security Overview

This repository implements comprehensive security measures to prevent unauthorized access and ensure safe release processes.

## 🛡️ Security Measures Implemented

### Branch Protection
- **Main Branch**: Protected with the following rules:
  - ✅ Required status checks (CI tests must pass)
  - ✅ Required pull request reviews (1 reviewer minimum)
  - ✅ Dismiss stale reviews when new commits are pushed
  - ✅ Require conversation resolution before merging
  - ✅ Require linear history (no merge commits)
  - ✅ Prohibit force pushes and branch deletions
  - ✅ Enforce admin compliance (admins cannot bypass rules)

### Environment Protection (PyPI Deployment)
- **PyPI Environment**: Requires manual approval for all deployments
  - ✅ Required reviewer: @krabhishek (repository owner)
  - ✅ Branch policy: Only protected branches can deploy
  - ✅ Environment secrets: PyPI credentials are environment-scoped

### Repository Security Features
- ✅ **Dependabot Vulnerability Alerts**: Automatic detection of vulnerable dependencies
- ✅ **Secret Scanning**: Detects accidentally committed secrets
- ✅ **Push Protection**: Blocks commits containing secrets
- ✅ **Code Scanning**: Vulnerability detection in source code (when configured)

### Workflow Security
- ✅ **Least Privilege Permissions**: Each workflow job has minimal required permissions
- ✅ **Explicit Permission Declarations**: No default or inherited permissions
- ✅ **Environment Contexts**: Sensitive operations use protected environments
- ✅ **Manual Approval Gates**: PyPI releases require explicit approval

## 🚀 Release Process

### Automated (Requires Approval)
1. **Create Release Tag**: `git tag v1.0.0 && git push origin v1.0.0`
2. **CI Validation**: Automatic testing and quality checks
3. **TestPyPI Deployment**: Automatic deployment to test environment
4. **Manual Approval**: Repository owner must approve PyPI deployment
5. **PyPI Release**: Package published to production PyPI
6. **GitHub Release**: Automatic GitHub release creation

### Emergency Release (Manual Dispatch)
1. **Navigate to Actions**: Go to GitHub Actions → Release to PyPI
2. **Run Workflow**: Click "Run workflow" button
3. **Select Environment**: Choose 'pypi' for production release
4. **Emergency Flag**: Check emergency option if needed
5. **Manual Approval**: Still requires approval for PyPI deployment

## 🔐 Access Control

### Repository Access
- **Owner**: @krabhishek (full admin access)
- **Collaborators**: None (add only trusted contributors)
- **Actions**: Environment protection prevents unauthorized releases

### Secrets Management
- **Repository Secrets**: None (avoid repository-level secrets)
- **Environment Secrets**: PyPI credentials stored in environment scope
- **Local Development**: Use personal tokens or local configuration

## 📋 Security Checklist for Contributors

- [ ] Never commit secrets, API keys, or credentials
- [ ] All changes require pull request review
- [ ] CI tests must pass before merging
- [ ] Follow semantic versioning for releases
- [ ] Use signed commits when possible
- [ ] Report security vulnerabilities privately

## 🚨 Security Incident Response

1. **Suspected Compromise**: Contact @krabhishek immediately
2. **Vulnerable Dependencies**: Dependabot will create alerts automatically
3. **Secret Exposure**: Push protection will block, but verify no secrets were committed
4. **Unauthorized Access**: Check repository access logs and revoke access tokens

## 📞 Reporting Security Issues

Please report security vulnerabilities privately to the repository owner:
- **GitHub**: @krabhishek
- **Method**: GitHub Security Advisories or direct contact

Do not create public issues for security vulnerabilities.

## 🔄 Security Audit Log

- **2025-06-22**: Initial security configuration implemented
  - Branch protection rules activated
  - Environment protection configured
  - Repository security features enabled
  - Workflow permissions restricted

---

*Last updated: 2025-06-22*
*Security measures are regularly reviewed and updated*