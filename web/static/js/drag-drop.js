/**
 * Drag & Drop File Upload System
 * Universal drag-and-drop functionality for all file inputs
 */

class DragDropUpload {
    constructor(options = {}) {
        this.options = {
            acceptedTypes: options.acceptedTypes || [],
            maxSize: options.maxSize || 100 * 1024 * 1024, // 100MB default
            multiple: options.multiple !== undefined ? options.multiple : true,
            onDrop: options.onDrop || null,
            onError: options.onError || null,
            ...options
        };
        this.processing = false; // Flag to prevent duplicate processing
    }

    /**
     * Initialize drag-drop for a specific file input
     * @param {string|Element} inputElement - Input element or selector
     * @param {string|Element} dropZone - Drop zone element or selector
     */
    init(inputElement, dropZone) {
        const input = typeof inputElement === 'string' ? document.querySelector(inputElement) : inputElement;
        const zone = typeof dropZone === 'string' ? document.querySelector(dropZone) : dropZone;

        if (!input || !zone) {
            console.error('DragDrop: Input or drop zone not found');
            return;
        }

        // Store reference
        zone._dragDropInput = input;

        // Setup events
        this.setupDragEvents(zone);
        this.setupClickEvent(zone, input);
        this.setupInputChange(input);
    }

    setupDragEvents(zone) {
        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            zone.addEventListener(eventName, this.preventDefaults, false);
            document.body.addEventListener(eventName, this.preventDefaults, false);
        });

        // Highlight drop zone when item is dragged over it
        ['dragenter', 'dragover'].forEach(eventName => {
            zone.addEventListener(eventName, () => this.highlight(zone), false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            zone.addEventListener(eventName, () => this.unhighlight(zone), false);
        });

        // Handle dropped files
        zone.addEventListener('drop', (e) => this.handleDrop(e, zone), false);
    }

    setupClickEvent(zone, input) {
        zone.addEventListener('click', (e) => {
            if (e.target.tagName !== 'BUTTON') {
                input.click();
            }
        });
    }

    setupInputChange(input) {
        input.addEventListener('change', (e) => {
            // Prevent duplicate processing
            if (this.processing) {
                return;
            }

            if (e.target.files.length > 0) {
                this.handleFiles(e.target.files, input);
            }
        });
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    highlight(zone) {
        zone.classList.add('drag-over');
    }

    unhighlight(zone) {
        zone.classList.remove('drag-over');
    }

    handleDrop(e, zone) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            const input = zone._dragDropInput;

            // Set files to input - this will automatically trigger 'change' event
            // Don't manually dispatch change to avoid duplicate handling
            try {
                input.files = files;
                // The browser automatically triggers 'change' when input.files is set
                // Our setupInputChange listener will handle it
            } catch (error) {
                // Fallback: If we can't set input.files, handle files directly
                console.error('Error setting files:', error);
                this.handleFiles(files, input);
            }
        }
    }

    handleFiles(files, input) {
        // Prevent duplicate processing
        if (this.processing) {
            return;
        }

        this.processing = true;
        const fileArray = Array.from(files);

        // Validate files
        const validation = this.validateFiles(fileArray);

        if (!validation.valid) {
            if (this.options.onError) {
                this.options.onError(validation.errors);
            } else {
                toastError(validation.errors.join('\n'));
            }
            this.processing = false;
            return;
        }

        // Show success message
        const fileNames = fileArray.map(f => f.name).join(', ');
        toastSuccess(`File${fileArray.length > 1 ? 's' : ''} selected: ${fileNames}`);

        // Callback
        if (this.options.onDrop) {
            this.options.onDrop(fileArray, input);
        }

        // Update drop zone text
        const zone = this.findDropZone(input);
        if (zone) {
            const textEl = zone.querySelector('.drop-zone-text');
            if (textEl) {
                textEl.textContent = `${fileArray.length} file${fileArray.length > 1 ? 's' : ''} selected`;
            }
        }

        // Reset processing flag after a short delay
        setTimeout(() => {
            this.processing = false;
        }, 100);
    }

    findDropZone(input) {
        // Find the drop zone associated with this input
        const zones = document.querySelectorAll('.drop-zone, .file-drop-zone');
        for (let zone of zones) {
            if (zone._dragDropInput === input) {
                return zone;
            }
        }
        return null;
    }

    validateFiles(files) {
        const errors = [];

        // Check count
        if (!this.options.multiple && files.length > 1) {
            errors.push('Only one file allowed');
        }

        // Check each file
        files.forEach(file => {
            // Check size
            if (file.size > this.options.maxSize) {
                errors.push(`${file.name} is too large (max ${this.formatBytes(this.options.maxSize)})`);
            }

            // Check type
            if (this.options.acceptedTypes.length > 0) {
                const ext = file.name.split('.').pop().toLowerCase();
                const mimeType = file.type.toLowerCase();

                const isValidExt = this.options.acceptedTypes.some(type =>
                    type.toLowerCase() === `.${ext}` || type.toLowerCase() === ext
                );

                const isValidMime = this.options.acceptedTypes.some(type =>
                    mimeType.includes(type.toLowerCase())
                );

                if (!isValidExt && !isValidMime) {
                    errors.push(`${file.name} has invalid file type. Accepted: ${this.options.acceptedTypes.join(', ')}`);
                }
            }
        });

        return {
            valid: errors.length === 0,
            errors
        };
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
}

/**
 * Auto-initialize drag-drop for all drop zones on page load
 */
function initializeAllDropZones() {
    // Document conversion drop zone - DISABLED (handled by inline handlers in convert.html)
    // const docInput = document.getElementById('file-input');
    // const docZone = document.getElementById('file-drop-zone');
    // if (docInput && docZone) {
    //     new DragDropUpload({
    //         acceptedTypes: ['md', 'markdown', 'txt', 'html', 'htm', 'pdf', 'docx', 'epub', 'odt', 'rtf', 'tex', 'latex', 'rst', 'org'],
    //         multiple: true  // Allow multiple files for conversion
    //     }).init(docInput, docZone);
    // }

    // COVERS PAGE - ALL DISABLED: covers.html has its own complete inline handlers for all inputs
    // Enabling these causes conflicts with inline handlers and processing flag blocks them

    // Cover background image upload (Create Cover tab) - DISABLED
    // const createBgInput = document.getElementById('create-bg-input');
    // const createBgZone = document.getElementById('create-bg-drop-zone');
    // if (createBgInput && createBgZone) {
    //     new DragDropUpload({
    //         acceptedTypes: ['png', 'jpg', 'jpeg', 'pdf', 'image/'],
    //         multiple: false
    //     }).init(createBgInput, createBgZone);
    // }

    // Cover conversion (Convert Existing Cover tab) - DISABLED
    // const coverInput = document.getElementById('cover-input');
    // const coverZone = document.getElementById('cover-drop-zone');
    // if (coverInput && coverZone) {
    //     new DragDropUpload({
    //         acceptedTypes: ['png', 'jpg', 'jpeg', 'pdf', 'image/'],
    //         multiple: false
    //     }).init(coverInput, coverZone);
    // }

    // WATERMARK PAGE - ALL DISABLED: watermark.html has its own complete inline handlers
    // Enabling these causes conflicts with inline handlers and processing flag blocks them

    // Watermark document - DISABLED
    // const watermarkDocInput = document.getElementById('doc-input');
    // const watermarkDocZone = document.getElementById('doc-drop-zone');
    // if (watermarkDocInput && watermarkDocZone) {
    //     new DragDropUpload({
    //         acceptedTypes: ['pdf', 'docx', 'epub'],
    //         multiple: false
    //     }).init(watermarkDocInput, watermarkDocZone);
    // }

    // Watermark logo image - DISABLED
    // const logoInput = document.getElementById('logo-input');
    // const logoZone = document.getElementById('logo-drop-zone');
    // if (logoInput && logoZone) {
    //     new DragDropUpload({
    //         acceptedTypes: ['png', 'jpg', 'jpeg', 'image/'],
    //         multiple: false
    //     }).init(logoInput, logoZone);
    // }
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeAllDropZones);
} else {
    initializeAllDropZones();
}

// Export for use in other scripts
window.DragDropUpload = DragDropUpload;
