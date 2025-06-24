document.addEventListener('DOMContentLoaded', function() {
    const analyzeBtn = document.getElementById('analyze-btn');
    const tweetUrlInput = document.getElementById('tweet_url');
    const resultsContent = document.getElementById('results-content');
    
    analyzeBtn.addEventListener('click', async function() {
        const tweetUrl = tweetUrlInput.value.trim();
        
        if (!tweetUrl) {
            showError('请输入有效的推文链接');
            return;
        }
        
        // 增强URL验证
        if (!isValidTwitterUrl(tweetUrl)) {
            showError('请输入有效的Twitter/X链接 (如: https://twitter.com/... 或 https://x.com/...)');
            return;
        }
        
        // 显示加载状态
        showLoading();
        
        try {
            // 发送请求到后端API
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ tweet_url: tweetUrl })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.error || '分析推文时出错');
            }
            
            // 显示结果
            displayResults(data);
            
        } catch (error) {
            showError(`分析失败: ${error.message}`);
        }
    });
    
    // 添加键盘支持
    tweetUrlInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            analyzeBtn.click();
        }
    });
    
    function showLoading() {
        resultsContent.innerHTML = `
            <div class="result-section">
                <div class="result-placeholder">
                    <div class="spinner">
                        <div class="bounce1"></div>
                        <div class="bounce2"></div>
                        <div class="bounce3"></div>
                    </div>
                    <p>正在分析中，请稍候...</p>
                    <p class="loading-tip">这可能需要10-20秒，请耐心等待</p>
                </div>
            </div>
        `;
    }
    
    function showError(message) {
        resultsContent.innerHTML = `
            <div class="result-section">
                <div class="result-header error">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>错误</h3>
                </div>
                <div class="result-content">
                    ${message}
                </div>
                <div class="retry-section">
                    <button id="retry-btn">重试</button>
                </div>
            </div>
        `;
        
        // 添加重试按钮事件
        document.getElementById('retry-btn').addEventListener('click', function() {
            tweetUrlInput.focus();
        });
    }
    
    function displayResults(data) {
        // 创建结果HTML
        let resultsHTML = '';
        
        // 原始内容
        resultsHTML += `
            <div class="result-section">
                <div class="result-header">
                    <i class="fas fa-file-alt"></i>
                    <h3>推文原文</h3>
                </div>
                <div class="result-content">
                    <div class="content-box">${data.tweet_content || '无内容'}</div>
                </div>
            </div>
        `;
        
        // 翻译结果
        resultsHTML += `
            <div class="result-section">
                <div class="result-header">
                    <i class="fas fa-language"></i>
                    <h3>中文翻译</h3>
                </div>
                <div class="result-content">
                    <div class="content-box translation">${data.translation || '无翻译结果'}</div>
                </div>
            </div>
        `;
        
        // 关键词
        if (data.keywords && data.keywords.length > 0) {
            const keywordsHTML = data.keywords.map(kw => 
                `<span class="keyword">${kw}</span>`
            ).join('');
            
            resultsHTML += `
                <div class="result-section">
                    <div class="result-header">
                        <i class="fas fa-tags"></i>
                        <h3>关键词分析</h3>
                    </div>
                    <div class="result-content">
                        <div class="keywords-container">
                            ${keywordsHTML}
                        </div>
                    </div>
                </div>
            `;
        }
        
        // 吸引点内容
        if (data.attractive_content && data.attractive_content.length > 0) {
            const attractiveHTML = data.attractive_content.map(item => 
                `<li><i class="fas fa-star"></i> ${item}</li>`
            ).join('');
            
            resultsHTML += `
                <div class="result-section">
                    <div class="result-header">
                        <i class="fas fa-fire"></i>
                        <h3>吸引点分析</h3>
                    </div>
                    <div class="result-content">
                        <ul class="attractive-list">${attractiveHTML}</ul>
                    </div>
                </div>
            `;
        }
        
        // 添加分享按钮
        resultsHTML += `
            <div class="share-section">
                <button id="new-analysis">
                    <i class="fas fa-plus"></i> 新的分析
                </button>
            </div>
        `;
        
        resultsContent.innerHTML = resultsHTML;
        
        // 添加新分析按钮事件
        document.getElementById('new-analysis').addEventListener('click', function() {
            tweetUrlInput.value = '';
            tweetUrlInput.focus();
            resultsContent.innerHTML = `
                <div class="result-section">
                    <div class="result-placeholder">
                        <i class="fas fa-file-alt"></i>
                        <p>分析结果将显示在这里</p>
                    </div>
                </div>
            `;
        });
    }
    
    function isValidTwitterUrl(url) {
        return /https?:\/\/(x\.com|twitter\.com|www\.x\.com|www\.twitter\.com)\/\S+/i.test(url);
    }
});