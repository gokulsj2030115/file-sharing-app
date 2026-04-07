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
        ? `Are you sure you want to delete the folder "${fullPath}"? This will recursively delete ALL files inside it.` 
        : `Are you sure you want to delete "${fullPath}"?`;

    if (confirm(message)) {
        if (isFolder) {
            const form = document.getElementById('deleteFolderForm');
            document.getElementById('folderPrefixToDelete').value = fullPath;
            form.submit();
        } else {
            const form = document.getElementById('deleteFileForm');
            form.action = `/delete/${encodeURIComponent(fullPath)}?prefix=${encodeURIComponent(getCurrentPrefix())}`;
            form.submit();
        }
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
