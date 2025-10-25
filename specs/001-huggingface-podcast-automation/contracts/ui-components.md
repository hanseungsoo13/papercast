# UI Components Contract

**Feature**: 001-huggingface-podcast-automation  
**Date**: 2025-10-24  
**Purpose**: Define contracts for UI components and interactions

## Component Specifications

### 1. PaperCard Component

**Purpose**: Display individual paper information with actions

#### Props/Attributes
```typescript
interface PaperCardProps {
  paper: EnhancedPaper;
  isPlaying?: boolean;
  onPlayToggle?: () => void;
  onViewPaper?: (paperId: string) => void;
  onSplitView?: (paperId: string) => void;
}
```

#### DOM Structure
```html
<div class="paper-card" data-paper-id="{paperId}">
  <div class="paper-thumbnail">
    <img src="{thumbnailUrl}" alt="{title} thumbnail" loading="lazy">
    <div class="paper-category-tags">
      <span class="category-tag">{category}</span>
    </div>
  </div>
  
  <div class="paper-content">
    <h3 class="paper-title">{title}</h3>
    <p class="paper-authors">{authors.join(', ')}</p>
    <p class="paper-abstract">{abstract}</p>
    <div class="paper-meta">
      <span class="upvotes">👍 {upvotes}</span>
      <span class="views">👁️ {viewCount}</span>
      <span class="date">{publishedDate}</span>
    </div>
  </div>
  
  <div class="paper-actions">
    <button class="btn-primary" onclick="viewPaper('{paperId}')">
      📄 논문 원본 보기
    </button>
    <button class="btn-secondary" onclick="toggleSplitView('{paperId}')">
      🔄 Split View
    </button>
    <button class="btn-audio" onclick="playPaperAudio('{paperId}')">
      {isPlaying ? '⏸️' : '▶️'} 오디오
    </button>
  </div>
</div>
```

#### CSS Classes
```css
.paper-card {
  /* Card container styles */
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  transition: transform 0.2s ease;
}

.paper-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(0,0,0,0.15);
}

.paper-thumbnail {
  position: relative;
  aspect-ratio: 16/9;
  overflow: hidden;
}

.paper-actions {
  display: flex;
  gap: 0.5rem;
  padding: 1rem;
}

@media (max-width: 768px) {
  .paper-actions {
    flex-direction: column;
  }
}
```

### 2. SplitView Component

**Purpose**: Manage split-screen layout for simultaneous paper viewing and podcast listening

#### Interface
```typescript
interface SplitViewManager {
  isActive: boolean;
  currentPaper: string | null;
  
  activate(paperId: string): void;
  deactivate(): void;
  toggle(paperId: string): void;
  resize(leftWidth: number): void;
}
```

#### DOM Structure
```html
<div class="split-view-container" data-active="false">
  <div class="split-view-left">
    <!-- Podcast player content -->
    <div class="podcast-player-section">
      <audio controls class="audio-player"></audio>
      <div class="episode-info"></div>
    </div>
  </div>
  
  <div class="split-view-divider" draggable="true">
    <div class="divider-handle"></div>
  </div>
  
  <div class="split-view-right">
    <!-- Paper viewer content -->
    <div class="paper-viewer-section">
      <div class="paper-viewer-header">
        <h3 class="current-paper-title"></h3>
        <button class="close-split-view" onclick="closeSplitView()">✕</button>
      </div>
      <div class="paper-viewer-content">
        <iframe class="paper-embed" src="" frameborder="0"></iframe>
        <div class="paper-fallback" style="display: none;">
          <p>이 논문은 임베딩을 지원하지 않습니다.</p>
          <a href="" target="_blank" class="btn-primary">새 탭에서 열기</a>
        </div>
      </div>
    </div>
  </div>
</div>
```

#### CSS Grid Layout
```css
.split-view-container {
  display: grid;
  grid-template-columns: 1fr 4px 1fr;
  height: 100vh;
  transition: grid-template-columns 0.3s ease;
}

.split-view-container[data-active="false"] {
  grid-template-columns: 1fr 0 0;
}

.split-view-divider {
  background: #e0e0e0;
  cursor: col-resize;
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .split-view-container {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto;
  }
}
```

### 3. AudioPlayer Component

**Purpose**: Enhanced audio player with paper synchronization

#### Interface
```typescript
interface AudioPlayerController {
  currentTime: number;
  duration: number;
  isPlaying: boolean;
  currentPaper: number; // Index of currently discussed paper
  
  play(): void;
  pause(): void;
  seek(time: number): void;
  setVolume(volume: number): void;
  onPaperChange(callback: (paperIndex: number) => void): void;
}
```

#### DOM Structure
```html
<div class="audio-player-enhanced">
  <audio class="audio-element" preload="metadata">
    <source src="{audioUrl}" type="audio/mpeg">
  </audio>
  
  <div class="player-controls">
    <button class="play-pause-btn">▶️</button>
    <div class="progress-container">
      <div class="progress-bar">
        <div class="progress-fill"></div>
        <div class="progress-handle"></div>
      </div>
      <div class="time-display">
        <span class="current-time">0:00</span>
        <span class="duration">0:00</span>
      </div>
    </div>
    <div class="volume-control">
      <button class="volume-btn">🔊</button>
      <input type="range" class="volume-slider" min="0" max="100" value="100">
    </div>
  </div>
  
  <div class="paper-timeline">
    <div class="timeline-marker" data-paper="0" data-time="0">Paper 1</div>
    <div class="timeline-marker" data-paper="1" data-time="180">Paper 2</div>
    <div class="timeline-marker" data-paper="2" data-time="360">Paper 3</div>
  </div>
</div>
```

### 4. PaperViewer Component

**Purpose**: Display paper content with embed fallback

#### Interface
```typescript
interface PaperViewer {
  currentPaper: EnhancedPaper | null;
  embedSupported: boolean;
  
  loadPaper(paper: EnhancedPaper): Promise<void>;
  checkEmbedSupport(url: string): Promise<boolean>;
  showFallback(): void;
}
```

#### Embed Check Logic
```javascript
async function checkEmbedSupport(url) {
  try {
    const response = await fetch(url, { 
      method: 'HEAD',
      mode: 'cors'
    });
    
    const xFrameOptions = response.headers.get('X-Frame-Options');
    const csp = response.headers.get('Content-Security-Policy');
    
    // Check for embedding restrictions
    if (xFrameOptions && xFrameOptions.toLowerCase() === 'deny') {
      return false;
    }
    
    if (csp && csp.includes('frame-ancestors')) {
      return false;
    }
    
    return true;
  } catch (error) {
    return false;
  }
}
```

## Accessibility Contracts

### Keyboard Navigation
```typescript
interface KeyboardShortcuts {
  'Space': 'togglePlayPause';
  'Escape': 'closeSplitView';
  'Ctrl+S': 'toggleSplitView';
  'ArrowLeft': 'previousPaper';
  'ArrowRight': 'nextPaper';
  'Ctrl+Enter': 'openPaperInNewTab';
}
```

### ARIA Labels
```html
<!-- Required ARIA attributes -->
<button 
  aria-label="논문 원본을 새 탭에서 열기"
  aria-describedby="paper-title-{paperId}"
  role="button"
  tabindex="0">
  📄 논문 원본 보기
</button>

<div 
  class="split-view-container"
  role="application"
  aria-label="분할 화면 논문 뷰어"
  aria-live="polite">
</div>

<audio 
  controls
  aria-label="팟캐스트 오디오 플레이어"
  aria-describedby="episode-title">
</audio>
```

### Screen Reader Support
```css
.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}
```

## Performance Contracts

### Lazy Loading
```javascript
// Image lazy loading
const imageObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const img = entry.target;
      img.src = img.dataset.src;
      img.classList.remove('lazy');
      imageObserver.unobserve(img);
    }
  });
});

// Component lazy loading
const componentObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      loadPaperMetadata(entry.target.dataset.paperId);
    }
  });
});
```

### Resource Loading Priorities
```html
<!-- Critical resources -->
<link rel="preload" href="styles.css" as="style">
<link rel="preload" href="script.js" as="script">

<!-- Non-critical resources -->
<link rel="prefetch" href="paper-viewer.js">
<link rel="dns-prefetch" href="//huggingface.co">
```

## Error Handling Contracts

### Error States
```typescript
interface ErrorState {
  type: 'network' | 'embed' | 'audio' | 'permission';
  message: string;
  recoverable: boolean;
  retryAction?: () => void;
}
```

### User-Friendly Error Messages
```javascript
const errorMessages = {
  'embed-blocked': '이 논문은 임베딩을 지원하지 않습니다. 새 탭에서 열어보세요.',
  'network-error': '네트워크 연결을 확인해주세요.',
  'audio-failed': '오디오를 로드할 수 없습니다. 다시 시도해주세요.',
  'paper-not-found': '논문을 찾을 수 없습니다.'
};
```

## Testing Contracts

### Component Testing
```javascript
// Required test cases for each component
describe('PaperCard', () => {
  it('should render paper information correctly');
  it('should handle click events');
  it('should be accessible via keyboard');
  it('should display fallback for missing thumbnails');
});

describe('SplitView', () => {
  it('should toggle split view mode');
  it('should handle window resize');
  it('should maintain aspect ratios');
  it('should work on mobile devices');
});
```

### Integration Testing
```javascript
// User journey tests
describe('Paper Viewing Journey', () => {
  it('should allow user to view paper while listening');
  it('should sync audio timeline with paper content');
  it('should handle embed failures gracefully');
  it('should maintain state across navigation');
});
```
