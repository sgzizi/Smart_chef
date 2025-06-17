import streamlit as st
import os
import re
import requests
import subprocess
import emoji
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

# 提取 AI 回复中的 Recipe Suggestion 段落内容
def extract_recipe_suggestion_section(full_text):
    pattern = r"\*\*Recipe Suggestion\*\*(.*?)\n\s*\n"
    match = re.search(pattern, full_text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return full_text  # 如果找不到段落，就退回用全文


# 只提取类似“lemon garlic salmon”风格的菜名短语
def extract_keywords_from_recipe(recipe_text):
    lines = recipe_text.splitlines()
    dish_keywords = []

    for line in lines:
        line = line.strip()
        # 匹配以大写字母开头的短语（常见于英文菜名）
        matches = re.findall(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})\b", line)
        for match in matches:
            match_clean = match.strip()
            if match_clean.lower() not in ['try', 'this', 'that', 'these', 'those', 'here', 'there', 'it']:
                dish_keywords.append(match_clean)

    return list(dict.fromkeys(dish_keywords))[:3] or ["Healthy Recipe"]

def remove_emojis(text):
    return emoji.replace_emoji(text, replace='')


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
# 分类天气
def categorize_weather(condition, temp):
    condition = condition.lower()
    try:
        temp = int(temp)  # 确保 temp 是整数类型
    except ValueError:
        temp = 0  # 如果 temp 不能转换为整数，设置为默认值 0

    if "rain" in condition or "雨" in condition:
        return "rain"
    elif temp <= 10:
        return "cold"
    elif temp >= 28:
        return "hot"
    else:
        return "mild"


# 展示天气和推荐
def display_weather_only(city_name, is_zh=True):
    # 根据语言切换天气提示文本
    weather_title = "🌦 当前天气" if is_zh else "🌦 Current Weather"
    weather_info = f"📍 {city_name} 当前天气：" if is_zh else f"📍 {city_name} Current weather:"

    # 显示标题和天气
    st.markdown(f"## {weather_title}")
    condition, temp = get_weather(city_name, is_zh)
    st.info(f"{weather_info} {condition}")

    # 小贴士提示
    tip_map = {
        "rain": "🌧️ 雨天湿气重，别忘了喝点热汤，保持身体温暖哦～" if is_zh else "🌧️ Rainy day! Stay warm and drink some hot soup to keep the moisture away.",
        "cold": "❄️ 天气寒冷，记得进补，多吃温热食物增强抵抗力～" if is_zh else "❄️ It's chilly! Warm up with nourishing foods to boost immunity.",
        "hot": "☀️ 天气炎热，注意补水，多吃些清爽蔬果更舒服～" if is_zh else "☀️ Hot weather today! Stay hydrated and eat more refreshing fruits and veggies.",
        "mild": "🌤️ 天气舒适，饭后不妨散散步，有助消化也有好心情～" if is_zh else "🌤️ Nice weather! How about a relaxing walk after your meal to aid digestion?"
    }
    _, weather_type = get_weather(city_name, is_zh)
    st.success(
        tip_map.get(weather_type, "🍽️ 保持好心情，吃顿开心饭！" if is_zh else "🍽️ Enjoy your meal and stay cheerful!"))


# 获取天气信息并将其传递到prompt中
def get_weather_info(city_name, is_zh=True):
    condition, temp = get_weather(city_name, is_zh)
    weather_type = categorize_weather(condition, temp)

    # 小贴士提示
    tip_map = {
        "rain": "🌧️ 雨天湿气重，别忘了喝点热汤，保持身体温暖哦～" if is_zh else "🌧️ Rainy day! Stay warm and drink some hot soup to keep the moisture away.",
        "cold": "❄️ 天气寒冷，记得进补，多吃温热食物增强抵抗力～" if is_zh else "❄️ It's chilly! Warm up with nourishing foods to boost immunity.",
        "hot": "☀️ 天气炎热，注意补水，多吃些清爽蔬果更舒服～" if is_zh else "☀️ Hot weather today! Stay hydrated and eat more refreshing fruits and veggies.",
        "mild": "🌤️ 天气舒适，饭后不妨散散步，有助消化也有好心情～" if is_zh else "🌤️ Nice weather! How about a relaxing walk after your meal to aid digestion?"
    }

    # 获取天气建议
    weather_tip = tip_map.get(weather_type,
        "🍽️ 保持好心情，吃顿开心饭！" if is_zh else "🍽️ Enjoy your meal and stay cheerful!")

    return f"当前天气：{condition}, {temp}°C", weather_tip


# 多语言支持
language = st.selectbox("🌐 Language / 语言", ["中文", "English"])
is_zh = language == "中文"

T = {
    "title": "🍽️ SmartChef 智能厨神助手" if is_zh else "🍽️ SmartChef: AI Cooking Assistant",
    "city": "📍 你所在的城市" if is_zh else "📍 Your city (in Chinese or English)",
    "ingredients": "🍅 你今天有哪些食材呢？（逗号分隔）" if is_zh else "🍅 What ingredients do you have? (comma-separated)",
    "diet": "🥗 有没有饮食偏好？" if is_zh else "🥗 Any dietary preference ?",
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
city_name = st.text_input(T["city"], value="Sydney")
display_weather_only(city_name, is_zh)
weather_str, weather_tip = get_weather_info(city_name, is_zh)

# 主输入区
ingredients = st.text_area(T["ingredients"], placeholder="e.g. 鸡胸肉, 西兰花, 洋葱" if is_zh else "e.g. Chicken breast, broccoli, onion")
col1, col2 = st.columns(2)
diet = col1.text_input(T["diet"], placeholder="如：低碳、高蛋白、素食" if is_zh else "e.g. low-carb, high-protein")
goal = col2.text_input(T["goal"], placeholder="如：减脂、健身恢复" if is_zh else "e.g. fat loss, muscle gain")

# 生成建议
if st.button(T["btn"]):
    prompt = f"""
    城市：{city_name}
    天气：{weather_str} | {weather_tip}
    我今天的食材是：{ingredients}
    饮食偏好：{diet}
    健康目标：{goal}

    As your nutrition advisor, “Chef Assistant,” I’ll provide recommendations in a light, warm, playful yet professional tone, tailored to your city's weather conditions:

    1️⃣ **Recipe Suggestion**  
    Based on the ingredients, dietary preferences, and health goals mentioned above, I’ll recommend 1–2 dishes that perfectly match your needs. I’ll provide an incredibly tempting description to help you understand their flavor, texture, and who they’re best suited for.

    2️⃣ **Recipe Steps**  
    In addition to recommending dishes, I’ll provide a step-by-step cooking guide. From chopping the ingredients to plating the final dish, I’ll include the exact grams of each ingredient and what to do at every stage (including spices and side dishes) to make the process simple, so you can enjoy cooking effortlessly.

    3️⃣ **Seasonal Dish Suggestions**  
    Based on your city’s weather and climate, I’ll recommend seasonal dishes that align with the city’s characteristics and seasonal changes. Whether it's the refreshing summer dishes or hearty winter meals, I’ll suggest the best dishes to match your seasonal cravings!

    4️⃣ **Nutritional Insight**  
    I’ll provide a brief nutritional breakdown of the recommended dishes, detailing their protein, carbohydrates, fats, fibers, and vitamins. I’ll also explain how these nutrients benefit your health and emphasize how they help you achieve your health goals, such as fat loss or muscle gain.

    5️⃣ **Smart Pairing Tips**  
    Based on the ingredients you currently have, I’ll offer additional tips to pair them with other ingredients or spices to make the dish more balanced and flavorful. For example, “Adding olive oil will increase smoothness,” or “Adding konjac can enhance satiety.

    6️⃣ **Common Pitfalls & Tips**  
    I’ll gently remind you of common dietary pitfalls, such as “Don’t forget to control the amount of sauce,” “Try not to eat too late at night,” or “Oats are great, but too much sugar will negate their health benefits.” These small tips will help you better control your diet and achieve your health goals.

    7️⃣ **Encouragement & Support**  
    You’re already doing great! Nutritional balancing is an ongoing process, and each small adjustment leads to bigger changes. Remember, eating is not just about health—it’s about enjoying life, and a good mood is the best seasoning! Keep it up, and together we’ll head towards a healthier version of yourself!
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
# Add translated content for reading section in T dictionary
T_reading = {
    "chef_result_title": "### ✅ Chef助手给你的建议：" if is_zh else "### ✅ Chef Assistant's suggestions:",
    "start_reading_button": "🔊 开始朗读" if is_zh else "🔊 Start Reading",
    "stop_reading_button": "🛑 停止朗读" if is_zh else "🛑 Stop Reading"
}

if "chef_result" in st.session_state:
    st.markdown(T_reading["chef_result_title"])
    st.write(st.session_state["chef_result"])

    with st.expander("🗣️ 朗读这段建议"if is_zh else 'Read this suggestion out loud', expanded=True):
        rate = st.slider("语速调节"if is_zh else 'Speed Control', 120, 240, 160, step=10)
        colr1, colr2 = st.columns(2)

        if colr1.button(T_reading["start_reading_button"]):
            clean_for_speech = remove_emojis(st.session_state["chef_result"])
            subprocess.Popen(["say", "-r", str(rate), clean_for_speech])

        if colr2.button(T_reading["stop_reading_button"]):
            subprocess.run(["killall", "say"])

    st.markdown(f"### {T['video_title']}")

    # 提取 Recipe Suggestion 部分
    suggestion_text = extract_recipe_suggestion_section(st.session_state["chef_result"])

    # 从中提取菜名作为搜索关键词
    query = " ".join(extract_keywords_from_recipe(suggestion_text))

    # （可选调试）展示提取结果
    st.write("🎯 视频搜索关键词："if is_zh else 'Video search keywords:', query)

    # 根据菜名搜索视频
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
