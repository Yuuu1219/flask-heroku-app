import os
from flask import Flask, request, render_template, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import spacy
from deep_translator import GoogleTranslator
import re
import random
from dotenv import load_dotenv

load_dotenv()  # 加载环境变量

app = Flask(__name__)

# 使用您提供的Chromedriver路径
nlp = spacy.load("en_core_web_sm")

def extract_text_from_tweet(url):
    # 增强URL验证
    if not re.match(r'https?://(x\.com|twitter\.com|www\.x\.com|www\.twitter\.com)/\S+', url):
        return None
        
    options = Options()
    options.add_argument('--headless=new')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')
    
    # 添加随机User-Agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    # 使用您提供的Chromedriver路径
    service = Service(executable_path=r"C:\Users\SZ0201\Desktop\chromedriver-win64\chromedriver.exe")
    
    try:
        driver = webdriver.Chrome(service=service, options=options)
        driver.get(url)
        time.sleep(3)
        
        # 尝试多种选择器提高成功率
        selectors = [
            'article div[lang]',
            'div[data-testid="tweetText"]',
            'div[lang].css-1dbjc4n.r-1s2bzr4'
        ]
        
        for selector in selectors:
            try:
                element = driver.find_element(By.CSS_SELECTOR, selector)
                if element.text.strip():
                    return element.text.strip()
            except:
                continue
        
        return None
    except Exception as e:
        app.logger.error(f"抓取失败：{e}")
        return None
    finally:
        if 'driver' in locals():
            driver.quit()

def translate_text(text):
    try:
        # 优化长文本处理
        if len(text) > 4500:
            text = text[:4500]
            truncated = True
        else:
            truncated = False
            
        translation = GoogleTranslator(source='auto', target='zh-CN').translate(text)
        
        if truncated:
            translation += "... [内容过长已截断]"
            
        return translation
    except Exception as e:
        app.logger.error(f"翻译失败: {e}")
        return "翻译失败"

def extract_keywords(text):
    """优化关键词提取算法"""
    doc = nlp(text)
    
    # 提取名词短语和实体
    keywords = set()
    noun_phrases = [chunk.text for chunk in doc.noun_chunks]
    entities = [ent.text for ent in doc.ents if ent.label_ in ['PERSON', 'ORG', 'GPE', 'PRODUCT', 'EVENT']]
    
    # 添加重要词性
    important_tokens = [
        token.lemma_.lower() for token in doc 
        if token.pos_ in ['NOUN', 'PROPN', 'ADJ', 'VERB'] 
        and not token.is_stop 
        and len(token.text) > 2
    ]
    
    keywords.update(noun_phrases)
    keywords.update(entities)
    keywords.update(important_tokens)
    
    # 按频率和长度排序
    return sorted(keywords, key=lambda x: (text.lower().count(x.lower()), len(x)), reverse=True)[:10]

def extract_attractive_content(text):
    """优化吸引内容提取"""
    doc = nlp(text)
    attractive_elements = []
    
    # 1. 提取情感强烈的句子
    emotional_sentences = [
        sent.text.strip() for sent in doc.sents 
        if any(token.text in ['!', '?'] for token in sent) or
           any(token.lemma_ in ['love', 'hate', 'amazing', 'terrible'] for token in sent)
    ]
    
    # 2. 提取问题和呼吁行动
    action_phrases = [
        sent.text.strip() for sent in doc.sents 
        if any(token.text.lower() in ['how', 'why', 'what', 'should', 'must', 'need'] for token in sent) or
           '?' in sent.text
    ]
    
    # 3. 提取数字和统计数据
    number_phrases = [
        chunk.text for chunk in doc.noun_chunks 
        if any(token.like_num for token in chunk)
    ]
    
    # 4. 提取专有名词和热门话题
    trending_topics = [
        ent.text for ent in doc.ents 
        if ent.label_ in ['PERSON', 'ORG', 'PRODUCT', 'EVENT']
    ]
    
    # 组合所有吸引元素
    attractive_elements.extend(emotional_sentences[:2])
    attractive_elements.extend(action_phrases[:2])
    attractive_elements.extend(number_phrases[:2])
    attractive_elements.extend(trending_topics[:3])
    
    # 去重并按长度排序
    unique_elements = list(set(attractive_elements))
    return sorted(unique_elements, key=len, reverse=True)[:5]  # 返回最多5条

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze_tweet():
    data = request.get_json()
    tweet_url = data.get('tweet_url')
    
    if not tweet_url:
        return jsonify({"error": "缺少推文链接"}), 400
        
    # 提取推文内容
    tweet_content = extract_text_from_tweet(tweet_url)
    
    if not tweet_content:
        return jsonify({"error": "无法获取推文内容，请检查链接是否正确"}), 500
        
    # 翻译文本
    translation = translate_text(tweet_content)
    
    # 提取关键词
    keywords = extract_keywords(tweet_content)
    
    # 提取吸引内容
    attractive_content = extract_attractive_content(tweet_content)
    
    return jsonify({
        "success": True,
        "tweet_content": tweet_content,
        "translation": translation,
        "keywords": keywords,
        "attractive_content": attractive_content
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5491))
    app.run(debug=os.environ.get('FLASK_DEBUG', 'False') == 'True', 
            host='0.0.0.0', 
            port=port)