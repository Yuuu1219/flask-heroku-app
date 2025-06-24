from flask import Flask
import spacy
import os

app = Flask(__name__)

# 获取当前环境信息
env = os.environ.get("ENV", "development")
port = int(os.environ.get("PORT", 5491))

# 模型加载函数
def load_spacy_model():
    try:
        # 尝试直接加载模型
        nlp = spacy.load("en_core_web_sm")
        print("✅ spaCy model loaded successfully")
        return nlp
    except OSError:
        print("⚠️ Model not found. Downloading now...")
        # 如果模型不存在则下载
        from spacy.cli import download
        download("en_core_web_sm")
        return spacy.load("en_core_web_sm")

# 全局加载模型（生产环境）
if env == "production":
    nlp = load_spacy_model()

@app.route('/')
def home():
    # 开发环境下按需加载（节省资源）
    if env == "development":
        local_nlp = load_spacy_model()
    else:
        local_nlp = nlp
        
    # 使用spaCy处理文本
    doc = local_nlp("Hello world from Render! This is a spaCy demo.")
    
    # 提取处理结果
    results = {
        "tokens": [token.text for token in doc],
        "entities": [(ent.text, ent.label_) for ent in doc.ents],
        "lemmas": [token.lemma_ for token in doc],
        "pos_tags": [(token.text, token.pos_) for token in doc]
    }
    
    return {
        "message": "SpaCy NLP Processing",
        "environment": env,
        "results": results
    }

@app.route('/health')
def health_check():
    return {"status": "healthy", "service": "spacy-nlp"}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port, debug=(env == "development"))