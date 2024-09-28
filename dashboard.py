import streamlit as st
import json
import math
import hashlib

# 加载应用数据
def load_apps():
    try:
        with open('apps.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# 保存应用数据
def save_apps(apps):
    with open('apps.json', 'w') as f:
        json.dump(apps, f)

# 简单的密码哈希函数
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# 验证用户
def authenticate(username, password):
    return username == "alantany" and hash_password(password) == hash_password("Mikeno01")

# 登录页面
def login_page():
    st.title("登录")
    username = st.text_input("用户名")
    password = st.text_input("密码", type="password")
    if st.button("登录"):
        if authenticate(username, password):
            st.session_state.logged_in = True
            st.success("登录成功！")
            st.rerun()
        else:
            st.error("用户名或密码错误")

# 主页面
def main():
    st.set_page_config(layout="wide")
    
    if 'logged_in' not in st.session_state or not st.session_state.logged_in:
        login_page()
    else:
        # 创建两个标签页
        tab1, tab2 = st.tabs(["应用仪表板", "管理应用"])
        
        with tab1:
            st.title("工具仪表板")

            # 加载现有应用
            apps = load_apps()

            # 自定义CSS来美化布局
            st.markdown("""
            <style>
            .stApp {
                background-color: #f2f2f7;
            }
            .app-icon {
                width: 60px;
                height: 60px;
                margin: 0 auto 10px;
                border-radius: 15px;
                display: flex;
                justify-content: center;
                align-items: center;
                font-size: 30px;
                color: white;
            }
            .app-name {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
                font-weight: 500;
                font-size: 14px;
                color: #1c1c1e;
                text-align: center;
            }
            .app-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                padding: 10px;
                transition: transform 0.3s;
            }
            .app-container:hover {
                transform: scale(1.05);
            }
            </style>
            """, unsafe_allow_html=True)

            # 显示现有应用
            rows = math.ceil(len(apps) / 4)
            for i in range(rows):
                cols = st.columns(4)
                for j in range(4):
                    idx = i * 4 + j
                    if idx < len(apps):
                        app = apps[idx]
                        with cols[j]:
                            icon_color = app.get('color', '#007AFF')
                            icon_text = app['name'][0].upper()
                            st.markdown(f"""
                            <a href="{app['url']}" target="_blank" style="text-decoration: none; color: inherit;">
                                <div class="app-container">
                                    <div class="app-icon" style="background-color: {icon_color};">
                                        {icon_text}
                                    </div>
                                    <div class="app-name">{app['name']}</div>
                                </div>
                            </a>
                            """, unsafe_allow_html=True)

        with tab2:
            st.title("管理应用")

            # 添加新应用的表单
            with st.form("new_app"):
                st.subheader("添加新应用")
                col1, col2 = st.columns(2)
                with col1:
                    name = st.text_input("应用名称")
                    url = st.text_input("应用URL")
                with col2:
                    color = st.color_picker("图标颜色", value='#007AFF')
                submitted = st.form_submit_button("添加")
                if submitted and name and url:
                    apps.append({"name": name, "url": url, "color": color})
                    save_apps(apps)
                    st.success("应用已添加!")
                    st.rerun()

            # 管理现有应用
            st.subheader("管理现有应用")
            for idx, app in enumerate(apps):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.write(f"{app['name']} - {app['url']}")
                with col2:
                    if st.button(f"编辑", key=f"edit_{idx}"):
                        st.session_state.editing_app = app
                        st.session_state.editing_index = idx
                with col3:
                    if st.button(f"删除", key=f"delete_{idx}"):
                        apps.pop(idx)
                        save_apps(apps)
                        st.rerun()

            # 编辑应用
            if 'editing_app' in st.session_state:
                st.subheader("编辑应用")
                with st.form("edit_app_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        name = st.text_input("应用名称", value=st.session_state.editing_app['name'])
                        url = st.text_input("应用URL", value=st.session_state.editing_app['url'])
                    with col2:
                        color = st.color_picker("图标颜色", value=st.session_state.editing_app.get('color', '#007AFF'))
                    if st.form_submit_button("保存修改"):
                        apps[st.session_state.editing_index] = {"name": name, "url": url, "color": color}
                        save_apps(apps)
                        del st.session_state.editing_app
                        del st.session_state.editing_index
                        st.success("应用已更新!")
                        st.rerun()

        if st.button("登出"):
            st.session_state.logged_in = False
            st.rerun()

if __name__ == "__main__":
    main()