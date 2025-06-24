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
        
        // 验证URL格式
        if (!isValidTwitterUrl(tweetUrl)) {
            showError('请输入有效的Twitter/X链接 (https://twitter.com/... 或 https://x.com/...)');
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
    
    function showLoading() {
        resultsContent.innerHTML = `
            <div class="result-section">
                <div class="result-placeholder">
                    <i class="fas fa-spinner fa-spin"></i>
                    <p>正在分析中，请稍候...</p>
                </div>
            </div>
        `;
    }
    
    function showError(message) {
        resultsContent.innerHTML = `
            <div class="result-section">
                <div class="result-header">
                    <i class="fas fa-exclamation-triangle"></i>
                    <h3>错误</h3>
                </div>
                <div class="result-content">
                    ${message}
                </div>
            </div>
        `;
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
                    ${data.tweet_content || '无内容'}
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
                    ${data.translation || '无翻译结果'}
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
                `<li>${item}</li>`
            ).join('');
            
            resultsHTML += `
                <div class="result-section">
                    <div class="result-header">
                        <i class="fas fa-fire"></i>
                        <h3>吸引点分析</h3>
                    </div>
                    <div class="result-content">
                        <ul>${attractiveHTML}</ul>
                    </div>
                </div>
            `;
        }
        
        resultsContent.innerHTML = resultsHTML;
    }
    
    function isValidTwitterUrl(url) {
        return /https?:\/\/(x\.com|twitter\.com)\/\S+/i.test(url);
    }
});