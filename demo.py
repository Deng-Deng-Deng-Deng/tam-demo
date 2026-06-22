import streamlit as st
from openai import OpenAI

# ==========================================
# 1. 界面与前置干预 (降低 PR, 提升 Trust, PEOU)
# ==========================================
st.set_page_config(page_title="智能导诊助手", page_icon="🏥")
st.title("🏥 智能导诊助手 Demo")

# 醒目的免责与隐私声明
st.info("💡 隐私与安全声明：本系统仅供学术调研使用，您的对话数据不会被留存。导诊建议不作为最终医疗诊断，请务必结合线下医生面诊。")

# ==========================================
# 2. 配置大模型 API
# ==========================================
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY")
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url="https://api.deepseek.com")

# ==========================================
# 3. 设定 AI 人设 (干预 PA, PE, EX, IQ)
# ==========================================
SYSTEM_PROMPT = """你是一个专业、温暖且富有同理心的三甲医院导诊助手。
你的任务是通过对话了解患者的症状，并推荐合适的就诊科室。

请严格遵循以下原则：
1. 情感共情 (Empathy)：面对患者的病痛描述，第一句话必须表达理解和关怀（例如："听到您这么难受，我感到很抱歉"）。
2. 拟人化对话 (Anthropomorphism)：使用自然、友善的人类口吻，不要像冷冰冰的机器。
3. 信息追问 (Information Quality)：如果患者描述模糊，请每次只提出1-2个关键的医学追问（如部位、时间、伴随症状）。
4. 可解释性 (Explainability)：在给出建议科室时，必须清晰解释医学逻辑（"因为您出现了...症状，这可能是...，因此我建议您优先前往【XX科】"）。
5. 限制轮数：争取在3轮对话内给出最终的科室建议，并附上简单的就医注意事项。
"""

# ==========================================
# 4. 初始化对话状态
# ==========================================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "assistant",
            "content": "您好呀！我是您的导诊小助手。去医院不知道该挂什么科？别担心，请详细跟我说说您今天哪里不舒服。",
        },
    ]

# 遍历并显示历史对话（过滤掉隐藏的 System Prompt）
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

# ==========================================
# 5. 核心对话与流式输出交互
# ==========================================
if prompt := st.chat_input("请输入您的症状，例如：我今天早上开始肚子疼..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=st.session_state.messages,
                stream=True,
            )

            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    full_response += chunk.choices[0].delta.content
                    message_placeholder.markdown(full_response + "▌")

            message_placeholder.markdown(full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )

        except Exception as e:
            st.error(f"系统开小差了，请检查网络或 API 设置：{e}")
