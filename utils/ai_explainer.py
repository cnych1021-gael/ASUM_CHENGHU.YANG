"""AI 解释器 - Google Gemini"""
import os
import streamlit as st

try:
    from dotenv import load_dotenv
    load_dotenv()
except:
    pass

try:
    from google import genai
    GEMINI_AVAILABLE = True
except:
    GEMINI_AVAILABLE = False

def init_gemini():
    if not GEMINI_AVAILABLE:
        return False, "google-genai 未安装"
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return False, "未找到 API key"
    try:
        return True, genai.Client(api_key=api_key)
    except Exception as e:
        return False, str(e)

@st.cache_data(ttl=3600, show_spinner=False)
def explain_concept_evolution(concept, similarity, cold_context="", post_context="", lang='zh'):
    """解释概念演变"""
    success, result = init_gemini()
    if not success:
        return f"⚠️ {result}"
    
    client = result
    change = '剧烈' if similarity < 0.5 else '中度' if similarity < 0.7 else '稳定'
    change_en = 'drastic' if similarity < 0.5 else 'moderate' if similarity < 0.7 else 'stable'
    change_es = 'drástico' if similarity < 0.5 else 'moderado' if similarity < 0.7 else 'estable'
    
    prompts = {
        'zh': f"""你是联合国大会演讲研究专家。请用中文解释概念"{concept}"的语义演变。
数据：相似度{similarity:.2f}（0=完全改变，1=稳定），变化程度：{change}
冷战时期关联词：{cold_context[:200]}
后冷战关联词：{post_context[:200]}

请回答（300字内）：
1. 简明解释：冷战和后冷战时期含义有何不同？
2. 历史背景：哪些事件导致了变化？
3. 现实意义：为什么重要？
4. 典型案例：举1-2个例子。

用段落格式，不要markdown。""",
        'en': f"""You are a UN speech research expert. Explain the semantic evolution of "{concept}" in English.
Data: similarity {similarity:.2f} (0=completely changed, 1=stable), level: {change_en}
Cold War terms: {cold_context[:200]}
Post-Cold War terms: {post_context[:200]}

Answer (under 300 words):
1. Brief explanation: How did meaning differ?
2. Historical context: What events caused this?
3. Significance: Why does it matter?
4. Cases: 1-2 examples.

Use paragraphs, no markdown.""",
        'es': f"""Eres experto en discursos ONU. Explica la evolución de "{concept}" en español.
Datos: similitud {similarity:.2f} (0=cambiado, 1=estable), nivel: {change_es}
Términos Guerra Fría: {cold_context[:200]}
Términos Post-Guerra Fría: {post_context[:200]}

Responde (menos 300 palabras):
1. Explicación: ¿Cómo difería el significado?
2. Contexto histórico: ¿Qué eventos causaron el cambio?
3. Significado: ¿Por qué importa?
4. Casos: 1-2 ejemplos.

Usa párrafos, sin markdown."""
    }
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompts[lang]
        )
        return response.text
    except Exception as e:
        return f"⚠️ {str(e)}"

@st.cache_data(ttl=3600, show_spinner=False)
def answer_question(question, context_data="", lang='zh'):
    """回答用户的自然语言问题"""
    success, result = init_gemini()
    if not success:
        return f"⚠️ {result}"
    
    client = result
    
    prompts = {
        'zh': f"""你是联合国大会演讲（1971-2025）政治语言学专家。

数据上下文：
{context_data}

用户问题：{question}

请用中文专业回答，300字内。如果数据不足，诚实说明。""",
        'en': f"""You are a UN speech (1971-2025) political linguistics expert.

Data context:
{context_data}

User question: {question}

Answer professionally in English, under 300 words.""",
        'es': f"""Eres experto en lingüística política de la ONU (1971-2025).

Contexto:
{context_data}

Pregunta: {question}

Responde profesionalmente en español, menos de 300 palabras."""
    }
    
    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompts[lang]
        )
        return response.text
    except Exception as e:
        return f"⚠️ {str(e)}"

def is_ai_available():
    success, _ = init_gemini()
    return success

def get_ai_status(lang='zh'):
    success, result = init_gemini()
    msgs = {
        'zh': {'ok': '✅ AI已就绪', 'err': f'❌ {result}'},
        'en': {'ok': '✅ AI Ready', 'err': f'❌ {result}'},
        'es': {'ok': '✅ IA Lista', 'err': f'❌ {result}'}
    }
    return msgs[lang]['ok'] if success else msgs[lang]['err']
