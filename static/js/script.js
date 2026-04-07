// Modal Handling
function openUploadModal() {
    document.getElementById('uploadModal').style.display = 'flex';
}

function openFolderModal() {
    document.getElementById('folderModal').style.display = 'flex';
}

function closeModal(modalId) {
    document.getElementById(modalId).style.display = 'none';
}

// Close modals when clicking outside
window.onclick = function(event) {
    if (event.target.classList.contains('modal')) {
        event.target.style.display = 'none';
    }
}

// Search Filtering (Client-side)
function filterFiles() {
    const input = document.getElementById('searchInput');
    const filter = input.value.toLowerCase();
    const fileList = document.getElementById('fileList');
    const rows = fileList.getElementsByClassName('file-row');

    for (let i = 0; i < rows.length; i++) {
        const nameAttr = rows[i].getAttribute('data-name');
        if (nameAttr && nameAttr.includes(filter)) {
            rows[i].style.display = "";
        } else {
            rows[i].style.display = "none";
        }
    }
}

// Share Logic
async function shareFile(fullPath) {
    try {
        const response = await fetch(`/share/${encodeURIComponent(fullPath)}`);
        const data = await response.json();
        if (data.success) {
            copyToClipboard(data.url);
            alert('Presigned URL copied to clipboard!\n(Expires in 1 hour)');
        } else {
            alert('Failed to generate share link: ' + data.error);
        }
    } catch (err) {
        console.error(err);
        alert('An unexpected error occurred during link generation.');
    }
}

function copyToClipboard(text) {
    const tempInput = document.createElement("input");
    tempInput.value = text;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand("copy");
    document.body.removeChild(tempInput);
}

// Delete Logic
function confirmDelete(fullPath, isFolder) {
    const message = isFolder 
        ? `Move folder "${fullPath}" and all its contents to Trash?` 
        : `Move "${fullPath}" to Trash?`;

    if (confirm(message)) {
        const form = document.getElementById('deleteFileForm');
        form.action = `/delete/${encodeURIComponent(fullPath)}?prefix=${encodeURIComponent(getCurrentPrefix())}`;
        form.submit();
    }
}

function restoreFile(fullPath) {
    if (confirm(`Restore "${fullPath}" to its original location?`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/restore/${encodeURIComponent(fullPath)}`;
        document.body.appendChild(form);
        form.submit();
    }
}

function confirmPermanentDelete(fullPath) {
    if (confirm(`PERMANENTLY DELETE "${fullPath}"? This cannot be undone.`)) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = `/permanent-delete/${encodeURIComponent(fullPath)}`;
        document.body.appendChild(form);
        form.submit();
    }
}

function getCurrentPrefix() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('prefix') || '';
}

// Auto-hide Flash Messages after 5 seconds
window.addEventListener('DOMContentLoaded', () => {
    const flashes = document.querySelectorAll('.flash');
    flashes.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 500);
        }, 5000);
    });
});
