document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('upload_form');
    const submitBtn = document.getElementById('submit_btn');
    const spinner = document.getElementById('spinner');
    const messageDiv = document.getElementById('message');
    const pdfLinks = document.getElementById('pdf_links');
    const blogLinks = document.getElementById('blog_links');
    const pdfLinksError = document.getElementById('pdf_links_error');
    const blogLinksError = document.getElementById('blog_links_error');

    const urlRegex = /^https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/;
    const pdfRegex = /\.pdf/i;

    function getUniqueUrls(text) {
        return [...new Set(text.split(/[\n,]+/).map(url => url.trim()).filter(url => url))];
    }

    function validateTextarea(textarea, errorElement, isPdfArea = false) {
        const value = textarea.value.trim();
        
        // Convert newlines to commas
        if (value.includes('\n')) {
            textarea.value = value.replace(/\n/g, ',');
        }

        const urls = getUniqueUrls(value);
        if (!urls.length) {
            textarea.classList.remove('error');
            errorElement.textContent = '';
            return true;
        }

        // Check for duplicate URLs between PDF and blog inputs
        const otherTextarea = isPdfArea ? blogLinks : pdfLinks;
        const otherUrls = getUniqueUrls(otherTextarea.value);
        const duplicates = urls.filter(url => otherUrls.includes(url));
        if (duplicates.length) {
            textarea.classList.add('error');
            errorElement.textContent = 'URL already exists in other input field';
            return false;
        }

        // Validate URLs
        const invalidUrls = urls.filter(url => !urlRegex.test(url));
        if (invalidUrls.length) {
            textarea.classList.add('error');
            errorElement.textContent = 'Invalid URL format';
            return false;
        }

        // For PDF area, ensure all URLs contain .pdf
        if (isPdfArea) {
            const nonPdfUrls = urls.filter(url => !pdfRegex.test(url));
            if (nonPdfUrls.length) {
                textarea.classList.add('error');
                errorElement.textContent = 'URLs must contain .pdf';
                return false;
            }
        } else {
            // For blog area, ensure no PDF URLs
            const pdfUrls = urls.filter(url => pdfRegex.test(url));
            if (pdfUrls.length) {
                textarea.classList.add('error');
                errorElement.textContent = 'PDF links not allowed here';
                return false;
            }
        }

        // Check for duplicates within the same textarea
        if (urls.length !== new Set(urls).size) {
            textarea.classList.add('error');
            errorElement.textContent = 'Duplicate URLs not allowed';
            return false;
        }

        textarea.classList.remove('error');
        errorElement.textContent = '';
        return true;
    }

    function showMessage(text, type = 'success') {
        messageDiv.className = `message ${type}`;
        messageDiv.style.display = 'block';
        messageDiv.textContent = text;
        messageDiv.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }

    // Real-time validation
    pdfLinks.addEventListener('input', () => {
        submitBtn.disabled = !validateTextarea(pdfLinks, pdfLinksError, true);
    });
    
    blogLinks.addEventListener('input', () => {
        submitBtn.disabled = !validateTextarea(blogLinks, blogLinksError, false);
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        pdfLinksError.textContent = '';
        blogLinksError.textContent = '';
        pdfLinks.classList.remove('error');
        blogLinks.classList.remove('error');
        messageDiv.style.display = 'none';

        const botName = document.getElementById('bot_name').value;
        if (!botName) {
            showMessage('Please select a bot', 'error');
            return;
        }

        const isPdfValid = validateTextarea(pdfLinks, pdfLinksError, true);
        const isBlogValid = validateTextarea(blogLinks, blogLinksError, false);

        if (!isPdfValid || !isBlogValid) {
            submitBtn.disabled = true;
            return;
        }

        if (!pdfLinks.value.trim() && !blogLinks.value.trim()) {
            showMessage('Please provide at least one URL', 'error');
            return;
        }

        submitBtn.disabled = true;
        spinner.style.display = 'inline-block';

        try {
            const formData = new FormData(form);
            const response = await fetch('/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();
            
            if (response.ok && result.status === 'success') {
                showMessage('Upload successful', 'success');
                pdfLinks.value = '';
                blogLinks.value = '';
            } else {
                showMessage(result.message || 'Upload failed', 'error');
            }
        } catch (error) {
            showMessage('Network error', 'error');
            console.error('Error:', error);
        } finally {
            submitBtn.disabled = false;
            spinner.style.display = 'none';
        }
    });
});
