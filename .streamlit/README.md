# Streamlit Configuration

This directory contains Streamlit-specific configuration files.

## ⚠️ IMPORTANT: Secrets Management (secrets.toml)

**SECURITY NOTICE:** Streamlit secrets are **DISABLED by default** in this application to prevent accidental API key exposure on cloud deployments.

### Why Secrets Are Disabled

When deployed to Streamlit Cloud or other hosting platforms, secrets can potentially expose the developer's API keys to all users. To prevent this security issue:

- ✅ **Secrets are disabled by default**
- ✅ **Users must enter their own API keys via the UI**
- ✅ **Each user's API key is stored locally in their session**

### Recommended: Manual API Key Entry

**For all users (local and cloud):**

1. Open the E-Book Maker app
2. Go to "🤖 AI Settings"
3. Enter your API key in the text field
4. Click "💾 Save & Test API Key"

Your API key will be saved to `config/ai_config.json` for future sessions.

### Getting Your API Key

Get your **FREE** Groq API key at: [https://console.groq.com/keys](https://console.groq.com/keys)

### Advanced: Local Development Only (Optional)

If you're running the app **locally for development** and want to use secrets.toml for convenience, you can manually enable it:

1. **Edit `app_streamlit.py` line 48:**
   ```python
   # Change from:
   st.session_state.ai_assistant = GroqAssistant()

   # To:
   st.session_state.ai_assistant = GroqAssistant(
       streamlit_secrets=st.secrets,
       allow_secrets=True
   )
   ```

2. **Create `.streamlit/secrets.toml`:**
   ```bash
   cp .streamlit/secrets.toml.example .streamlit/secrets.toml
   ```

3. **Add your API key:**
   ```toml
   GROQ_API_KEY = "gsk_your_actual_api_key_here"
   ```

⚠️ **WARNING:**
- **NEVER** enable secrets on cloud deployments
- **NEVER** commit `secrets.toml` to git (it's already in `.gitignore`)
- Only use this for **local development**

### Security Best Practices

- 🔒 Each user should use their **own** Groq API key
- 🔒 Never share or commit API keys to version control
- 🔒 Use the UI-based API key entry for maximum security
- 🔒 The `secrets.toml.example` file is safe to commit (contains no real keys)

For more information on Streamlit secrets, see: [Streamlit Secrets Documentation](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
