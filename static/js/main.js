// 配置常量
const CONFIG = {
    PREVIEW_DEBOUNCE_TIME: 500,
    MIN_SCALE: 0.1,
    MAX_SCALE: 5,
    SCALE_STEP: 1.2
};

// 状态管理
const state = {
    currentFile: null,
    originalFileName: null,
    previewDebounceTimer: null,
    transform: {
        scale: 1,
        isDragging: false,
        startX: 0,
        startY: 0,
        translateX: 0,
        translateY: 0
    }
};

// DOM 元素
const elements = {
    uploadZone: document.getElementById('uploadZone'),
    fileInput: document.getElementById('file'),
    retryButton: document.getElementById('retryButton'),
    svgPreview: document.getElementById('svgPreview'),
    zoomIn: document.getElementById('zoomIn'),
    zoomOut: document.getElementById('zoomOut'),
    zoomReset: document.getElementById('zoomReset'),
    zoomLevel: document.getElementById('zoomLevel'),
    loadingOverlay: document.getElementById('loadingOverlay'),
    uploadForm: document.getElementById('uploadForm'),
    sourcePreview: document.getElementById('sourcePreview')
};

// 工具函数
const utils = {
    showLoading() {
        elements.loadingOverlay.style.display = 'flex';
    },
    
    hideLoading() {
        elements.loadingOverlay.style.display = 'none';
    },
    
    showError(message) {
        console.error('Error:', message);
        elements.svgPreview.innerHTML = `
            <div class="upload-prompt">
                预览生成失败：${message}<br>
                请调整参数后重试
            </div>`;
    }
};

// 格式卡片处理
function initFormatCards() {
    document.querySelectorAll('.format-card').forEach(card => {
        const radio = card.querySelector('input[type="radio"]');
        if (radio.checked) {
            card.classList.add('selected');
        }
        
        card.addEventListener('click', () => {
            document.querySelectorAll('.format-card').forEach(c => {
                c.classList.remove('selected');
            });
            card.classList.add('selected');
            radio.checked = true;
            updatePreview();
        });
    });
}

// 文件上传处理
function initFileUpload() {
    elements.uploadZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        e.stopPropagation();
        elements.uploadZone.style.borderColor = '#2196F3';
        elements.uploadZone.style.backgroundColor = 'rgba(33, 150, 243, 0.05)';
    });

    elements.uploadZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        e.stopPropagation();
        elements.uploadZone.style.borderColor = '#ddd';
        elements.uploadZone.style.backgroundColor = '';
    });

    elements.uploadZone.addEventListener('drop', (e) => {
        e.preventDefault();
        e.stopPropagation();
        elements.uploadZone.style.borderColor = '#ddd';
        elements.uploadZone.style.backgroundColor = '';
        
        if (e.dataTransfer.files.length > 0) {
            elements.fileInput.files = e.dataTransfer.files;
            handleFileSelect(e.dataTransfer.files[0]);
        }
    });

    elements.uploadZone.addEventListener('click', () => {
        if (!document.querySelector('.preview-image')) {
            elements.fileInput.click();
        }
    });

    elements.retryButton.addEventListener('click', (e) => {
        e.stopPropagation();
        elements.fileInput.click();
    });

    elements.fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
}

// 文件处理函数
function handleFileSelect(file) {
    if (!file) return;
    
    state.currentFile = file;
    state.originalFileName = file.name;
    const reader = new FileReader();
    
    reader.onload = function(e) {
        elements.sourcePreview.innerHTML = '';
        const img = document.createElement('img');
        img.src = e.target.result;
        img.className = 'preview-image';
        elements.sourcePreview.appendChild(img);
        elements.retryButton.style.display = 'block';
        updatePreview();
    };
    
    reader.onerror = function(error) {
        utils.showError('文件读取失败：' + error.message);
    };
    
    reader.readAsDataURL(file);
}

// 预览更新函数
function updatePreview() {
    if (!state.currentFile) return;
    
    clearTimeout(state.previewDebounceTimer);
    state.previewDebounceTimer = setTimeout(() => {
        const formData = new FormData();
        formData.append('file', state.currentFile);
        
        // 添加所有参数
        ['blacklevel', 'turdsize', 'alphamax', 'opttolerance'].forEach(id => {
            formData.append(id, document.getElementById(id).value);
        });
        formData.append('color', document.getElementById('color').value);
        formData.append('outline_only', document.getElementById('outline_only').checked);

        utils.showLoading();

        fetch('/preview', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const container = document.createElement('div');
                container.className = 'svg-container';
                container.innerHTML = data.svg;
                elements.svgPreview.innerHTML = '';
                elements.svgPreview.appendChild(container);
                resetTransform();
            } else {
                utils.showError(data.error);
            }
        })
        .catch(error => {
            utils.showError(error.message);
        })
        .finally(utils.hideLoading);
    }, CONFIG.PREVIEW_DEBOUNCE_TIME);
}

// 变换处理函数
function updateTransform() {
    const container = elements.svgPreview.querySelector('.svg-container');
    if (container) {
        const { scale, translateX, translateY } = state.transform;
        container.style.transform = `translate(${translateX}px, ${translateY}px) scale(${scale})`;
        elements.zoomLevel.textContent = `${Math.round(scale * 100)}%`;
    }
}

function resetTransform() {
    state.transform = {
        scale: 1,
        isDragging: false,
        startX: 0,
        startY: 0,
        translateX: 0,
        translateY: 0
    };
    updateTransform();
}

// 缩放和平移功能初始化
function initTransformControls() {
    elements.zoomIn.addEventListener('click', () => {
        state.transform.scale = Math.min(state.transform.scale * CONFIG.SCALE_STEP, CONFIG.MAX_SCALE);
        updateTransform();
    });

    elements.zoomOut.addEventListener('click', () => {
        state.transform.scale = Math.max(state.transform.scale / CONFIG.SCALE_STEP, CONFIG.MIN_SCALE);
        updateTransform();
    });

    elements.zoomReset.addEventListener('click', resetTransform);

    // 拖动功能
    elements.svgPreview.addEventListener('mousedown', (e) => {
        if (e.target.closest('.preview-controls')) return;
        state.transform.isDragging = true;
        elements.svgPreview.classList.add('grabbing');
        state.transform.startX = e.clientX - state.transform.translateX;
        state.transform.startY = e.clientY - state.transform.translateY;
    });

    document.addEventListener('mousemove', (e) => {
        if (!state.transform.isDragging) return;
        state.transform.translateX = e.clientX - state.transform.startX;
        state.transform.translateY = e.clientY - state.transform.startY;
        updateTransform();
    });

    document.addEventListener('mouseup', () => {
        state.transform.isDragging = false;
        elements.svgPreview.classList.remove('grabbing');
    });

    // 鼠标滚轮缩放
    elements.svgPreview.addEventListener('wheel', (e) => {
        e.preventDefault();
        const delta = e.deltaY > 0 ? 0.9 : 1.1;
        const newScale = state.transform.scale * delta;
        
        if (newScale >= CONFIG.MIN_SCALE && newScale <= CONFIG.MAX_SCALE) {
            const container = elements.svgPreview.querySelector('.svg-container');
            const rect = container.getBoundingClientRect();
            
            // 计算鼠标相对于容器的位置
            const mouseX = e.clientX - rect.left;
            const mouseY = e.clientY - rect.top;
            
            // 计算鼠标位置相对于容器中心的偏移量
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            // 计算新的位移
            state.transform.translateX = state.transform.translateX + (mouseX - centerX) * (1 - delta);
            state.transform.translateY = state.transform.translateY + (mouseY - centerY) * (1 - delta);
            state.transform.scale = newScale;
            
            updateTransform();
        }
    });
}

// 滑块初始化
function initSliders() {
    function updateSliderValue(sliderId, valueId) {
        const slider = document.getElementById(sliderId);
        const valueDisplay = document.getElementById(valueId);
        valueDisplay.textContent = slider.value;
        
        slider.addEventListener('input', function() {
            valueDisplay.textContent = this.value;
        });
    }

    ['blacklevel', 'turdsize', 'alphamax', 'opttolerance'].forEach(id => {
        updateSliderValue(id, `${id}Value`);
        document.getElementById(id).addEventListener('input', updatePreview);
    });

    ['color', 'outline_only'].forEach(id => {
        document.getElementById(id).addEventListener('input', updatePreview);
    });
}

// 表单提交处理
function initFormSubmit() {
    elements.uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!state.currentFile) {
            alert('请先选择图片');
            return;
        }
        
        utils.showLoading();
        
        fetch('/', {
            method: 'POST',
            body: new FormData(this)
        })
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok.');
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            const originalName = state.originalFileName || 'converted';
            const baseName = originalName.substring(0, originalName.lastIndexOf('.')) || originalName;
            const newExt = document.querySelector('input[name="output_format"]:checked').value;
            a.download = `${baseName}.${newExt}`;
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        })
        .catch(error => {
            console.error('Error:', error);
            alert('转换失败，请重试');
        })
        .finally(utils.hideLoading);
    });
}

// 初始化颜色预设功能
function initColorPresets() {
    const colorInput = document.getElementById('color');
    const presetButtons = document.querySelectorAll('.color-preset');
    
    presetButtons.forEach(button => {
        button.addEventListener('click', () => {
            const color = button.dataset.color;
            colorInput.value = color;
            // 移除其他按钮的选中状态
            presetButtons.forEach(btn => btn.classList.remove('selected'));
            // 添加当前按钮的选中状态
            button.classList.add('selected');
        });
    });
}

// 初始化应用
function initApp() {
    initFormatCards();
    initFileUpload();
    initTransformControls();
    initSliders();
    initFormSubmit();
    initColorPresets();
}

// 启动应用
document.addEventListener('DOMContentLoaded', initApp); 