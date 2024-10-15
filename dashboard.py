import streamlit as st
import math
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# Firebase 配置信息
firebase_config = {
    "apiKey": "AIzaSyDpAamnXrfgiRl6T7j1gYuM-Lfb7mNtrfU",
    "authDomain": "kids-coder.firebaseapp.com",
    "databaseURL": "https://kids-coder.firebaseio.com",
    "projectId": "kids-coder",
    "storageBucket": "kids-coder.appspot.com",
    "messagingSenderId": "816808155181",
    "appId": "1:816808155181:web:f361e52b77001d01f300a4"
}

# 初始化 Firebase
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-adminsdk.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': firebase_config['databaseURL']
    })

# 获取数据库引用
ref = db.reference('apps')

# 加载应用数据
def load_apps():
    apps = ref.get()
    return [app for app in apps.values()] if apps else []

# 保存新应用
def save_app(name, url, color):
    apps = load_apps()
    new_app = {
        'name': name,
        'url': url,
        'color': color,
        'position': len(apps) + 1
    }
    ref.push(new_app)

# 更新应用
def update_app(key, name, url, color):
    ref.child(key).update({
        'name': name,
        'url': url,
        'color': color
    })

# 删除应用
def delete_app(key):
    ref.child(key).delete()

# 移动应用位置
def move_app(key, direction):
    apps = ref.get()
    app_keys = list(apps.keys())
    app_index = app_keys.index(key)
    
    if direction == 'up' and app_index > 0:
        swap_key = app_keys[app_index - 1]
    elif direction == 'down' and app_index < len(app_keys) - 1:
        swap_key = app_keys[app_index + 1]
    else:
        return
    
    app1 = apps[key]
    app2 = apps[swap_key]
    app1['position'], app2['position'] = app2['position'], app1['position']
    
    ref.update({
        key: app1,
        swap_key: app2
    })

# 主页面
def main():
    st.set_page_config(layout="wide")
    
    # 创建两个标签页
    tab1, tab2 = st.tabs(["我的应用", "管理应用"])
    
    with tab1:
        st.title("我的应用")

        # 加载现有应用
        apps = load_apps()

        # 自定义CSS来美化布局
        st.markdown("""
        <style>
        .stApp {
            background-color: #f2f2f7;
        }
        .app-icon {
            width: 120px;
            height: 120px;
            margin: 0 auto 20px;
            border-radius: 30px;
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 60px;
            color: white;
        }
        .app-name {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
            font-weight: 500;
            font-size: 24px;
            color: #1c1c1e;
            text-align: center;
            margin-top: 10px;
        }
        .app-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 20px;
            transition: transform 0.3s;
            margin-bottom: 20px;
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
                        icon_color = app['color']
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
                save_app(name, url, color)
                st.success("应用已添加!")
                st.rerun()

        # 管理现有应用
        st.subheader("管理现有应用")
        apps = ref.get()
        if apps:
            for key, app in apps.items():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
                with col1:
                    st.write(f"{app['name']} - {app['url']}")
                with col2:
                    if st.button(f"编辑", key=f"edit_{key}"):
                        st.session_state.editing_app = app
                        st.session_state.editing_app_key = key
                with col3:
                    if st.button(f"删除", key=f"delete_{key}"):
                        delete_app(key)
                        st.rerun()
                with col4:
                    if st.button("↑", key=f"up_{key}"):
                        move_app(key, 'up')
                        st.rerun()
                with col5:
                    if st.button("↓", key=f"down_{key}"):
                        move_app(key, 'down')
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
                    color = st.color_picker("图标颜色", value=st.session_state.editing_app['color'])
                if st.form_submit_button("保存修改"):
                    update_app(st.session_state.editing_app_key, name, url, color)
                    del st.session_state.editing_app
                    del st.session_state.editing_app_key
                    st.success("应用已更新!")
                    st.rerun()

if __name__ == "__main__":
    main()
