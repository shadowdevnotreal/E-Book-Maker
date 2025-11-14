# Streamlit Configuration

This directory contains Streamlit-specific configuration files.

## Secrets Management (secrets.toml)

The **recommended way** to configure your Groq API key is using Streamlit's built-in secrets management.

### Why Use Secrets?

✅ **Secure** - Never commit API keys to git
✅ **Convenient** - No need to enter key in UI every time
✅ **Automatic** - Works immediately on app start
✅ **Standard** - Uses Streamlit's official secrets management

### Setup Instructions

1. **Copy the example file:**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

2. **Edit the file and add your actual API key:**
   ```toml
   GROQ_API_KEY = "gsk_your_actual_api_key_here"
   ```

3. **Restart the Streamlit app:**
   ```bash
   streamlit run app_streamlit.py
   ```

4. **Verify it's working:**
   - Go to "🤖 AI Settings" in the app
   - You should see "✅ API Key loaded from **secrets.toml**"

### Getting Your API Key

Get your free Groq API key at: [https://console.groq.com/keys](https://console.groq.com/keys)

### Security Notes

- ⚠️ **Never commit `secrets.toml` to git** (it's already in `.gitignore`)
- ✅ The `secrets.toml.example` file is safe to commit (it contains no real keys)
- ✅ Local secrets work for local development
- ✅ For Streamlit Cloud deployment, use the Streamlit Cloud secrets manager

### Alternative: Manual Entry

If you prefer not to use secrets.toml, you can still enter your API key manually through the UI:
1. Go to "🤖 AI Settings"
2. Scroll to "Manual API Key Entry"
3. Enter your API key and click "💾 Save & Test API Key"

The manual entry method stores the key in `config/ai_config.json`.

### Priority Order

The app checks for API keys in this order:
1. **First:** `.streamlit/secrets.toml` (recommended)
2. **Second:** `config/ai_config.json` (manual entry fallback)

## Streamlit Cloud Deployment

When deploying to Streamlit Cloud:

1. Go to your app settings on Streamlit Cloud
2. Navigate to "Secrets"
3. Add your secret in TOML format:
   ```toml
   GROQ_API_KEY = "gsk_your_api_key_here"
   ```
4. Save and redeploy

For more information, see: [Streamlit Secrets Documentation](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
