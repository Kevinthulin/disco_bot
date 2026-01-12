# Pre-Commit Security Checklist

Before committing and pushing to GitHub, verify:

## Critical Checks

- [ ] **No Discord bot tokens** in any files
- [ ] **No `.env` files** (they're in `.gitignore` but double-check)
- [ ] **No hardcoded secrets** in code
- [ ] **No API keys** or passwords in source code
- [ ] **No credentials** in configuration files

## File-Specific Checks

### Configuration Files
- [ ] `render.yaml` - Only contains key names, no values (`sync: false`)
- [ ] `railway.json` - No token values
- [ ] `Procfile` - No secrets
- [ ] `requirements.txt` - No private repositories

### Code Files
- [ ] All tokens use `os.getenv('DISCORD_TOKEN')` or similar
- [ ] No `token = "..."` hardcoded strings
- [ ] No `password = "..."` hardcoded strings
- [ ] No `api_key = "..."` hardcoded strings

### Documentation
- [ ] Examples use placeholders like `YOUR_TOKEN_HERE`
- [ ] No actual tokens in README or guides
- [ ] Security warnings are present

## Quick Verification Commands

Before committing, run these checks:

```bash
# Search for potential tokens (should return no results)
grep -r "MTIzNDU2Nzg5MDEyMzQ1Njc4OTA" . --exclude-dir=.git

# Check for .env files (should return no results)
find . -name ".env*" -not -path "./.git/*"

# Check for common secret patterns
grep -ri "discord.*token.*=" . --exclude-dir=.git --exclude="*.md"
```

## If You Find Secrets

1. **If already committed**: 
   - Reset the commit: `git reset HEAD~1`
   - Remove the secret from files
   - If pushed, reset your token immediately

2. **If pushed to GitHub**:
   - Reset your Discord bot token immediately
   - Consider using `git-filter-repo` to remove secrets from history
   - See [GitHub's guide on removing sensitive data](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository)

## Safe to Commit

These are safe to commit:
- Environment variable names (e.g., `DISCORD_TOKEN`)
- Placeholder values (e.g., `YOUR_TOKEN_HERE`)
- Configuration file structure (without values)
- Code that reads from environment variables

