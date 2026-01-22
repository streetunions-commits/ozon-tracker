#!/usr/bin/env python3
"""
🤖 OZON TRACKER MASTER - ПОЛНАЯ АВТОМАТИЗАЦИЯ
Скачивает из Google Drive → Обновляет → Запускает сервер
Просто запустите один раз - и забудьте о проблемах!
"""

import os
import sys
import json
import subprocess
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime

# ============================================================================
# КОНФИГУРАЦИЯ
# ============================================================================

FOLDER_ID = "1OjTOfrm15gp_v0q6HADS-yfrO7KyMcQU"
FILE_NAME = "server.py"
LOG_FILE = "tracker.log"

# ============================================================================
# ЛОГИРОВАНИЕ
# ============================================================================

def log(message, level="INFO"):
    """Логирует сообщение в консоль и файл"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if level == "INFO":
        icon = "ℹ️"
    elif level == "SUCCESS":
        icon = "✅"
    elif level == "ERROR":
        icon = "❌"
    elif level == "WARNING":
        icon = "⚠️"
    else:
        icon = "📝"
    
    msg = f"[{timestamp}] {icon} {message}"
    print(msg)
    
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(msg + "\n")
    except:
        pass

# ============================================================================
# СКАЧИВАНИЕ ФАЙЛА С GOOGLE DRIVE
# ============================================================================

def download_from_drive(file_id, filename):
    """Скачивает файл с Google Drive"""
    log(f"📥 Скачивание {filename} с Google Drive...", "INFO")
    
    try:
        # Google Drive URL для скачивания
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
        
        # Скачиваем с перенаправлениями
        request = urllib.request.Request(url)
        request.add_header('User-Agent', 'Mozilla/5.0')
        
        response = urllib.request.urlopen(request, timeout=30)
        content = response.read()
        
        # Сохраняем файл
        with open(filename, 'wb') as f:
            f.write(content)
        
        log(f"✓ Файл {filename} скачан ({len(content)} байт)", "SUCCESS")
        return True
    
    except Exception as e:
        log(f"Ошибка скачивания: {e}", "ERROR")
        return False

# ============================================================================
# ПОЛУЧЕНИЕ ID ФАЙЛА
# ============================================================================

def get_file_id_from_folder(folder_id, filename):
    """Получает ID файла из папки (без авторизации - просто угадываем)"""
    # Используем известный ID файла
    return "1kPVnKD1CfIClRSmhEi02UyroWQgS29wp"

# ============================================================================
# ОБНОВЛЕНИЕ КОДА
# ============================================================================

IMPROVED_SERVER_CODE = '''#!/usr/bin/env python3
"""
🌐 OZON PRODUCT TRACKER - МАСТЕР ВЕРСИЯ
Автоматически обновляется и запускается
"""

import http.server
import socketserver
import json
import sys
import urllib.request
import urllib.error
from urllib.parse import urlparse, parse_qs
from datetime import datetime

OZON_CONFIG = {
    'client_id': '138926',
    'api_key': 'acc74291-a862-4cbb-813b-e33f6ea0fe9d',
    'api_url': 'https://api-seller.ozon.ru'
}

class Database:
    def __init__(self):
        self.products = []
        self.syncs = []
        self.last_sync = None
        self.connection_status = "Инициализация..."
        self.last_error = None
        self.sync_from_ozon()
    
    def sync_from_ozon(self):
        """Синхронизация товаров из Ozon API"""
        try:
            print("\\n" + "="*80)
            print("🔄 СИНХРОНИЗАЦИЯ ТОВАРОВ ИЗ OZON API")
            print("="*80)
            
            self.connection_status = "Подключение..."
            
            url = f"{OZON_CONFIG['api_url']}/v3/product/list"
            print(f"\\n📍 URL: {url}")
            print(f"📍 Client ID: {OZON_CONFIG['client_id']}")
            
            headers = {
                'Client-Id': OZON_CONFIG['client_id'],
                'Api-Key': OZON_CONFIG['api_key'],
                'Content-Type': 'application/json'
            }
            
            data = json.dumps({
                'filter': {'visibility': 'ALL'},
                'limit': 100,
                'offset': 0
            }).encode('utf-8')
            
            print(f"📤 Отправляю запрос...")
            
            req = urllib.request.Request(url, data=data, headers=headers, method='POST')
            
            with urllib.request.urlopen(req, timeout=15) as response:
                response_body = response.read().decode('utf-8')
                
                print(f"📥 Получен ответ ({len(response_body)} байт)")
                
                result = json.loads(response_body)
                
                print(f"📊 Обработка ответа...")
                
                # Попробуем разные варианты структуры
                products_list = []
                
                if 'result' in result:
                    if isinstance(result['result'], dict):
                        if 'products' in result['result']:
                            products_list = result['result']['products']
                        else:
                            # Может быть другой ключ
                            for key in result['result']:
                                if isinstance(result['result'][key], list) and len(result['result'][key]) > 0:
                                    if isinstance(result['result'][key][0], dict):
                                        products_list = result['result'][key]
                                        break
                    elif isinstance(result['result'], list):
                        products_list = result['result']
                
                elif 'products' in result and isinstance(result['products'], list):
                    products_list = result['products']
                
                elif isinstance(result, list):
                    products_list = result
                
                if not products_list:
                    raise Exception(f"Не найдены товары. Структура ответа: {list(result.keys())}")
                
                print(f"✓ Найдено товаров: {len(products_list)}")
                
                self.products = []
                for i, p in enumerate(products_list):
                    try:
                        product = {
                            'id': p.get('product_id') or p.get('id') or i,
                            'sku': p.get('sku') or p.get('offer_id') or 'N/A',
                            'name': p.get('name') or p.get('title') or 'Unknown',
                            'price': p.get('price') or p.get('current_price') or 0,
                            'stock': p.get('stock') or p.get('stocks') or p.get('quantity') or 0,
                            'status': p.get('status') or 'active',
                            'rating': p.get('rating') or p.get('rating_value') or 0
                        }
                        self.products.append(product)
                    except Exception as e:
                        print(f"⚠️ Ошибка товара #{i}: {e}")
                
                print(f"\\n✓ УСПЕШНО! Загружено {len(self.products)} товаров")
                
                self.connection_status = "✓ Подключено"
                self.last_error = None
                
                self.syncs.append({
                    'id': len(self.syncs) + 1,
                    'date': datetime.now().isoformat(),
                    'type': 'full',
                    'products_count': len(self.products),
                    'status': 'success',
                    'error': None
                })
                
                self.last_sync = datetime.now().isoformat()
                print("="*80 + "\\n")
                return True
        
        except urllib.error.HTTPError as e:
            try:
                error_body = e.read().decode('utf-8')
                print(f"❌ HTTP {e.code}: {e.reason}")
                print(f"📋 Ответ: {error_body[:300]}\\n")
                self.last_error = f"HTTP {e.code}: {error_body[:100]}"
            except:
                self.last_error = f"HTTP {e.code}: {e.reason}"
            
            self.connection_status = f"❌ HTTP {e.code}"
            self.syncs.append({
                'id': len(self.syncs) + 1,
                'date': datetime.now().isoformat(),
                'type': 'full',
                'products_count': 0,
                'status': 'error',
                'error': self.last_error
            })
            
            print("="*80 + "\\n")
            return False
        
        except urllib.error.URLError as e:
            error_msg = f"Ошибка сети: {str(e)}"
            print(f"❌ {error_msg}\\n")
            self.last_error = error_msg
            self.connection_status = "❌ Нет интернета"
            
            self.syncs.append({
                'id': len(self.syncs) + 1,
                'date': datetime.now().isoformat(),
                'type': 'full',
                'products_count': 0,
                'status': 'error',
                'error': error_msg
            })
            
            print("="*80 + "\\n")
            return False
        
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Ошибка: {error_msg}\\n")
            self.last_error = error_msg
            self.connection_status = f"❌ {error_msg[:40]}"
            
            self.syncs.append({
                'id': len(self.syncs) + 1,
                'date': datetime.now().isoformat(),
                'type': 'full',
                'products_count': 0,
                'status': 'error',
                'error': error_msg
            })
            
            print("="*80 + "\\n")
            return False

db = Database()

class Handler(http.server.SimpleHTTPRequestHandler):
    
    def do_GET(self):
        path = urlparse(self.path).path
        query = parse_qs(urlparse(self.path).query)
        
        try:
            if path == '/' or path == '/index.html':
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                self.wfile.write(self.get_html().encode('utf-8'))
            
            elif path == '/api/products':
                self.send_json({'total': len(db.products), 'products': db.products})
            
            elif path == '/api/search':
                q = query.get('q', [''])[0].lower()
                results = [p for p in db.products if q in p['name'].lower()]
                self.send_json({'query': q, 'count': len(results), 'products': results})
            
            elif path == '/api/stats':
                self.send_json({
                    'total_products': len(db.products),
                    'total_stock': sum(p['stock'] for p in db.products),
                    'average_price': round(sum(p['price'] for p in db.products) / len(db.products), 2) if db.products else 0,
                    'syncs': len(db.syncs),
                    'last_sync': db.last_sync,
                    'connection_status': db.connection_status,
                    'last_error': db.last_error
                })
            
            elif path == '/api/sync/history':
                self.send_json({'total': len(db.syncs), 'syncs': db.syncs})
            
            elif path == '/api/health':
                self.send_json({
                    'status': 'ok',
                    'products_loaded': len(db.products),
                    'connection_status': db.connection_status,
                    'last_error': db.last_error
                })
            
            else:
                self.send_response(404)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'error': 'Not found'}).encode('utf-8'))
        
        except Exception as e:
            self.send_json({'error': str(e)}, 500)
    
    def do_POST(self):
        path = urlparse(self.path).path
        
        try:
            if path == '/api/sync':
                success = db.sync_from_ozon()
                self.send_json({
                    'success': success,
                    'products_synced': len(db.products),
                    'errors': 0 if success else 1,
                    'message': 'Синхронизация завершена' if success else 'Ошибка синхронизации',
                    'connection_status': db.connection_status,
                    'last_error': db.last_error
                })
            else:
                self.send_response(404)
                self.send_json({'error': 'Not found'})
        
        except Exception as e:
            self.send_json({'error': str(e), 'success': False}, 500)
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode('utf-8'))
    
    def log_message(self, format, *args):
        pass
    
    def get_html(self):
        status_color = '#4CAF50' if '✓' in db.connection_status else '#f44336'
        status_icon = '🟢' if '✓' in db.connection_status else '🔴'
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Ozon Tracker</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: Arial, sans-serif; background: linear-gradient(135deg, #667eea, #764ba2); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ background: white; padding: 30px; border-radius: 10px; text-align: center; margin-bottom: 30px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .header h1 {{ color: #333; margin-bottom: 5px; }}
        .header p {{ color: #666; }}
        .status {{ background: #e8f5e9; color: {status_color}; padding: 10px 15px; border-radius: 5px; display: inline-block; margin-top: 10px; font-weight: bold; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: white; padding: 20px; border-radius: 10px; box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .card h2 {{ color: #667eea; margin-bottom: 15px; }}
        .stat {{ padding: 10px; background: #f5f5f5; border-left: 4px solid #667eea; margin: 10px 0; }}
        .stat-value {{ color: #667eea; font-weight: bold; font-size: 1.3em; }}
        .big-stat {{ text-align: center; font-size: 2.5em; color: #667eea; font-weight: bold; padding: 20px; }}
        input {{ width: 100%; padding: 12px; border: 2px solid #667eea; border-radius: 5px; margin: 10px 0; font-size: 1em; }}
        button {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; padding: 12px 30px; border-radius: 5px; cursor: pointer; width: 100%; margin-top: 10px; font-weight: bold; }}
        button:hover {{ transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; }}
        tr:hover {{ background: #f9f9f9; }}
        .full-width {{ grid-column: 1 / -1; }}
        .search-results {{ margin-top: 10px; padding: 10px; background: #f5f5f5; border-radius: 5px; max-height: 300px; overflow-y: auto; }}
        .search-item {{ padding: 10px; margin: 5px 0; background: white; border-left: 4px solid #667eea; border-radius: 3px; }}
        .spinner {{ display: inline-block; width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #667eea; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 10px; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        .error-box {{ background: #ffebee; color: #c62828; padding: 15px; border-radius: 5px; margin-top: 10px; border-left: 4px solid #c62828; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Ozon Product Tracker</h1>
            <p>Автоматическое управление товарами</p>
            <div class="status">{status_icon} {db.connection_status}</div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>📊 Статистика</h2>
                <div class="big-stat" id="stat-count">-</div>
                <div style="text-align: center; color: #666; margin-bottom: 20px;">Товаров</div>
                <div class="stat">
                    <div>Остаток:</div>
                    <div class="stat-value" id="stat-stock">-</div>
                </div>
                <div class="stat">
                    <div>Ср. цена:</div>
                    <div class="stat-value" id="stat-price">-</div>
                </div>
            </div>

            <div class="card">
                <h2>🔄 Синхронизация</h2>
                <div class="stat">
                    <div>Последняя:</div>
                    <div class="stat-value" id="last-sync" style="font-size: 0.9em;">-</div>
                </div>
                <div class="stat">
                    <div>Всего:</div>
                    <div class="stat-value" id="sync-count">-</div>
                </div>
                <button onclick="sync()">🔄 Синхронизировать</button>
            </div>

            <div class="card">
                <h2>🔗 API Ozon</h2>
                <div class="stat">
                    <div>Статус:</div>
                    <div class="stat-value" style="color: {status_color};" id="api-status">-</div>
                </div>
                <div id="error-msg" class="error-box" style="display: none;"></div>
            </div>
        </div>

        <div class="card full-width">
            <h2>🔍 Поиск товаров</h2>
            <input type="text" id="search" placeholder="Введите название..." onkeyup="search()">
            <div class="search-results" id="results"></div>
        </div>

        <div class="card full-width">
            <h2>📦 Товары</h2>
            <table>
                <thead>
                    <tr><th>ID</th><th>SKU</th><th>Название</th><th>Цена</th><th>Остаток</th></tr>
                </thead>
                <tbody id="products"></tbody>
            </table>
        </div>

        <div class="card full-width">
            <h2>📈 История синхронизаций</h2>
            <table>
                <thead>
                    <tr><th>Дата</th><th>Товаров</th><th>Статус</th><th>Ошибка</th></tr>
                </thead>
                <tbody id="syncs"></tbody>
            </table>
        </div>
    </div>

    <script>
        function loadData() {{
            fetch('/api/products').then(r => r.json()).then(d => {{
                let html = '';
                if (d.products.length === 0) {{
                    html = '<tr><td colspan="5" style="text-align: center; color: #999;">Нажмите "Синхронизировать"</td></tr>';
                }} else {{
                    d.products.forEach(p => {{
                        html += `<tr>
                            <td>${{p.id}}</td>
                            <td>${{p.sku}}</td>
                            <td><strong>${{p.name}}</strong></td>
                            <td>₽${{p.price.toLocaleString()}}</td>
                            <td>${{p.stock}} шт</td>
                        </tr>`;
                    }});
                }}
                document.getElementById('products').innerHTML = html;
            }});
            
            fetch('/api/stats').then(r => r.json()).then(d => {{
                document.getElementById('stat-count').textContent = d.total_products;
                document.getElementById('stat-stock').textContent = (d.total_stock || 0).toLocaleString() + ' шт';
                document.getElementById('stat-price').textContent = '₽' + Math.round(d.average_price || 0).toLocaleString();
                document.getElementById('sync-count').textContent = d.syncs;
                document.getElementById('api-status').textContent = d.connection_status;
                
                if (d.last_error) {{
                    document.getElementById('error-msg').textContent = '⚠️ ' + d.last_error;
                    document.getElementById('error-msg').style.display = 'block';
                }} else {{
                    document.getElementById('error-msg').style.display = 'none';
                }}
                
                if (d.last_sync) {{
                    const date = new Date(d.last_sync).toLocaleString('ru-RU');
                    document.getElementById('last-sync').textContent = date;
                }}
            }});

            fetch('/api/sync/history').then(r => r.json()).then(d => {{
                let html = '';
                d.syncs.forEach(s => {{
                    const date = new Date(s.date).toLocaleString('ru-RU');
                    const status_color = s.status === 'success' ? '#4CAF50' : '#f44336';
                    const status_text = s.status === 'success' ? '✓ Успешно' : '✗ Ошибка';
                    html += `<tr>
                        <td>${{date}}</td>
                        <td>${{s.products_count}}</td>
                        <td><span style="color: ${{status_color}};\">${{status_text}}</span></td>
                        <td>${{s.error || '-'}}</td>
                    </tr>`;
                }});
                document.getElementById('syncs').innerHTML = html || '<tr><td colspan="4">История пуста</td></tr>';
            }});
        }}

        function search() {{
            let q = document.getElementById('search').value;
            if (!q) {{
                document.getElementById('results').innerHTML = '';
                return;
            }}
            fetch('/api/search?q=' + encodeURIComponent(q)).then(r => r.json()).then(d => {{
                let html = '';
                if (d.count === 0) {{
                    html = '<div style="color: #999;">Не найдено</div>';
                }} else {{
                    d.products.forEach(p => {{
                        html += `<div class="search-item"><strong>${{p.name}}</strong><br><small>₽${{p.price.toLocaleString()}} | ${{p.stock}} шт</small></div>`;
                    }});
                }}
                document.getElementById('results').innerHTML = html;
            }});
        }}

        function sync() {{
            const btn = event.target;
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span>Синхронизация...';
            
            fetch('/api/sync', {{method: 'POST'}}).then(r => r.json()).then(d => {{
                setTimeout(() => {{
                    if (d.success) {{
                        alert(`✓ УСПЕШНО!\\n\\nТоваров загружено: ${{d.products_synced}}`);
                    }} else {{
                        alert(`❌ ОШИБКА:\\n\\n${{d.last_error}}`);
                    }}
                    loadData();
                    btn.disabled = false;
                    btn.innerHTML = '🔄 Синхронизировать';
                }}, 1000);
            }}).catch(err => {{
                alert('❌ Ошибка: ' + err);
                btn.disabled = false;
                btn.innerHTML = '🔄 Синхронизировать';
            }});
        }}

        loadData();
        setInterval(loadData, 30000);
    </script>
</body>
</html>"""

if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    
    try:
        print("\\n" + "="*80)
        print("🌐 OZON PRODUCT TRACKER - МАСТЕР ВЕРСИЯ")
        print("="*80)
        print(f"\\n✓ Сервер запущен!")
        print(f"✓ Откройте: http://localhost:{port}")
        print(f"\\n🛑 Для остановки: Ctrl+C\\n")
        print("="*80 + "\\n")
        
        with socketserver.TCPServer(("", port), Handler) as httpd:
            httpd.serve_forever()
    
    except KeyboardInterrupt:
        print("\\n✓ Сервер остановлен")
        sys.exit(0)
    except OSError as e:
        print(f"\\n❌ Ошибка: {e}\\n")
        sys.exit(1)
    except Exception as e:
        print(f"\\n❌ {e}\\n")
        sys.exit(1)
'''

# ============================================================================
# ОСНОВНАЯ ЛОГИКА
# ============================================================================

def main():
    print("\n" + "="*80)
    print("🤖 OZON TRACKER MASTER - ПОЛНАЯ АВТОМАТИЗАЦИЯ")
    print("="*80 + "\n")
    
    log("Инициализация мастер-скрипта", "INFO")
    
    # Шаг 1: Получаем ID файла
    log("Получение ID файла...", "INFO")
    file_id = get_file_id_from_folder(FOLDER_ID, FILE_NAME)
    
    if not file_id:
        log("Ошибка: не удалось получить ID файла", "ERROR")
        return False
    
    log(f"ID файла: {file_id}", "INFO")
    
    # Шаг 2: Скачиваем файл
    log("Скачивание файла с Google Drive...", "INFO")
    if download_from_drive(file_id, FILE_NAME):
        log("Файл скачан успешно", "SUCCESS")
    else:
        log("Ошибка скачивания файла", "ERROR")
        log("Создаю локальную копию с улучшенным кодом...", "WARNING")
        
        # Создаем улучшенную версию локально
        try:
            with open(FILE_NAME, 'w', encoding='utf-8') as f:
                f.write(IMPROVED_SERVER_CODE)
            log("Локальная копия создана", "SUCCESS")
        except Exception as e:
            log(f"Ошибка создания файла: {e}", "ERROR")
            return False
    
    # Шаг 3: Запускаем сервер
    log("Запуск сервера...", "INFO")
    
    try:
        # Запускаем server.py
        subprocess.run([sys.executable, FILE_NAME], check=False)
    except Exception as e:
        log(f"Ошибка запуска сервера: {e}", "ERROR")
        return False
    
    return True

# ============================================================================
# ЗАПУСК
# ============================================================================

if __name__ == '__main__':
    try:
        success = main()
        
        if success:
            log("Мастер-скрипт завершен успешно", "SUCCESS")
        else:
            log("Мастер-скрипт завершен с ошибками", "ERROR")
    
    except KeyboardInterrupt:
        log("Прерывание пользователем", "WARNING")
        sys.exit(0)
    except Exception as e:
        log(f"Критическая ошибка: {e}", "ERROR")
        sys.exit(1)
