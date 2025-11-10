# Instructions to Push to GitHub

## Option 1: Push from Your Terminal (Recommended)

1. Open your terminal and navigate to the project:
   ```bash
   cd "/Users/zinebaourid/Library/CloudStorage/OneDrive-Personal/Programming/2025/MINDAI"
   ```

2. Push to GitHub:
   ```bash
   git push origin main
   ```

3. When prompted:
   - **Username**: Enter your GitHub username
   - **Password**: Enter your Personal Access Token (NOT your GitHub password)
   - The token will be saved securely in macOS Keychain for future use

## Option 2: Use Token in URL (One-time)

If you prefer to push now with the token in the URL:

```bash
git push https://YOUR_USERNAME:YOUR_TOKEN@github.com/zaourid1/hellosynk.git main
```

Replace:
- `YOUR_USERNAME` with your GitHub username
- `YOUR_TOKEN` with your Personal Access Token

⚠️ **Note**: This method exposes the token in the command history. Consider Option 1 for better security.

## Option 3: Use Environment Variable

```bash
export GIT_ASKPASS=echo
git -c credential.helper='!f() { echo "username=YOUR_USERNAME"; echo "password=YOUR_TOKEN"; }; f' push origin main
```

## Creating a Personal Access Token

If you don't have a token yet:

1. Go to GitHub.com → Settings → Developer settings
2. Click "Personal access tokens" → "Tokens (classic)"
3. Click "Generate new token (classic)"
4. Give it a name (e.g., "HelloSynk Project")
5. Select scope: **repo** (full control of private repositories)
6. Click "Generate token"
7. **Copy the token immediately** (you won't see it again!)

## What Will Be Pushed

All 27 files are ready to push:
- ✅ All HelloSynk source code (hellosynk/)
- ✅ Examples and documentation
- ✅ Configuration files
- ✅ No personal information or API keys

