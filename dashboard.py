import streamlit as st
import math
import requests
import json

# JSONbin.io 配置
JSONBIN_API_KEY = st.secrets["JSONBIN_API_KEY"]
JSONBIN_BIN_ID = st.secrets["JSONBIN_BIN_ID"]

# JSONbin.io 操作函数
def load_apps():
    url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}/latest"
    headers = {
        "X-Master-Key": JSONBIN_API_KEY
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['record']['apps']
    return []

def save_apps(apps):
    url = f"https://api.jsonbin.io/v3/b/{JSONBIN_BIN_ID}"
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": JSONBIN_API_KEY
    }
    data = {"apps": apps}
    response = requests.put(url, json=data, headers=headers)
    return response.status_code == 200

def save_app(name, url, color):
    apps = load_apps()
    new_app = {
        'name': name,
        'url': url,
        'color': color,
        'position': len(apps) + 1
    }
    apps.append(new_app)
    save_apps(apps)

def update_app(index, name, url, color):
    apps = load_apps()
    apps[index]['name'] = name
    apps[index]['url'] = url
    apps[index]['color'] = color
    save_apps(apps)

def delete_app(index):
    apps = load_apps()
    del apps[index]
    for i, app in enumerate(apps):
        app['position'] = i + 1
    save_apps(apps)

def move_app(index, direction):
    apps = load_apps()
    if direction == 'up' and index > 0:
        apps[index], apps[index-1] = apps[index-1], apps[index]
    elif direction == 'down' and index < len(apps) - 1:
        apps[index], apps[index+1] = apps[index+1], apps[index]
    for i, app in enumerate(apps):
        app['position'] = i + 1
    save_apps(apps)

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
        apps = load_apps()
        for i, app in enumerate(apps):
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            with col1:
                st.write(f"{app['name']} - {app['url']}")
            with col2:
                if st.button(f"编辑", key=f"edit_{i}"):
                    st.session_state.editing_app = app
                    st.session_state.editing_app_index = i
            with col3:
                if st.button(f"删除", key=f"delete_{i}"):
                    delete_app(i)
                    st.rerun()
            with col4:
                if st.button("↑", key=f"up_{i}"):
                    move_app(i, 'up')
                    st.rerun()
            with col5:
                if st.button("↓", key=f"down_{i}"):
                    move_app(i, 'down')
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
                    update_app(st.session_state.editing_app_index, name, url, color)
                    del st.session_state.editing_app
                    del st.session_state.editing_app_index
                    st.success("应用已更新!")
                    st.rerun()

if __name__ == "__main__":
    main()
