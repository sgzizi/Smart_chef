import streamlit as st
import os
import re
import requests
import subprocess
from dotenv import load_dotenv

# 页面设置
st.set_page_config(page_title="SmartChef 智能厨神助手", page_icon="🍽️", layout="wide")

# 加载 API 密钥
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

# 城市映射和天气对应菜品
CITY_MAP = {
    "北京": "Beijing", "上海": "Shanghai", "广州": "Guangzhou", "深圳": "Shenzhen",
    "南京": "Nanjing", "秦皇岛": "Qinhuangdao", "杭州": "Hangzhou", "重庆": "Chongqing",
    "天津": "Tianjin", "武汉": "Wuhan", "成都": "Chengdu", "长沙": "Changsha"
}

SEASONAL_FOODS = {
    "cold": ["羊肉炖萝卜", "红枣枸杞汤", "生姜鸡汤", "牛肉粥"],
    "hot": ["绿豆汤", "凉拌黄瓜", "番茄鸡蛋冷面", "西瓜沙拉"],
    "rain": ["山药排骨汤", "茯苓薏米粥", "陈皮鸭", "冬瓜汤"],
    "mild": ["清炒时蔬", "蒸南瓜", "香菇滑鸡", "玉米排骨汤"]
}

# 清理文本
def clean_text(text):
    text = re.sub(r"[-=]{3,}", "", text)
    text = re.sub(r"[~~]{2,}(.*?)~~", "", text)
    text = re.sub(r"<s>.*?</s>", "", text)
    text = re.sub(r"<del>.*?</del>", "", text)
    text = re.sub(r"[（(][^）)]+[）)]", "", text)
    text = re.sub(r"[—–－_‾﹣]+", "", text)
    text = text.replace("✅ 小宝回答：", "")
    text = text.replace("✅ Chef助手回答：", "")
    return text.strip()

# 关键词提取（用于视频推荐）
def extract_keywords(text):
    keywords = ["营养", "饮食", "食谱", "蔬菜", "低脂", "健康", "高蛋白", "低碳水", "减脂", "三高", "糖尿病", "早餐", "午餐", "晚餐"]
    found = set()
    for line in text.splitlines():
        for word in keywords:
            if word in line:
                found.add(word)
    return list(found)[:3] or ["健康饮食"]

# 视频推荐
def recommend_youtube_videos(query, max_results=3):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&maxResults={max_results}&q={query}&key={YOUTUBE_API_KEY}"
    res = requests.get(url)
    videos = []
    if res.status_code == 200:
        for item in res.json().get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            link = f"https://www.youtube.com/watch?v={video_id}"
            videos.append((title, link))
    return videos

# 获取天气
def get_weather(city_name, is_zh=True):
    query = CITY_MAP.get(city_name.strip(), city_name)
    url = f"http://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={query}&lang={'zh' if is_zh else 'en'}"
    try:
        res = requests.get(url)
        data = res.json()
        condition = data["current"]["condition"]["text"]
        temp = data["current"]["temp_c"]
        weather_type = categorize_weather(condition, temp)
        return f"{condition}, {temp}°C", weather_type
    except:
        return "❌ 天气获取失败", "mild"

# 分类天气
def categorize_weather(condition, temp):
    condition = condition.lower()
    if "rain" in condition or "雨" in condition:
        return "rain"
    elif temp <= 10:
        return "cold"
    elif temp >= 28:
        return "hot"
    else:
        return "mild"

# 展示天气和推荐
def display_weather_and_recipes(city_name, is_zh=True):
    st.markdown("## 🌦 当前天气与时令推荐")
    weather_str, weather_type = get_weather(city_name, is_zh)
    st.info(f"📍 {city_name} 当前天气：{weather_str}")
    st.markdown("🍽️ 推荐以下适合当前天气的时令菜：")
    for dish in SEASONAL_FOODS.get(weather_type, []):
        st.markdown(f"- {dish}")

# 多语言支持
language = st.selectbox("🌐 Language / 语言", ["中文", "English"])
is_zh = language == "中文"

T = {
    "title": "🍽️ SmartChef 智能厨神助手" if is_zh else "🍽️ SmartChef: AI Cooking Assistant",
    "city": "📍 你所在的城市（可中文）" if is_zh else "📍 Your city (in Chinese or English)",
    "ingredients": "🍅 你今天有哪些食材呢？（逗号分隔）" if is_zh else "🍅 What ingredients do you have? (comma-separated)",
    "diet": "🥗 有没有饮食偏好（可选）？" if is_zh else "🥗 Any dietary preference (optional)?",
    "goal": "🎯 你今天的健康目标是？" if is_zh else "🎯 What's your health goal today?",
    "btn": "👨‍🍳 生成饮食建议" if is_zh else "👨‍🍳 Generate Cooking Advice",
    "answer": "✅ Chef助手回答：" if is_zh else "✅ Chef Assistant's reply:",
    "ask_subtitle": "💬 有其他饮食问题想问Chef助手吗？" if is_zh else "💬 Any cooking/nutrition question for Chef?",
    "question": "🥣 聊聊你的饮食小困惑～" if is_zh else "🥣 Ask Chef something...",
    "send": "发送 / Send",
    "history": "📜 历史问答记录" if is_zh else "📜 Conversation History",
    "video_title": "🎥 Chef推荐的视频" if is_zh else "🎥 Video Suggestions from Chef"
}

# 标题与城市输入
st.title(T["title"])
city_name = st.text_input(T["city"], value="上海")
display_weather_and_recipes(city_name, is_zh)

# 主输入区
ingredients = st.text_area(T["ingredients"], placeholder="e.g. 鸡胸肉, 西兰花, 洋葱")
col1, col2 = st.columns(2)
diet = col1.text_input(T["diet"], placeholder="如：低碳、高蛋白、素食" if is_zh else "e.g. low-carb, high-protein")
goal = col2.text_input(T["goal"], placeholder="如：减脂、健身恢复" if is_zh else "e.g. fat loss, muscle gain")

# 生成建议
if st.button(T["btn"]):
    prompt = f"""
我今天的食材是：{ingredients}
饮食偏好：{diet}
健康目标：{goal}

请你作为营养顾问“Chef助手”，语气轻松温暖、俏皮有趣但专业，结合以上内容，帮我生成：
1️⃣ 推荐食谱（Recipe Suggestion）
请根据食材、饮食偏好和健康目标，推荐 1~2 个适合的菜品，并附上详细且有食欲的描述（如风味、口感、适合人群等）。
2️⃣ 营养价值解析（Nutritional Insight）
对推荐菜品的营养组成进行简要解释，比如蛋白质、碳水、脂肪、纤维、维生素等含量及其健康益处，突出与健康目标（如减脂/增肌）之间的关系。
3️⃣ 个性化搭配建议（Smart Pairing Tips）
在已有食材基础上，推荐额外可以搭配的小食材或调味品，让菜品更均衡或更美味，例如“加点橄榄油会更润”、“再加点魔芋能增强饱腹感”。
4️⃣ 饮食误区与实用提醒（Common Pitfalls & Tips）
温馨提醒用户可能会忽略的饮食误区，例如“别忘了控制酱料用量”、“晚餐别太晚吃”、“燕麦虽好，但加糖太多就失效了”等。
5️⃣ 关怀鼓励话语（Encouragement & Support）
用轻松愉快又带点人情味的语言，对用户进行积极反馈与心理支持，例如：“已经很棒啦～营养搭配这种事，一点点优化就会有大不同！”、“记得吃饭要开心，心情好才是最好的调味料～”

"""
    r = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
        json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}]}
    )
    if r.status_code == 200:
        result = clean_text(r.json()["choices"][0]["message"]["content"])
        st.session_state["chef_result"] = result
    else:
        st.error("❌ Chef助手暂时没能生成建议，请检查API密钥或网络")

# 输出 + 视频 + 朗读
if "chef_result" in st.session_state:
    st.markdown("### ✅ Chef助手给你的建议：")
    st.write(st.session_state["chef_result"])

    with st.expander("🗣️ 朗读这段建议", expanded=True):
        rate = st.slider("语速调节", 120, 240, 160, step=10)
        colr1, colr2 = st.columns(2)
        if colr1.button("🔊 开始朗读"):
            subprocess.Popen(["say", "-r", str(rate), st.session_state["chef_result"]])
        if colr2.button("🛑 停止朗读"):
            subprocess.run(["killall", "say"])

    st.markdown(f"### {T['video_title']}")
    query = " ".join(extract_keywords(st.session_state["chef_result"]))
    videos = recommend_youtube_videos(query)
    if videos:
        for title, link in videos:
            st.markdown(f"- [{title}]({link})")
    else:
        st.info("🍳 Chef助手没找到相关视频，可以换个关键词试试~")

# 问答模块
st.markdown("---")
st.subheader(T["ask_subtitle"])
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

question = st.text_input(T["question"])
if st.button(T["send"]) and question.strip():
    history = "\n".join([f"你：{q}\nChef助手：{a}" for q, a in st.session_state.chat_history[-3:]])
    full_prompt = f"{history}\n你：{question}\nChef助手："
    r = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}", "Content-Type": "application/json"},
        json={"model": "deepseek-chat", "messages": [{"role": "user", "content": full_prompt}]}
    )
    if r.status_code == 200:
        reply = clean_text(r.json()["choices"][0]["message"]["content"])
        st.session_state.chat_history.append((question, reply))
        st.success(T["answer"])
        st.write(reply)

# 展示历史记录
if st.session_state.chat_history:
    st.markdown("---")
    st.subheader(T["history"])
    for q, a in reversed(st.session_state.chat_history[-5:]):
        st.markdown(f"**🧍 你：** {q}")
        st.markdown(f"**👨‍🍳 Chef助手：** {a}")
