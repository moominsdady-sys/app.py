import streamlit as st
import pandas as pd
from openai import OpenAI
from datetime import datetime
import pytz
import requests

# 1. ตั้งค่าหน้าเว็บธีมมืดและขยายหน้าจอกว้างสไตล์เกมเทคคูน
st.set_page_config(page_title="👑 Gold Mine Commander - Cloud AI", layout="wide")

# ==============================================================================
# 2. DATA BRIDGE PIPELINE (เปิดประตูเชื่อมดึงสัญญาณสด)
# ==============================================================================
FIREBASE_URL = "http://restful-api.dev"

try:
    response = requests.get(FIREBASE_URL).json()
    my_mine = None
    for obj in response:
        # ระบบจะค้นหาและดึงข้อมูลของพอร์ตนายท่านมาแสดงผลอัตโนมัติ
        if obj.get('name') and str(obj.get('name')).startswith("gold_mine_"):
            my_mine = obj['data']
            break
            
    if my_mine:
        acc_data = my_mine["account_info"]
        open_positions = my_mine["open_positions"] if my_mine["open_positions"] is not None else []
        mine_stats = my_mine["mine_stats"]
        status_msg = f"⚡ ตรวจพบสัญญาณขุดอัปเดตเรียลไทม์ล่าสุดเมื่อ: {mine_stats['last_update']}"
    else:
        raise Exception("Waiting sync")
    
    bkk_time = datetime.now(pytz.timezone('Asia/Bangkok')).hour
    if 14 <= bkk_time < 20: mine_stats["session"] = "🇬🇧 London Session (เหมืองยุโรปกำลังขุดหนัก)"
    elif 20 <= bkk_time or bkk_time < 4: mine_stats["session"] = "🇺🇸 New York Session (ตลาดหลักผันผวนสูงมาก!)"
    else: mine_stats["session"] = "🇯🇵 Tokyo/Sydney Session (ช่วงเวลาฟาร์มเหมืองเงียบๆ)"
except:
    # โหมดจำลองความปลอดภัยหากเครื่องคอมนอกยังไม่ได้กดส่งสัญญาณ
    acc_data = {"login": "กำลังรอซิงก์พอร์ต...", "balance": 0, "equity": 0, "margin_free": 0, "margin_level": 0}
    open_positions = []
    mine_stats = {"current_dd": 0, "max_dd_val": 4.52, "max_dd_date": "12/06/2026", "total_buy_lot": 0, "total_sell_lot": 0, "total_lot": 0, "spread": 0, "session": "-"}
    status_msg = "⏳ กำลังรอเปิดเครื่องส่งสัญญาณคลื่นวิทยุจากเครื่องคอมนอกหลังบ้าน..."

# ==============================================================================
# 3. INTERFACE DESIGN LAYOUT (การจัดแถวและคอลัมน์)
# ==============================================================================
with st.sidebar:
    st.header("👑 ศูนย์ตั้งค่าความปลอดภัย")
    openai_key = st.text_input("รหัสสมอง AI (OpenAI API Key):", type="password")
    st.markdown("---")
    st.caption("ระบบเชื่อมพอร์ตเหมืองทองข้ามคลาวด์อัตโนมัติ")

st.title("👑 Gold Mine Commander: AI Cloud Manager")
st.caption(status_msg)
st.markdown("---")

col_dash, col_3d, col_ai = st.columns([3, 1.8, 2])

# --- [คอลัมน์ที่ 1]: ตารางสรุปแบบ Row/Column ---
with col_dash:
    st.subheader("📊 รายงานสถานะการผลิตในเหมืองทอง")
    r1_c1, r1_c2, r1_c3 = st.columns(3)
    r1_c1.metric("💰 ทุนในคลังทั้งหมด (Balance)", f"${acc_data['balance']:,}")
    r1_c2.metric("💎 มูลค่าสุทธิโรงงาน (Equity)", f"${acc_data['equity']:,}")
    r1_c3.metric("⏳ สภาพคล่องการผลิต (Free Margin)", f"${acc_data['margin_free']:,}")
    
    st.markdown(" ")
    r2_c1, r2_c2, r2_c3 = st.columns(3)
    r2_c1.metric("📉 ความเสียหายเรียบลอย (% Current DD)", f"{mine_stats['current_dd']:.2f}%")
    r2_c2.metric("🚨 วิกฤตประวัติศาสตร์ (% Max DD)", f"{mine_stats['max_dd_val']}%", delta=f"เมื่อ {mine_stats['max_dd_date']}", delta_color="inverse")
    r2_c3.metric("⚡ ค่าธรรมเนียมคู่แร่ (Spread XAU)", f"{mine_stats['spread']} Pips")
    
    st.markdown(" ")
    r3_c1, r3_c2, r3_c3, r3_c4 = st.columns(4)
    r3_c1.metric("⚒️ แรงขุดขึ้น (Total Buy Lot)", f"{mine_stats['total_buy_lot']:.2f}")
    r3_c2.metric("⛏️ แรงขุดลง (Total Sell Lot)", f"{mine_stats['total_sell_lot']:.2f}")
    r3_c3.metric("📦 ขนาดสัญญารวม (Total Lot)", f"{mine_stats['total_lot']:.2f}")
    r3_c4.metric("🛡️ เกราะค้ำเหมือง (Margin Level)", f"{acc_data['margin_level']:.1f}%")
    
    st.markdown("### 📑 รายชื่อออเดอร์เหมืองแร่ในปัจจุบัน")
    if open_positions:
        st.dataframe(pd.DataFrame(open_positions), use_container_width=True, hide_index=True)
    else:
        st.info("🚜 ไม่มีคำสั่งขุดเจาะค้าง: เหมืองกำลังสแตนด์บาย")

# --- [คอลัมน์ที่ 2]: ระบบ 3D ซ้อนรูปโครงร่างเหมืองจาก GitHub ---
with col_3d:
    st.subheader("📦 เหมืองจำลอง Live 3D")
    
    # 📌 ลิงก์ดึงข้อมูลโมเดลตรงของนายท่านจาก GitHub (ระบบสแกนอัตโนมัติจากไฟล์ในห้องเรโปเดียวกัน)
    repo_name = st.experimental_user.email if hasattr(st, "experimental_user") else ""
    URL_BG = "bg.glb"
    URL_DIG = "dig.glb"
    URL_TRUCK = "truck.glb"
    
    floating_pnl = sum(p.get('เสบียงเหลว (Profit)', 0.0) for p in open_positions)
    
    vehicle_url = URL_DIG
    animation_mode = ""
    if open_positions:
        animation_mode = "autoplay"
        if floating_pnl >= 0:
            model_status = "⛏️ สถานะ: ขุดเจอสายแร่ทองคำ! (พอร์ตบวก)"
            vehicle_url = URL_DIG
        else:
            model_status = "⚠️ สถานะ: ระบายเสบียงค้ำพอร์ต (พอร์ตลบ)"
            vehicle_url = URL_TRUCK
    else:
        model_status = "🚜 สถานะ: เครื่องจักรสแตนด์บายพอร์ตว่างงาน"
        
    st.caption(model_status)
    
    html_3d_code = f"""
    <script type="module" src="https://unpkg.com"></script>
    <div style="position: relative; width: 100%; height: 350px; background-color: #0f1116; border-radius: 10px;">
        <model-viewer id="mine-viewer" src="{URL_BG}" alt="Gold Mine Background" auto-rotate camera-controls interaction-prompt="none" shadow-intensity="1.5" bounds="tight" camera-orbit="auto auto auto" style="width: 100%; height: 100%;"></model-viewer>
    </div>
    <script>
        const viewer = document.querySelector('#mine-viewer');
        viewer.addEventListener('load', () => {{
            const vScript = document.createElement('model-viewer');
            vScript.setAttribute('src', '{vehicle_url}');
            if('{animation_mode}') vScript.setAttribute('{animation_mode}', '');
            vScript.setAttribute('scale', '0.15 0.15 0.15');
            vScript.setAttribute('style', 'position: absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; background:transparent;');
            viewer.parentElement.appendChild(vScript);
            viewer.addEventListener('camera-change', () => {{ vScript.cameraOrbit = viewer.getCameraOrbit().toString(); }});
        }});
    </script>
    """
    st.components.v1.html(html_3d_code, height=360)
    st.info(f"🕒 เขตพื้นที่ตลาด:\n\n{mine_stats['session']}")

# --- [คอลัมน์ที่ 3]: เลขา AI พลอยคุมเหมืองทอง ---
with col_ai:
    st.subheader("🤖 เลขาเหมืองทอง: พลอย")
    cmd_col1, cmd_col2 = st.columns(2)
    user_query = ""
    
    with cmd_col1:
        if st.button("📊 รายงานสรุปแผน", use_container_width=True):
            user_query = "สรุปรายงานสถานะผลิตและสรุปเงินทุนของเหมืองตอนนี้หน่อย"
    with cmd_col2:
        if st.button("🚨 ตรวจแนวรบเสี่ยง", use_container_width=True):
            user_query = "ประเมินวิเคราะห์จุดความเสี่ยงอันตรายของพอร์ตและค่าล็อตทั้งหมดตอนนี้"

    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "รายงานตัวค่ะท่านผู้บัญชาการเหมือง! พลอยพร้อมวิเคราะห์พอร์ตจริงแล้วค่ะ!"}]

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]): st.write(msg["content"])

    chat_input = st.chat_input("พิมพ์รหัสคุยกับเลขาพลอย...")
    if chat_input: user_query = chat_input

    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"): st.write(user_query)
        with st.chat_message("assistant"):
            if not openai_key:
                st.warning("❌ กรุณาใส่รหัส OpenAI API Key ที่แถบเมนูด้านซ้ายก่อนนะคะ")
            else:
                with st.spinner("เลขาพลอยกำลังส่งพอร์ตเข้าประมวลผลสมองส่วนกลาง..."):
                    try:
                        client = OpenAI(api_key=openai_key)
                        system_prompt = f"You are an expert AI Trading Manager named 'พลอย' in a Gold Mine tycoon simulation game linked to real MT5 data. Call user 'ผู้บัญชาการ' or 'นายท่าน'. Speak in Thai language."
                        api_messages = [{"role": "system", "content": system_prompt}]
                        for m in st.session_state.messages: api_messages.append({"role": m["role"], "content": m["content"]})
                        res = client.chat.completions.create(model="gpt-4o", messages=api_messages, temperature=0.7)
                        st.write(res.choices.message.content)
                        st.session_state.messages.append({"role": "assistant", "content": res.choices.message.content})
                    except Exception as e: st.error(f"ระบบเชื่อมข้อมูลสมองขัดข้อง: {str(e)}")
