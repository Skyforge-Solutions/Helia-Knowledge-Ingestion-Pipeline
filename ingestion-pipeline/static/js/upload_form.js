document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('uploadForm');
    const submitBtn = document.getElementById('submitBtn');
    const spinner = document.getElementById('spinner');
    const messageDiv = document.getElementById('message');
    const pdfLinks = document.getElementById('pdf_links');
    const blogLinks = document.getElementById('blog_links');
    const pdfLinksError = document.getElementById('pdf_links_error');
    const blogLinksError = document.getElementById('blog_links_error');

    // URL validation regex
    const urlRegex = /^https?:\/\/[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/;

    function validateUrls(text) {
        if (!text.trim()) return true; // Empty input is valid
        const urls = text.split(',').map(url => url.trim());
        return urls.every(url => urlRegex.test(url));
    }

    function validateTextarea(textarea, errorElement) {
        const value = textarea.value.trim();
        const urls = value.split(',').map(url => url.trim()).filter(url => url !== '');
        
        // Remove any newlines
        if (value.includes('\n')) {
            textarea.value = value.replace(/\n/g, ',');
        }

        // Check if all URLs are valid
        if (urls.length > 0 && !validateUrls(value)) {
            textarea.classList.add('error');
            errorElement.textContent = 'Please enter valid, comma-separated URLs starting with http:// or https://';
            return false;
        }

        textarea.classList.remove('error');
        errorElement.textContent = '';
        return true;
    }

    function showMessage(text, type, skippedUrls = []) {
        messageDiv.style.display = 'block';
        messageDiv.style.backgroundColor = type === 'error' ? '#fee2e2' : '#dcfce7';
        messageDiv.style.color = type === 'error' ? '#991b1b' : '#166534';
        
        let messageContent = `<p>${text}</p>`;
        
        if (skippedUrls.length > 0) {
            messageContent += `<ul>`;
            skippedUrls.forEach(url => {
                messageContent += `<li><a href="${url}" target="_blank">${url}</a></li>`;
            });
            messageContent += `</ul>`;
        }
        
        messageDiv.innerHTML = messageContent;
    }

    // Real-time validation
    pdfLinks.addEventListener('input', () => validateTextarea(pdfLinks, pdfLinksError));
    blogLinks.addEventListener('input', () => validateTextarea(blogLinks, blogLinksError));

    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        // Reset error states
        pdfLinksError.textContent = '';
        blogLinksError.textContent = '';
        pdfLinks.classList.remove('error');
        blogLinks.classList.remove('error');
        messageDiv.style.display = 'none';

        // Validate bot selection
        const botName = document.getElementById('bot_name').value;
        if (!botName) {
            showMessage('Please select a bot', 'error');
            return;
        }

        // Validate URLs
        const isPdfValid = validateTextarea(pdfLinks, pdfLinksError);
        const isBlogValid = validateTextarea(blogLinks, blogLinksError);

        if (!isPdfValid || !isBlogValid) {
            return;
        }

        // Check if at least one field has content
        if (!pdfLinks.value.trim() && !blogLinks.value.trim()) {
            showMessage('Please provide at least one PDF or blog link', 'error');
            return;
        }

        // Show loading state
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
                showMessage(result.message, 'success', result.skipped_urls);
                if (result.new_count > 0) {
                    form.reset();
                }
            } else {
                showMessage(result.message || 'Upload failed. Please try again.', 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('An error occurred. Please try again.', 'error');
        } finally {
            submitBtn.disabled = false;
            spinner.style.display = 'none';
        }
    });
});
