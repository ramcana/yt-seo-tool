# Security Guidelines

## Sensitive Files - NEVER Commit These!

### ✅ Already Protected in `.gitignore`

**OAuth & Authentication:**
- `config/client_secret.json` - Google OAuth client credentials
- `token.pickle` / `token.json` - OAuth access/refresh tokens
- `credentials.json` - Any credential files
- `*.token`, `*.credentials` - Token files
- `oauth_token*`, `refresh_token*` - Token variants

**Environment & Configuration:**
- `.env` - Environment variables (API keys, secrets)
- `.env.local` - Local environment overrides
- `config/*secret*.json` - Any secret config files

**API Keys & Certificates:**
- `*.key` - Private keys
- `*.pem` - Certificate files
- `*.p12`, `*.pfx` - Certificate bundles
- `api_key*` - API key files
- `service_account*.json` - Service account credentials

**Databases:**
- `*.db`, `*.sqlite` - Local databases (may contain sensitive data)

## Setup Checklist

### Initial Setup
1. ✅ Copy `.env.example` to `.env`
2. ✅ Add your credentials to `.env` (NEVER commit this file)
3. ✅ Place `client_secret.json` in `config/` directory
4. ✅ Run OAuth flow to generate `token.pickle`
5. ✅ Verify `.gitignore` is working:
   ```bash
   git status
   # Should NOT show token.pickle, client_secret.json, or .env
   ```

### Before Committing
1. ✅ Run `git status` and verify no sensitive files are staged
2. ✅ Check for accidentally committed secrets:
   ```bash
   git diff --cached | grep -i "secret\|token\|key\|password"
   ```
3. ✅ Review `.env.example` - should only contain placeholders

### If You Accidentally Commit Secrets

**IMMEDIATELY:**
1. Rotate all exposed credentials (revoke and regenerate)
2. Remove from git history:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/secret/file" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. Force push (if already pushed to remote)
4. Update `.gitignore` to prevent recurrence

## Safe Configuration Practices

### ✅ DO:
- Use `.env` files for secrets (excluded from git)
- Use `settings.example.toml` with placeholders
- Document required environment variables in README
- Use environment variables in production
- Rotate credentials regularly
- Use different credentials for dev/staging/prod

### ❌ DON'T:
- Hardcode API keys or secrets in code
- Commit `.env` files
- Share credentials via chat/email
- Use production credentials in development
- Store secrets in code comments
- Commit database files with real data

## OAuth Token Security

### Current Implementation
- **Storage:** `token.pickle` (binary serialized)
- **Location:** Project root (gitignored)
- **Scope:** YouTube Data API (read/write)
- **Refresh:** Automatic via google-auth library

### Best Practices
1. **Token Storage:**
   - Keep `token.pickle` in gitignored location
   - Set restrictive file permissions (600 on Unix)
   - Never share or commit tokens

2. **Token Refresh:**
   - Tokens auto-refresh when expired
   - Monitor for refresh failures
   - Re-authenticate if refresh fails

3. **Scope Management:**
   - Only request necessary scopes
   - Current: `youtube`, `youtube.force-ssl`
   - Review scopes periodically

## Safety Controls for YouTube API

### Multi-Layer Protection
1. **DRY_RUN=true** (default)
   - Logs changes without applying
   - Test mode for all operations

2. **REQUIRE_CONFIRMATION=true** (default)
   - Manual typing "APPLY" required
   - Prevents accidental updates

3. **Tag Merging**
   - Never deletes existing tags
   - Only adds new tags

4. **Original Value Backup**
   - Stores original metadata before changes
   - Enables rollback if needed

### Configuration
```toml
[safety]
DRY_RUN = true              # ALWAYS true for testing
REQUIRE_CONFIRMATION = true  # ALWAYS true for production
MERGE_TAGS = true           # Never delete tags
```

## Monitoring & Auditing

### Check for Exposed Secrets
```bash
# Scan git history for secrets
git log -p | grep -i "secret\|token\|key\|password"

# Check current files
grep -r "sk-" .  # OpenAI keys
grep -r "AIza" . # Google API keys
```

### Regular Security Tasks
- [ ] Monthly: Rotate OAuth credentials
- [ ] Quarterly: Review `.gitignore` patterns
- [ ] Quarterly: Audit API access logs
- [ ] Yearly: Review and update scopes

## Incident Response

### If Credentials Are Compromised
1. **Immediate Actions:**
   - Revoke compromised credentials in Google Cloud Console
   - Generate new credentials
   - Update `.env` with new credentials
   - Clear `token.pickle` and re-authenticate

2. **Investigation:**
   - Check git history for exposure
   - Review access logs for unauthorized use
   - Identify how credentials were exposed

3. **Prevention:**
   - Update `.gitignore` if needed
   - Document lessons learned
   - Update security procedures

## Resources

- [Google OAuth 2.0 Best Practices](https://developers.google.com/identity/protocols/oauth2/best-practices)
- [YouTube Data API Security](https://developers.google.com/youtube/v3/guides/authentication)
- [Git Secrets Detection](https://github.com/awslabs/git-secrets)
