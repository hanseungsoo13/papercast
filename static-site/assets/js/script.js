// PaperCast JavaScript

// Global state
let splitViewActive = false;
let currentPaperIndex = -1;

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializePage();
    setupEventListeners();
    setupAccessibility();
});

function initializePage() {
    console.log('PaperCast initialized');
    
    // Check if we're on an episode page
    if (typeof papersData !== 'undefined') {
        console.log(`Loaded ${papersData.length} papers`);
    }
}

function setupEventListeners() {
    // Split View toggle button
    const splitViewToggle = document.getElementById('split-view-toggle');
    if (splitViewToggle) {
        splitViewToggle.addEventListener('click', () => toggleSplitView(0));
    }
    
    // Close Split View button
    const closeSplitView = document.getElementById('close-split-view');
    if (closeSplitView) {
        closeSplitView.addEventListener('click', closeSplitViewMode);
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', handleKeyboardShortcuts);
}

function setupAccessibility() {
    // Add ARIA labels dynamically
    const audioElements = document.querySelectorAll('audio');
    audioElements.forEach(audio => {
        if (!audio.getAttribute('aria-label')) {
            audio.setAttribute('aria-label', '팟캐스트 오디오 플레이어');
        }
    });
}

function handleKeyboardShortcuts(event) {
    // Escape: Close split view
    if (event.key === 'Escape' && splitViewActive) {
        closeSplitViewMode();
    }
    
    // Ctrl+S: Toggle split view
    if (event.ctrlKey && event.key === 's') {
        event.preventDefault();
        if (currentPaperIndex >= 0) {
            toggleSplitView(currentPaperIndex);
        } else {
            toggleSplitView(0);
        }
    }
}

function openPaperInNewTab(paperUrl) {
    if (paperUrl) {
        window.open(paperUrl, '_blank', 'noopener,noreferrer');
    }
}

function openPaperPDF(arxivId, fallbackUrl) {
    // Try to open ArXiv PDF if arxivId is available
    if (arxivId && arxivId.trim() !== '') {
        const pdfUrl = `https://arxiv.org/pdf/${arxivId}`;
        window.open(pdfUrl, '_blank', 'noopener,noreferrer');
    } else {
        // Fallback to original URL
        openPaperInNewTab(fallbackUrl);
    }
}

function toggleSplitView(paperIndex) {
    if (typeof papersData === 'undefined' || !papersData[paperIndex]) {
        console.error('Paper data not available');
        return;
    }
    
    const paper = papersData[paperIndex];
    const container = document.getElementById('split-view-container');
    
    if (!container) {
        console.error('Split view container not found');
        return;
    }
    
    if (splitViewActive && currentPaperIndex === paperIndex) {
        // Close if same paper
        closeSplitViewMode();
    } else {
        // Open or switch to new paper
        openSplitViewMode(paper, paperIndex);
    }
}

function openSplitViewMode(paper, paperIndex) {
    const container = document.getElementById('split-view-container');
    const paperTitle = document.getElementById('current-paper-title');
    const paperEmbed = document.getElementById('paper-embed');
    const pdfViewerContainer = document.getElementById('pdf-viewer-container');
    const pdfViewer = document.getElementById('pdf-viewer');
    const paperFallback = document.getElementById('paper-fallback');
    const fallbackLink = document.getElementById('fallback-link');
    
    // Update state
    splitViewActive = true;
    currentPaperIndex = paperIndex;
    
    // Show container
    container.setAttribute('data-active', 'true');
    container.setAttribute('aria-hidden', 'false');
    
    // Update title
    paperTitle.textContent = paper.title;
    
    // Move audio player to split view (instead of duplicating)
    moveAudioPlayerToSplitView();
    
    // Hide all viewers initially
    paperEmbed.style.display = 'none';
    pdfViewerContainer.style.display = 'none';
    paperFallback.style.display = 'none';
    
    // Determine how to display the paper
    const arxivId = paper.arxiv_id;
    
    if (arxivId && arxivId.trim() !== '') {
        // Use PDF viewer for ArXiv papers
        const pdfUrl = `https://arxiv.org/pdf/${arxivId}`;
        pdfViewer.src = pdfUrl;
        pdfViewerContainer.style.display = 'block';
    } else if (paper.embed_supported) {
        // Try iframe embedding
        paperEmbed.src = paper.url;
        paperEmbed.style.display = 'block';
    } else {
        // Show fallback with PDF link
        paperFallback.style.display = 'block';
        const fallbackPdfUrl = arxivId ? `https://arxiv.org/pdf/${arxivId}` : paper.url;
        fallbackLink.href = fallbackPdfUrl;
    }
    
    // Update button state
    updateSplitViewButtons();
    
    // Focus management
    document.getElementById('close-split-view').focus();
}

function moveAudioPlayerToSplitView() {
    const mainAudio = document.getElementById('podcast-audio');
    const placeholder = document.getElementById('audio-player-placeholder');
    const audioSection = document.querySelector('.audio-player-section');
    
    if (mainAudio && placeholder && audioSection) {
        // Move the entire audio player to split view
        const audioPlayerEnhanced = audioSection.querySelector('.audio-player-enhanced');
        if (audioPlayerEnhanced) {
            placeholder.innerHTML = '';
            placeholder.appendChild(audioPlayerEnhanced);
        }
    }
}

function returnAudioPlayerToMain() {
    const placeholder = document.getElementById('audio-player-placeholder');
    const audioSection = document.querySelector('.audio-player-section');
    
    if (placeholder && audioSection) {
        const audioPlayerEnhanced = placeholder.querySelector('.audio-player-enhanced');
        if (audioPlayerEnhanced) {
            audioSection.insertBefore(audioPlayerEnhanced, audioSection.querySelector('.episode-info'));
            placeholder.innerHTML = '<p>Split View 모드에서는 위의 오디오 플레이어가 이곳으로 이동합니다.</p>';
        }
    }
}

function closeSplitViewMode() {
    const container = document.getElementById('split-view-container');
    
    // Update state
    splitViewActive = false;
    
    // Hide container
    container.setAttribute('data-active', 'false');
    container.setAttribute('aria-hidden', 'true');
    
    // Return audio player to main section
    returnAudioPlayerToMain();
    
    // Clear all viewers
    const paperEmbed = document.getElementById('paper-embed');
    const pdfViewer = document.getElementById('pdf-viewer');
    if (paperEmbed) {
        paperEmbed.src = '';
    }
    if (pdfViewer) {
        pdfViewer.src = '';
    }
    
    // Update button state
    updateSplitViewButtons();
}

// Audio sync is no longer needed since we move the player instead of duplicating it

function updateSplitViewButtons() {
    const buttons = document.querySelectorAll('.split-view-btn');
    buttons.forEach((button, index) => {
        if (splitViewActive && index === currentPaperIndex) {
            button.textContent = '❌ Split View 닫기';
            button.setAttribute('aria-pressed', 'true');
        } else {
            button.textContent = '🔄 Split View';
            button.setAttribute('aria-pressed', 'false');
        }
    });
}

// Utility functions
function formatDuration(seconds) {
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}:${secs.toString().padStart(2, '0')}`;
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Export for global access
window.openPaperInNewTab = openPaperInNewTab;
window.openPaperPDF = openPaperPDF;
window.toggleSplitView = toggleSplitView;
window.closeSplitViewMode = closeSplitViewMode;
