/**
 * Cover Templates Gallery
 * Loads and displays professional cover templates
 */

let allTemplates = [];
let selectedTemplate = null;

// Load templates on page load
async function loadCoverTemplates() {
    try {
        const response = await fetch('/api/cover-templates');
        const data = await response.json();

        if (data.success) {
            allTemplates = data.templates;
            displayTemplates(allTemplates);
            setupTemplateFilters();
            setupTemplateToggle();
        } else {
            console.error('Failed to load templates:', data.error);
            document.getElementById('template-gallery').innerHTML =
                '<div class="loading-templates" style="color: #ef4444;">Failed to load templates</div>';
        }
    } catch (error) {
        console.error('Error loading templates:', error);
        document.getElementById('template-gallery').innerHTML =
            '<div class="loading-templates" style="color: #ef4444;">Error loading templates</div>';
    }
}

// Display templates in the gallery
function displayTemplates(templates) {
    const gallery = document.getElementById('template-gallery');

    if (templates.length === 0) {
        gallery.innerHTML = '<div class="loading-templates">No templates found</div>';
        return;
    }

    gallery.innerHTML = templates.map(template => `
        <div class="template-card" data-template-id="${template.id}" data-category="${template.category}">
            <div class="template-preview" style="background: ${template.colors.background};">
                <div class="template-preview-placeholder">
                    <div class="title" style="color: ${template.colors.title};">Your Title</div>
                    <div class="subtitle" style="color: ${template.colors.subtitle};">Your Subtitle</div>
                </div>
            </div>
            <div class="template-info">
                <div class="template-name">${template.name}</div>
                <div class="template-category">${template.category}</div>
                <div class="template-description">${template.description}</div>
            </div>
        </div>
    `).join('');

    // Add click handlers to template cards
    document.querySelectorAll('.template-card').forEach(card => {
        card.addEventListener('click', () => {
            const templateId = card.dataset.templateId;
            selectTemplate(templateId);
        });
    });
}

// Select a template and apply it to the form
function selectTemplate(templateId) {
    const template = allTemplates.find(t => t.id === templateId);
    if (!template) return;

    selectedTemplate = template;

    // Update UI
    document.querySelectorAll('.template-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelector(`[data-template-id="${templateId}"]`).classList.add('selected');

    // Apply template to form
    applyTemplateToForm(template);

    // Show success toast
    if (window.Toast) {
        Toast.success(`Template "${template.name}" applied!`, 3000);
    }

    // Scroll to form
    document.getElementById('create-cover-form').scrollIntoView({
        behavior: 'smooth',
        block: 'nearest'
    });
}

// Apply template colors and style to form
function applyTemplateToForm(template) {
    // Extract colors from background
    const colors = template.colors;

    // If background is gradient, extract first color
    if (colors.background.startsWith('linear-gradient')) {
        const gradientColors = extractGradientColors(colors.background);
        if (gradientColors.length >= 2) {
            document.getElementById('primary-color').value = gradientColors[0];
            document.getElementById('secondary-color').value = gradientColors[1];
        }
    } else {
        // Solid color background
        document.getElementById('primary-color').value = colors.background;
        document.getElementById('secondary-color').value = colors.accent;
    }

    // Set style dropdown based on template
    const styleSelect = document.getElementById('style');
    if (colors.background.startsWith('linear-gradient')) {
        styleSelect.value = 'gradient';
    } else if (template.category === 'minimal') {
        styleSelect.value = 'minimalist';
    } else {
        styleSelect.value = 'solid';
    }
}

// Extract hex colors from gradient string
function extractGradientColors(gradientStr) {
    const hexMatches = gradientStr.match(/#[0-9a-fA-F]{6}/g);
    return hexMatches || [];
}

// Setup filter buttons
function setupTemplateFilters() {
    const filterButtons = document.querySelectorAll('.template-filter-btn');

    filterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Update active button
            filterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Filter templates
            const category = btn.dataset.category;
            if (category === 'all') {
                displayTemplates(allTemplates);
            } else {
                const filtered = allTemplates.filter(t =>
                    t.category === category ||
                    t.name.toLowerCase().includes(category) ||
                    t.description.toLowerCase().includes(category)
                );
                displayTemplates(filtered);
            }
        });
    });
}

// Setup template gallery toggle
function setupTemplateToggle() {
    const toggleBtn = document.getElementById('hide-templates-btn');
    const gallerySection = document.querySelector('.template-gallery-section');

    toggleBtn.addEventListener('click', () => {
        if (gallerySection.classList.contains('collapsed')) {
            gallerySection.classList.remove('collapsed');
            toggleBtn.textContent = '▲ Hide Templates';
        } else {
            gallerySection.classList.add('collapsed');
            toggleBtn.textContent = '▼ Show Templates';
        }
    });
}

// Initialize templates when page loads
if (document.getElementById('template-gallery')) {
    loadCoverTemplates();
}
