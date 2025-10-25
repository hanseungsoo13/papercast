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
    
    // Try to embed paper
    if (paper.embed_supported) {
        paperEmbed.src = paper.url;
        paperEmbed.style.display = 'block';
        paperFallback.style.display = 'none';
    } else {
        // Show fallback
        paperEmbed.style.display = 'none';
        paperFallback.style.display = 'block';
        fallbackLink.href = paper.url;
    }
    
    // Sync audio players
    syncAudioPlayers();
    
    // Update button state
    updateSplitViewButtons();
    
    // Focus management
    document.getElementById('close-split-view').focus();
}

function closeSplitViewMode() {
    const container = document.getElementById('split-view-container');
    
    // Update state
    splitViewActive = false;
    
    // Hide container
    container.setAttribute('data-active', 'false');
    container.setAttribute('aria-hidden', 'true');
    
    // Clear embed
    const paperEmbed = document.getElementById('paper-embed');
    if (paperEmbed) {
        paperEmbed.src = '';
    }
    
    // Update button state
    updateSplitViewButtons();
}

function syncAudioPlayers() {
    const mainAudio = document.getElementById('podcast-audio');
    const splitAudio = document.getElementById('split-view-audio');
    
    if (mainAudio && splitAudio) {
        // Sync time and playing state
        splitAudio.currentTime = mainAudio.currentTime;
        
        if (!mainAudio.paused) {
            splitAudio.play().catch(e => console.log('Auto-play prevented:', e));
        }
        
        // Sync controls
        mainAudio.addEventListener('play', () => {
            if (splitViewActive) splitAudio.play().catch(e => console.log(e));
        });
        
        mainAudio.addEventListener('pause', () => {
            if (splitViewActive) splitAudio.pause();
        });
        
        mainAudio.addEventListener('timeupdate', () => {
            if (splitViewActive && Math.abs(splitAudio.currentTime - mainAudio.currentTime) > 1) {
                splitAudio.currentTime = mainAudio.currentTime;
            }
        });
        
        // Reverse sync
        splitAudio.addEventListener('timeupdate', () => {
            if (splitViewActive && Math.abs(mainAudio.currentTime - splitAudio.currentTime) > 1) {
                mainAudio.currentTime = splitAudio.currentTime;
            }
        });
    }
}

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
window.toggleSplitView = toggleSplitView;
window.closeSplitViewMode = closeSplitViewMode;
