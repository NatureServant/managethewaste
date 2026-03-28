const searchBtn = document.getElementById('analyzeButton');
const uploadImg = document.getElementById('imageUpload');
const resultArea = document.getElementById('result');

searchBtn.addEventListener('click', async () => {
    resultArea.style.display = 'block';
    if (!uploadImg.files.length) {
        resultArea.innerText = 'Please choose an image first.';
        return;
    }

    const file = uploadImg.files[0];
    const formData = new FormData();
    formData.append('image', file);

    resultArea.innerText = 'Analyzing image, please wait...';

    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            body: formData,
        });

        const text = await response.text();

        if (!response.ok) {
            try {
                const jsonErr = JSON.parse(text);
                throw new Error(jsonErr.error || 'Server error');
            } catch (parseErr) {
                throw new Error('Server error (non-JSON response): ' + text.slice(0, 300));
            }
        }

        let data;
        try {
            data = JSON.parse(text);
        } catch (parseError) {
            throw new Error('Failed to parse JSON from server: ' + text.slice(0, 300));
        }

        if (!data || typeof data.result !== 'string') {
            throw new Error('Unexpected response payload: ' + JSON.stringify(data));
        }

        resultArea.innerHTML = formatQuotedText(data.result);
    } catch (error) {
        resultArea.innerText = 'Error: ' + error.message;
    }
});

function escapeHtml(text) {
    return text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        // .replace(/"/g, '&quot;')
        // .replace(/'/g, '&#39;');
}

function formatQuotedText(text) {
    if (!text) return '';

    // escape special chars to avoid accidental HTML injection
    let escaped = escapeHtml(text);

    // Strip regular quotes around content (prioritize quotes-only contexts)
    escaped = escaped.replace(/&quot;([^&]+?)&quot;/g, '$1');
    escaped = escaped.replace(/&#39;([^&#]+?)&#39;/g, '$1');

    // Heading-style: **Heading**: becomes larger heading text (without retained colon)
    escaped = escaped.replace(/\*\*([^*]+?)\*\*\s*:\s*/g, (m, p1) => {
        return `<div class="result-heading">${p1.trim()}</div>`;
    });

    // Inline bold style for **text** (less strong style)
    escaped = escaped.replace(/\*\*([^*]+?)\*\*/g, (m, p1) => {
        return `<span class="result-bold">${p1.trim()}</span>`;
    });

    // Highlight 'bin' and phrases ending with bin (e.g. 'compost bin', 'plastic recycling bin') in red
    escaped = escaped.replace(/\b([a-zA-Z]+(?:\s+[a-zA-Z]+){0,2}\s+bin)\b/gi, (m) => {
        return `<span class="bin-word">${m}</span>`;
    });

    // Preserve line breaks
    return escaped.replace(/\n/g, '<br>');
}

