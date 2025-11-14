/**
 * Universal AI Assistant Widget
 * Provides AI-powered help on all pages
 */

class AIAssistant {
    constructor() {
        this.isOpen = false;
        this.isEnabled = false;
        this.conversationHistory = [];
        this.conversationContext = {}; // Store context like topic, genre, etc.
        this.userPreferences = {}; // Remember user preferences
        this.lastActivity = Date.now();
        this.proactiveMode = true; // Enable proactive suggestions
        this.init();
    }

    async init() {
        // Check if AI is enabled
        try {
            const response = await fetch('/api/ai/status');
            const status = await response.json();
            this.isEnabled = status.enabled;

            if (this.isEnabled) {
                this.createWidget();
                this.attachEventListeners();
                this.showAIBadge();
            }
        } catch (error) {
            console.log('AI Assistant not available');
        }
    }

    createWidget() {
        const widget = document.createElement('div');
        widget.id = 'ai-assistant-widget';
        widget.innerHTML = `
            <!-- Floating Button -->
            <button class="ai-float-button" id="ai-toggle-btn" title="AI Assistant - Get help with marketing, research, and using the tools">
                <span class="ai-icon">📚</span>
                <span class="ai-button-text">AI Help</span>
                <span class="ai-notification-dot"></span>
            </button>

            <!-- Chat Panel -->
            <div class="ai-chat-panel" id="ai-chat-panel" style="display: none;">
                <div class="ai-chat-header">
                    <div class="ai-header-content">
                        <span class="ai-header-icon">📚</span>
                        <div>
                            <h4>AI Publishing Assistant</h4>
                            <p class="ai-status-text">Powered by <strong>Groq</strong></p>
                        </div>
                    </div>
                    <button class="ai-close-btn" id="ai-close-btn">✕</button>
                </div>

                <div class="ai-chat-messages" id="ai-chat-messages">
                    <div class="ai-message ai-message-assistant">
                        <div class="ai-message-content">
                            👋 <strong>Hi! I'm your AI Publishing Assistant</strong><br><br>
                            I'm here to make your e-book creation journey smooth and professional. I can help you with:
                            <ul style="margin-top: 8px; padding-left: 20px; line-height: 1.8;">
                                <li>📚 <strong>Writing & Content</strong>: Titles, subtitles, chapter outlines, and proofreading</li>
                                <li>🎨 <strong>Design</strong>: Cover designs, color schemes, and typography suggestions</li>
                                <li>✍️ <strong>Editing</strong>: Grammar checks, readability improvements, and style refinement</li>
                                <li>📖 <strong>Marketing</strong>: Book descriptions, back cover text, and promotional copy</li>
                                <li>💡 <strong>Strategy</strong>: Publishing advice, formatting tips, and best practices</li>
                            </ul>
                            <br>💬 <em>I'm smart, conversational, and remember our conversation context. Just ask me anything!</em>
                        </div>
                    </div>
                </div>

                <div class="ai-quick-actions" id="ai-quick-actions">
                    <!-- Quick action buttons will be inserted here based on current page -->
                </div>

                <div class="ai-chat-input-container">
                    <textarea
                        class="ai-chat-input"
                        id="ai-chat-input"
                        placeholder="Ask me anything..."
                        rows="1"
                    ></textarea>
                    <button class="ai-send-btn" id="ai-send-btn">
                        <span>➤</span>
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(widget);

        // Add context-specific quick actions
        this.addQuickActions();
    }

    attachEventListeners() {
        const toggleBtn = document.getElementById('ai-toggle-btn');
        const closeBtn = document.getElementById('ai-close-btn');
        const sendBtn = document.getElementById('ai-send-btn');
        const input = document.getElementById('ai-chat-input');

        toggleBtn.addEventListener('click', () => this.togglePanel());
        closeBtn.addEventListener('click', () => this.closePanel());
        sendBtn.addEventListener('click', () => this.sendMessage());

        input.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize textarea
        input.addEventListener('input', function() {
            this.style.height = 'auto';
            this.style.height = Math.min(this.scrollHeight, 120) + 'px';
        });
    }

    showAIBadge() {
        // Show the AI ENABLED badge on the page
        const badge = document.getElementById('nav-ai-status');
        if (badge) {
            badge.style.display = 'inline-block';
        }
    }

    addQuickActions() {
        const container = document.getElementById('ai-quick-actions');
        if (!container) return;

        const currentPage = window.location.pathname;
        let actions = [];

        if (currentPage.includes('/covers') || currentPage === '/') {
            actions = [
                { text: '💡 Suggest Title', action: () => this.quickSuggestTitle() },
                { text: '🎨 Color Ideas', action: () => this.quickSuggestColors() },
                { text: '✨ Design Style', action: () => this.quickSuggestStyle() }
            ];
        } else if (currentPage.includes('/convert')) {
            actions = [
                { text: '📚 Suggest Title/Author', action: () => this.quickSuggestTitleAuthor() },
                { text: '📝 Generate Outline', action: () => this.quickGenerateOutline() },
                { text: '📖 Book Description', action: () => this.quickGenerateDescription() }
            ];
        } else if (currentPage.includes('/watermark')) {
            actions = [
                { text: '©️ Copyright Text', action: () => this.quickCopyrightText() },
                { text: '📝 Professional Disclaimer', action: () => this.quickDisclaimer() }
            ];
        } else {
            actions = [
                { text: '❓ How to use', action: () => this.quickHelp() },
                { text: '💡 Best Practices', action: () => this.quickBestPractices() }
            ];
        }

        container.innerHTML = actions.map(action =>
            `<button class="ai-quick-action-btn" data-action="${action.text}">${action.text}</button>`
        ).join('');

        // Attach click handlers
        container.querySelectorAll('.ai-quick-action-btn').forEach((btn, index) => {
            btn.addEventListener('click', actions[index].action);
        });
    }

    togglePanel() {
        this.isOpen = !this.isOpen;
        const panel = document.getElementById('ai-chat-panel');
        const btn = document.getElementById('ai-toggle-btn');

        if (this.isOpen) {
            panel.style.display = 'flex';
            btn.classList.add('active');
            setTimeout(() => {
                document.getElementById('ai-chat-input').focus();
            }, 100);
        } else {
            panel.style.display = 'none';
            btn.classList.remove('active');
        }
    }

    closePanel() {
        this.isOpen = false;
        document.getElementById('ai-chat-panel').style.display = 'none';
        document.getElementById('ai-toggle-btn').classList.remove('active');
    }

    async sendMessage() {
        const input = document.getElementById('ai-chat-input');
        const message = input.value.trim();

        if (!message) return;

        // Add user message to chat
        this.addMessage(message, 'user');
        input.value = '';
        input.style.height = 'auto';

        // Show typing indicator
        this.showTypingIndicator();

        try {
            // For now, use a generic chat endpoint (you may want to create one)
            // Or route to specific endpoints based on keywords
            const response = await this.routeMessage(message);

            this.hideTypingIndicator();
            this.addMessage(response, 'assistant');
        } catch (error) {
            this.hideTypingIndicator();
            this.addMessage('Sorry, I encountered an error. Please try again.', 'assistant');
        }
    }

    async routeMessage(message) {
        const lowerMessage = message.toLowerCase();

        // Store message in conversation history
        this.conversationHistory.push({ role: 'user', content: message, timestamp: Date.now() });

        // Extract context from message
        this.extractContext(message);

        // Intelligent routing based on keywords and context
        if (lowerMessage.includes('title') && (lowerMessage.includes('suggest') || lowerMessage.includes('generate') || lowerMessage.includes('book'))) {
            const topic = message.replace(/title|suggest|generate|book|about|for/gi, '').trim();
            if (topic.length < 3) {
                return 'Please provide more details about what the book is about. For example: "Suggest a title for a book about productivity"';
            }
            this.conversationContext.topic = topic;
            return await this.suggestTitle(topic);

        } else if (lowerMessage.includes('author') && (lowerMessage.includes('name') || lowerMessage.includes('suggest') || lowerMessage.includes('pen name'))) {
            return this.suggestAuthorName(message);

        } else if (lowerMessage.includes('color') || lowerMessage.includes('colour') || lowerMessage.includes('scheme')) {
            const genre = this.conversationContext.genre || 'general';
            return await this.suggestColors(genre);

        } else if (lowerMessage.includes('subtitle')) {
            if (this.conversationContext.title) {
                return await this.suggestSubtitle(this.conversationContext.title);
            }
            return 'Please provide the book title first, then I can suggest a subtitle. For example: "Suggest a subtitle for The Productivity Master"';

        } else if (lowerMessage.includes('outline') || lowerMessage.includes('chapter')) {
            const topic = this.conversationContext.topic || message.replace(/outline|chapter|generate|create|make|for/gi, '').trim();
            if (topic.length > 3) {
                return await this.generateOutline(topic);
            }
            return '📚 I can help create a chapter outline! What is your book topic?';

        } else if (lowerMessage.includes('description') || lowerMessage.includes('summary') || lowerMessage.includes('about') && lowerMessage.includes('book')) {
            return await this.generateBookDescription();

        } else if (lowerMessage.includes('proofread') || lowerMessage.includes('correct') || lowerMessage.includes('grammar')) {
            return '📝 I can help proofread! Please paste the text you\'d like me to review, or upload it to the Convert page for automatic checking.';

        } else if (lowerMessage.includes('cover') && lowerMessage.includes('design')) {
            return '🎨 For cover design:\n1. Go to the Covers page\n2. Fill in your title and author\n3. Click the AI buttons to get suggestions for:\n   • Creative titles\n   • Color schemes\n   • Design styles\n\nWant me to suggest colors now?';

        } else if (lowerMessage.includes('watermark') || lowerMessage.includes('copyright')) {
            return this.quickCopyrightText();

        } else if (lowerMessage.includes('help') || lowerMessage.includes('how')) {
            return this.getContextualHelp();

        } else if (lowerMessage.includes('genre') || lowerMessage.includes('category')) {
            return this.suggestGenre(message);

        } else if (lowerMessage.includes('marketing') || lowerMessage.includes('promote') || lowerMessage.includes('sell')) {
            return await this.generateMarketingCopy();

        } else {
            // Use general AI chat endpoint with conversation context
            return await this.sendToAI(message);
        }
    }

    extractContext(message) {
        // Extract key information from user messages
        const lowerMessage = message.toLowerCase();

        // Extract genre/category
        const genres = ['fiction', 'non-fiction', 'business', 'romance', 'thriller', 'mystery', 'fantasy', 'sci-fi', 'horror', 'biography', 'self-help', 'cooking', 'travel', 'history'];
        genres.forEach(genre => {
            if (lowerMessage.includes(genre)) {
                this.conversationContext.genre = genre;
            }
        });

        // Extract book title if mentioned
        const titleMatch = message.match(/"([^"]+)"|'([^']+)'/);
        if (titleMatch) {
            this.conversationContext.title = titleMatch[1] || titleMatch[2];
        }
    }

    async sendToAI(message) {
        try {
            // Build context-aware message
            let contextMessage = message;

            if (Object.keys(this.conversationContext).length > 0) {
                const context = [];
                if (this.conversationContext.topic) context.push(`Topic: ${this.conversationContext.topic}`);
                if (this.conversationContext.genre) context.push(`Genre: ${this.conversationContext.genre}`);
                if (this.conversationContext.title) context.push(`Book Title: ${this.conversationContext.title}`);

                if (context.length > 0) {
                    contextMessage = `Context: ${context.join(', ')}\n\nUser question: ${message}`;
                }
            }

            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: contextMessage,
                    history: this.conversationHistory.slice(-5) // Send last 5 messages for context
                })
            });

            const data = await response.json();
            if (data.success) {
                // Store assistant response in history
                this.conversationHistory.push({ role: 'assistant', content: data.response, timestamp: Date.now() });
                return data.response;
            } else {
                return this.getFallbackResponse(message);
            }
        } catch (error) {
            return this.getFallbackResponse(message);
        }
    }

    getFallbackResponse(message) {
        return `I understand you're asking about: "${message}"\n\n` +
            `I can help you with:\n` +
            `• 📚 Book titles: "Suggest a title about [topic]"\n` +
            `• 🎨 Cover design: "What colors work for [genre]?"\n` +
            `• ✍️ Writing help: "Generate chapter outline for [topic]"\n` +
            `• 📝 Text editing: "Proofread my text"\n` +
            `• 💡 Marketing: "Generate marketing copy"\n\n` +
            `Try asking one of these!`;
    }

    getContextualHelp() {
        const currentPage = window.location.pathname;

        if (currentPage.includes('/covers')) {
            return '🎨 **Covers Page Help:**\n\n' +
                   '1. Fill in your book title\n' +
                   '2. Click "AI Suggest Title" for creative ideas\n' +
                   '3. Click "AI Colors" for color scheme suggestions\n' +
                   '4. Choose your design style\n' +
                   '5. Click "Generate Cover"\n\n' +
                   'Ask me: "Suggest colors for a business book"';
        } else if (currentPage.includes('/convert')) {
            return '📄 **Convert Page Help:**\n\n' +
                   '1. Upload your document (MD, TXT, HTML, PDF, DOCX)\n' +
                   '2. Fill in title and author\n' +
                   '3. Select output formats (EPUB, PDF, HTML, DOCX)\n' +
                   '4. Click "Convert Document"\n\n' +
                   'Ask me: "Generate a chapter outline"';
        } else if (currentPage.includes('/watermark')) {
            return '💧 **Watermark Page Help:**\n\n' +
                   '1. Upload your document\n' +
                   '2. Enter watermark text or upload logo\n' +
                   '3. Adjust opacity and position\n' +
                   '4. Click "Apply Watermark"\n\n' +
                   'Ask me: "Generate copyright text"';
        } else {
            return '👋 **E-Book Maker Help:**\n\n' +
                   '• **Convert**: Transform documents to EPUB, PDF, etc.\n' +
                   '• **Covers**: Design professional book covers\n' +
                   '• **Watermark**: Protect your documents\n' +
                   '• **Settings**: Configure AI and dependencies\n\n' +
                   'What would you like to do?';
        }
    }

    async suggestTitle(topic = '') {
        if (!topic) {
            return 'Please provide a topic for the book title. For example: "Suggest a title for a book about productivity"';
        }

        try {
            const response = await fetch('/api/ai/suggest-title', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic: topic, genre: '' })
            });

            const data = await response.json();
            return data.success ? `📚 How about: "${data.title}"` : 'Sorry, I couldn\'t generate a title.';
        } catch {
            return 'Error generating title.';
        }
    }

    async suggestColors() {
        try {
            const response = await fetch('/api/ai/suggest-colors', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ genre: 'general', mood: 'professional' })
            });

            const data = await response.json();
            if (data.success && data.colors) {
                const colorText = typeof data.colors === 'string' ? data.colors : JSON.stringify(data.colors);
                return `🎨 Color Scheme Suggestion:\n\n${colorText}`;
            }
            return 'Sorry, I couldn\'t generate colors.';
        } catch (error) {
            console.error('Color suggestion error:', error);
            return 'Error generating colors.';
        }
    }

    // Quick action methods
    quickSuggestTitle() {
        this.addMessage('Can you suggest a creative book title?', 'user');
        this.addMessage('I\'d be happy to! What is your book about? Please tell me the topic or theme.', 'assistant');
    }

    quickSuggestColors() {
        this.addMessage('What colors would work well for a book cover?', 'user');
        this.showTypingIndicator();

        fetch('/api/ai/suggest-colors', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ genre: 'general', mood: 'professional' })
        })
        .then(res => res.json())
        .then(data => {
            this.hideTypingIndicator();
            if (data.success && data.colors) {
                // Ensure we're adding the string content, not the object
                const colorText = typeof data.colors === 'string' ? data.colors : JSON.stringify(data.colors);
                this.addMessage(`🎨 Color Scheme Suggestion:\n\n${colorText}`, 'assistant');
            } else {
                this.addMessage('Sorry, I couldn\'t generate colors right now.', 'assistant');
            }
        })
        .catch((error) => {
            this.hideTypingIndicator();
            console.error('Color generation error:', error);
            this.addMessage('Error generating colors. Please try again.', 'assistant');
        });
    }

    quickSuggestStyle() {
        this.addMessage('What design style should I use?', 'user');
        this.addMessage('Great question! Design styles vary by genre. What genre is your book? (e.g., fiction, non-fiction, business, romance, thriller, etc.)', 'assistant');
    }

    quickGenerateOutline() {
        this.addMessage('Help me create a chapter outline', 'user');
        this.addMessage('I can help with that! What is the main topic of your book?', 'assistant');
    }

    quickProofread() {
        this.addMessage('I need to proofread my text', 'user');
        this.addMessage('I can help proofread your text. Please paste the text you\'d like me to review in the "Convert" page, and I can check it for grammar, spelling, and clarity.', 'assistant');
    }

    quickImproveReadability() {
        this.addMessage('How can I improve readability?', 'user');
        this.addMessage('I can help improve your text\'s readability! Here are some tips:\n\n• Use shorter sentences\n• Break up long paragraphs\n• Use active voice\n• Avoid jargon\n• Add headings and subheadings\n\nWould you like me to analyze specific text?', 'assistant');
    }

    quickCopyrightText() {
        const year = new Date().getFullYear();
        return `Here are professional copyright text options:\n\n` +
               `1. © ${year} All Rights Reserved\n` +
               `2. © ${year} [Your Name]. Confidential.\n` +
               `3. © ${year} [Your Name/Company]. Do Not Copy.\n` +
               `4. Property of [Your Name]. © ${year}\n` +
               `5. CONFIDENTIAL - © ${year} - Do Not Distribute\n\n` +
               `Just replace [Your Name] with your actual name!`;
    }

    quickDisclaimer() {
        this.addMessage('Create a professional disclaimer', 'user');
        this.addMessage('Here\'s a professional disclaimer:\n\n"This document is proprietary and confidential. Unauthorized reproduction, distribution, or disclosure is strictly prohibited. © ' + new Date().getFullYear() + ' All Rights Reserved."', 'assistant');
    }

    quickHelp() {
        this.addMessage('How do I use this tool?', 'user');
        const currentPage = window.location.pathname;
        let help = 'Let me help you! ';

        if (currentPage.includes('/covers')) {
            help += 'On the Covers page, you can create professional book covers. Fill in the title, select colors, and choose a design style. I can suggest creative titles and color schemes!';
        } else if (currentPage.includes('/convert')) {
            help += 'On the Convert page, upload your document files and convert them to EPUB, PDF, DOCX, or HTML formats. I can help with proofreading and generating content!';
        } else if (currentPage.includes('/watermark')) {
            help += 'On the Watermark page, protect your documents by adding custom text or logo watermarks. I can suggest professional copyright text!';
        } else {
            help += 'Use the navigation menu to access different tools. I\'m here to help with AI-powered suggestions throughout the app!';
        }

        this.addMessage(help, 'assistant');
    }

    quickBestPractices() {
        this.addMessage('What are best practices?', 'user');
        this.addMessage('📚 Best Practices for E-Book Creation:\n\n1. **Quality Content**: Proofread thoroughly\n2. **Professional Cover**: Eye-catching design\n3. **Proper Formatting**: Use headings and structure\n4. **Metadata**: Add accurate title and author info\n5. **Legal Protection**: Use watermarks for drafts\n6. **Test Formats**: Preview on multiple devices', 'assistant');
    }

    // NEW SMART METHODS

    quickSuggestTitleAuthor() {
        this.addMessage('Help me with title and author name', 'user');
        this.addMessage('I\'d love to help! Let\'s start with the title. What is your book about? (e.g., "A guide to productivity for entrepreneurs")', 'assistant');
    }

    async quickGenerateDescription() {
        this.addMessage('Generate a book description', 'user');

        if (this.conversationContext.title || this.conversationContext.topic) {
            this.showTypingIndicator();
            const response = await this.generateBookDescription();
            this.hideTypingIndicator();
            this.addMessage(response, 'assistant');
        } else {
            this.addMessage('I\'d be happy to create a book description! First, tell me: What is your book about?', 'assistant');
        }
    }

    suggestAuthorName(message) {
        const genres = {
            'romance': ['Emma Sterling', 'Juliet Rivers', 'Victoria Knight', 'Scarlett Monroe'],
            'thriller': ['Alex Hunter', 'Jack Stone', 'Morgan Black', 'Ryan Cross'],
            'fantasy': ['Aria Moonweaver', 'Thorne Shadowblade', 'Elara Starwind', 'Kai Dragonheart'],
            'business': ['J.M. Peterson', 'Sarah Mitchell', 'David Clarke', 'Michael Reynolds'],
            'sci-fi': ['Nova Sterling', 'Zane Carter', 'Lyra Phoenix', 'Rex Quantum'],
            'mystery': ['Detective Morgan Chase', 'Catherine Holmes', 'Maxwell Grey', 'Olivia Raven']
        };

        const genre = this.conversationContext.genre || 'general';
        const suggestions = genres[genre] || ['A. J. Thompson', 'M. L. Anderson', 'S. K. Williams', 'R. D. Cooper'];

        return `Here are some author name suggestions for ${genre} books:\n\n` +
               suggestions.map((name, i) => `${i + 1}. ${name}`).join('\n') +
               `\n\nTip: Consider using initials for a professional look, or a memorable full name that matches your genre!`;
    }

    async suggestSubtitle(title) {
        try {
            const response = await fetch('/api/ai/suggest-subtitle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    title: title,
                    genre: this.conversationContext.genre || 'general'
                })
            });

            const data = await response.json();
            if (data.success && data.subtitle) {
                return `📖 Perfect subtitle for "${title}":\n\n"${data.subtitle}"`;
            }
        } catch {}

        // Fallback suggestions
        return `Here are subtitle ideas for "${title}":\n\n` +
               `• A Comprehensive Guide to [Topic]\n` +
               `• Mastering [Key Skill] in [Timeframe]\n` +
               `• Discover the Secrets of [Main Benefit]\n` +
               `• Transform Your [Area] Forever`;
    }

    async generateOutline(topic) {
        try {
            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `Generate a detailed chapter outline for a book about: ${topic}. Include 8-10 chapters with brief descriptions.`
                })
            });

            const data = await response.json();
            if (data.success) {
                this.conversationContext.outline = data.response;
                return `📚 Here's a chapter outline for your book about ${topic}:\n\n${data.response}`;
            }
        } catch {}

        return `📚 Here's a suggested outline for "${topic}":\n\n` +
               `**Chapter 1**: Introduction - Setting the Stage\n` +
               `**Chapter 2**: The Foundation - Core Concepts\n` +
               `**Chapter 3**: Getting Started - First Steps\n` +
               `**Chapter 4**: Advanced Techniques\n` +
               `**Chapter 5**: Common Challenges\n` +
               `**Chapter 6**: Expert Strategies\n` +
               `**Chapter 7**: Real-World Applications\n` +
               `**Chapter 8**: Putting It All Together\n` +
               `**Chapter 9**: Resources and Next Steps\n` +
               `**Chapter 10**: Conclusion - Your Path Forward`;
    }

    async generateBookDescription() {
        const title = this.conversationContext.title || 'Your Book';
        const topic = this.conversationContext.topic || 'this topic';
        const genre = this.conversationContext.genre || 'general';

        try {
            const response = await fetch('/api/ai/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: `Write a compelling book description for a ${genre} book titled "${title}" about ${topic}. Make it engaging and professional, suitable for back cover or Amazon listing.`
                })
            });

            const data = await response.json();
            if (data.success) {
                return `📖 Here's your book description:\n\n${data.response}\n\n✨ Feel free to customize it!`;
            }
        } catch {}

        return `📖 Here's a book description template:\n\n` +
               `"${title}" is your comprehensive guide to mastering ${topic}. Whether you're a beginner or experienced professional, this book provides practical insights and actionable strategies.\n\n` +
               `Inside, you'll discover:\n` +
               `• Step-by-step guidance\n` +
               `• Real-world examples\n` +
               `• Expert tips and techniques\n` +
               `• Common pitfalls to avoid\n\n` +
               `Transform your understanding of ${topic} and achieve the results you've been looking for!`;
    }

    suggestGenre(message) {
        return `📚 I can help identify the genre! Based on your book, here are common genres:\n\n` +
               `**Fiction**: Romance, Thriller, Mystery, Fantasy, Sci-Fi, Horror, Literary Fiction\n` +
               `**Non-Fiction**: Business, Self-Help, Biography, History, Science, How-To, Travel\n\n` +
               `Which genre best fits your book? This helps me provide better suggestions!`;
    }

    async generateMarketingCopy() {
        const title = this.conversationContext.title || 'your book';
        const topic = this.conversationContext.topic || 'this topic';

        return `📢 Marketing Copy for "${title}":\n\n` +
               `**Headline**: Discover the Ultimate Guide to ${topic}\n\n` +
               `**Hook**: Are you ready to transform the way you approach ${topic}?\n\n` +
               `**Benefits**:\n` +
               `✓ Learn proven strategies that work\n` +
               `✓ Get results faster than ever before\n` +
               `✓ Join thousands of satisfied readers\n\n` +
               `**Call-to-Action**: Get your copy today and start your journey!\n\n` +
               `**Social Media Post**: "Just released! ${title} - Your guide to mastering ${topic}. Available now! #newbook #${topic.replace(/\s+/g, '')}"\n\n` +
               `Feel free to customize this for your needs!`;
    }

    addMessage(content, sender) {
        const messagesContainer = document.getElementById('ai-chat-messages');
        const messageDiv = document.createElement('div');
        messageDiv.className = `ai-message ai-message-${sender}`;

        messageDiv.innerHTML = `
            <div class="ai-message-content">${content.replace(/\n/g, '<br>')}</div>
        `;

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    showTypingIndicator() {
        const messagesContainer = document.getElementById('ai-chat-messages');
        const indicator = document.createElement('div');
        indicator.id = 'ai-typing-indicator';
        indicator.className = 'ai-message ai-message-assistant';
        indicator.innerHTML = `
            <div class="ai-message-content">
                <div class="ai-typing-dots">
                    <span></span><span></span><span></span>
                </div>
            </div>
        `;
        messagesContainer.appendChild(indicator);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    hideTypingIndicator() {
        const indicator = document.getElementById('ai-typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }
}

// Initialize AI Assistant when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.aiAssistant = new AIAssistant();
    });
} else {
    window.aiAssistant = new AIAssistant();
}
