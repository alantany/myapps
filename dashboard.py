import streamlit as st
import sqlite3
import math

# 创建数据库连接
def get_db_connection():
    conn = sqlite3.connect('apps.db')
    conn.row_factory = sqlite3.Row
    return conn

# 初始化数据库
def init_db():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS apps (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            url TEXT NOT NULL,
            color TEXT NOT NULL,
            position INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# 加载应用数据
def load_apps():
    conn = get_db_connection()
    apps = conn.execute('SELECT * FROM apps ORDER BY position').fetchall()
    conn.close()
    return apps

# 保存新应用
def save_app(name, url, color):
    conn = get_db_connection()
    max_position = conn.execute('SELECT MAX(position) FROM apps').fetchone()[0] or 0
    conn.execute('INSERT INTO apps (name, url, color, position) VALUES (?, ?, ?, ?)',
                 (name, url, color, max_position + 1))
    conn.commit()
    conn.close()

# 更新应用
def update_app(id, name, url, color):
    conn = get_db_connection()
    conn.execute('UPDATE apps SET name = ?, url = ?, color = ? WHERE id = ?',
                 (name, url, color, id))
    conn.commit()
    conn.close()

# 删除应用
def delete_app(id):
    conn = get_db_connection()
    conn.execute('DELETE FROM apps WHERE id = ?', (id,))
    conn.commit()
    conn.close()

# 移动应用位置
def move_app(id, direction):
    conn = get_db_connection()
    current_app = conn.execute('SELECT * FROM apps WHERE id = ?', (id,)).fetchone()
    if direction == 'up':
        other_app = conn.execute('SELECT * FROM apps WHERE position < ? ORDER BY position DESC LIMIT 1', 
                                 (current_app['position'],)).fetchone()
    else:
        other_app = conn.execute('SELECT * FROM apps WHERE position > ? ORDER BY position ASC LIMIT 1', 
                                 (current_app['position'],)).fetchone()
    
    if other_app:
        conn.execute('UPDATE apps SET position = ? WHERE id = ?', (other_app['position'], current_app['id']))
        conn.execute('UPDATE apps SET position = ? WHERE id = ?', (current_app['position'], other_app['id']))
        conn.commit()
    conn.close()

# 主页面
def main():
    st.set_page_config(layout="wide")
    init_db()
    
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
        for app in apps:
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            with col1:
                st.write(f"{app['name']} - {app['url']}")
            with col2:
                if st.button(f"编辑", key=f"edit_{app['id']}"):
                    st.session_state.editing_app = app
            with col3:
                if st.button(f"删除", key=f"delete_{app['id']}"):
                    delete_app(app['id'])
                    st.rerun()
            with col4:
                if st.button("↑", key=f"up_{app['id']}"):
                    move_app(app['id'], 'up')
                    st.rerun()
            with col5:
                if st.button("↓", key=f"down_{app['id']}"):
                    move_app(app['id'], 'down')
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
                    update_app(st.session_state.editing_app['id'], name, url, color)
                    del st.session_state.editing_app
                    st.success("应用已更新!")
                    st.rerun()

if __name__ == "__main__":
    main()