import json
import sqlite3

# 创建数据库连接
def get_db_connection():
    conn = sqlite3.connect('apps.db')
    return conn

# 读取 JSON 数据
def load_json_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# 将数据插入到 SQLite 数据库
def insert_data_to_db(data):
    conn = get_db_connection()
    for app in data:
        # 获取当前应用数量
        current_count = conn.execute('SELECT COUNT(*) FROM apps').fetchone()[0]
        position = current_count + 1  # 设置 position 为当前数量 + 1
        conn.execute('INSERT INTO apps (name, url, color, position) VALUES (?, ?, ?, ?)', 
                     (app['name'], app['url'], app['color'], position))
    conn.commit()
    conn.close()

# 主函数
def main():
    json_data = load_json_data('apps.json')  # 确保路径正确
    insert_data_to_db(json_data)
    print("数据迁移完成！")

if __name__ == "__main__":
    main() 