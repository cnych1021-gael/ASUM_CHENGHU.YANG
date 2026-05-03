import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print(f"✅ API Key: {api_key[:10]}...{api_key[-4:]}")

try:
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents="用中文一句话说：主权是什么？"
    )
    print("\n🎉 Gemini 测试成功!")
    print(f"回答: {response.text}")
except Exception as e:
    print(f"\n❌ 错误: {e}")
