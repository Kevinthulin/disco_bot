# Security Policy

## Supported Versions

We actively support security updates for the latest version of the bot. Please keep your bot updated.

## Security Best Practices

### Bot Token Security

**CRITICAL**: Never commit your Discord bot token to this repository or any public repository.

1. **Always use environment variables** for your bot token:
   - Set `DISCORD_TOKEN` as an environment variable
   - Never hardcode tokens in source code
   - Never commit `.env` files (they are in `.gitignore`)

2. **If your token is exposed**:
   - Immediately go to [Discord Developer Portal](https://discord.com/developers/applications)
   - Navigate to your bot → Bot section → Reset Token
   - Update the token in all your deployment environments
   - Review bot activity logs for unauthorized access

### Environment Variables

The bot uses the following environment variables:

- `DISCORD_TOKEN` (required) - Your Discord bot token

**Never commit these values to Git.** They are automatically ignored by `.gitignore`.

### Code Security

1. **Input Sanitization**: All user inputs are sanitized to prevent Discord markdown injection
2. **Rate Limiting**: Commands are rate-limited to prevent abuse (2 commands per 5 seconds per user)
3. **SSL Verification**: SSL certificate verification is enabled by default
4. **Error Handling**: Sensitive information is not exposed in error messages

### Dependencies

Regularly update dependencies to receive security patches:

**Using pipenv (recommended for local development):**
```bash
pipenv update
```

**Using pip:**
```bash
pip install --upgrade -r requirements.txt
```

Check for known vulnerabilities:
- Use `pip-audit` or `safety` to scan dependencies
- Monitor GitHub security advisories for `discord.py`, `yt-dlp`, and `PyNaCl`

### Hosting Security

When deploying to hosting platforms:

1. **Use environment variables** in your hosting platform's dashboard
2. **Never commit** hosting configuration files with secrets
3. **Enable logging** to monitor bot activity
4. **Set up alerts** for unusual activity
5. **Use HTTPS** for any web interfaces
6. **Restrict bot permissions** to only what's necessary

### Bot Permissions

Only grant the minimum required permissions:

**Required:**
- Connect (join voice channels)
- Speak (play audio)
- Send Messages (respond to commands)
- Read Message History (read commands)
- Embed Links (for queue display)

**Optional:**
- Use Voice Activity (for better voice quality)

**Do NOT grant:**
- Administrator (unless absolutely necessary)
- Manage Server
- Manage Channels
- Manage Roles
- Kick Members
- Ban Members

### Reporting Security Issues

If you discover a security vulnerability, please **DO NOT** open a public issue. Instead:

1. **Email**: [Your email or create a security contact]
2. **Include**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if any)

We will respond within 48 hours and work with you to resolve the issue.

### Security Checklist for Contributors

Before submitting code:

- [ ] No hardcoded tokens, API keys, or secrets
- [ ] No sensitive data in logs or error messages
- [ ] Input validation and sanitization implemented
- [ ] Rate limiting considered for new commands
- [ ] Dependencies are up to date
- [ ] Code follows security best practices
- [ ] `.gitignore` updated if new sensitive files are created

### Known Security Considerations

1. **YouTube URL Extraction**: Uses `yt-dlp` which may be affected by YouTube API changes
2. **Rate Limiting**: Current rate limit is 2 commands per 5 seconds per user - adjust if needed
3. **Voice Channel Access**: Bot requires voice channel permissions - ensure proper server permissions
4. **Multi-Server Support**: Each server has isolated state - no cross-server data leakage

### Additional Resources

- [Discord Developer Portal Security](https://discord.com/developers/docs/topics/security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.readthedocs.io/en/stable/library/security_warnings.html)

## Disclaimer

This bot is provided as-is. Users are responsible for:
- Securing their bot tokens
- Managing bot permissions appropriately
- Keeping dependencies updated
- Monitoring bot activity
- Complying with Discord's Terms of Service

