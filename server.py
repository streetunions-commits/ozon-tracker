#!/usr/bin/env python3
"""
🌐 OZON PRODUCT TRACKER - УЛУЧШЕННАЯ ВЕРСИЯ
С выпадающим списком товаров
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
        try:
            print("\n" + "="*80)
            print("🔄 СИНХРОНИЗАЦИЯ ТОВАРОВ ИЗ OZON API")
            print("="*80)
            
            self.connection_status = "Подключение..."
            
            url = f"{OZON_CONFIG['api_url']}/v3/product/list"
            print(f"\n📍 URL: {url}")
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
                
                products_list = []
                
                if 'result' in result:
                    if isinstance(result['result'], dict):
                        if 'products' in result['result']:
                            products_list = result['result']['products']
                        else:
                            for key in result['result']:
                                if isinstance(result['result'][key], list):
                                    if len(result['result'][key]) > 0:
                                        if isinstance(result['result'][key][0], dict):
                                            products_list = result['result'][key]
                                            break
                    elif isinstance(result['result'], list):
                        products_list = result['result']
                
                elif 'products' in result:
                    if isinstance(result['products'], list):
                        products_list = result['products']
                
                elif isinstance(result, list):
                    products_list = result
                
                if not products_list:
                    raise Exception("Не найдены товары")
                
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
                        print(f"⚠️ Ошибка товара {i}")
                
                print(f"\n✓ УСПЕШНО! Загружено {len(self.products)} товаров")
                
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
                print("="*80 + "\n")
                return True
        
        except urllib.error.HTTPError as e:
            try:
                error_body = e.read().decode('utf-8')
                print(f"❌ HTTP {e.code}")
                self.last_error = f"HTTP {e.code}"
            except:
                self.last_error = f"HTTP {e.code}"
            
            self.connection_status = f"❌ HTTP {e.code}"
            
            self.syncs.append({
                'id': len(self.syncs) + 1,
                'date': datetime.now().isoformat(),
                'type': 'full',
                'products_count': 0,
                'status': 'error',
                'error': self.last_error
            })
            
            print("="*80 + "\n")
            return False
        
        except urllib.error.URLError as e:
            error_msg = "Ошибка сети"
            print(f"❌ {error_msg}\n")
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
            
            print("="*80 + "\n")
            return False
        
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Ошибка: {error_msg}\n")
            self.last_error = error_msg
            self.connection_status = "❌ Ошибка"
            
            self.syncs.append({
                'id': len(self.syncs) + 1,
                'date': datetime.now().isoformat(),
                'type': 'full',
                'products_count': 0,
                'status': 'error',
                'error': error_msg
            })
            
            print("="*80 + "\n")
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
            
            elif path == '/api/product':
                product_id = query.get('id', [None])[0]
                if product_id:
                    product = next((p for p in db.products if str(p['id']) == product_id), None)
                    if product:
                        self.send_json({'product': product})
                    else:
                        self.send_json({'error': 'Not found'}, 404)
                else:
                    self.send_json({'error': 'No id'}, 400)
            
            elif path == '/api/stats':
                self.send_json({
                    'total_products': len(db.products),
                    'total_stock': sum(p['stock'] for p in db.products),
                    'average_price': round(sum(p['price'] for p in db.products) / len(db.products), 2) if db.products else 0,
                    'syncs': len(db.syncs),
                    'last_sync': db.last_sync,
                    'connection_status': db.connection_status
                })
            
            elif path == '/api/health':
                self.send_json({
                    'status': 'ok',
                    'products_loaded': len(db.products),
                    'connection_status': db.connection_status
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
                    'message': 'OK' if success else 'ERROR',
                    'connection_status': db.connection_status
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
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; padding: 20px; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ background: white; padding: 30px; border-radius: 15px; text-align: center; margin-bottom: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }}
        .header h1 {{ color: #333; margin-bottom: 5px; font-size: 2.5em; }}
        .header p {{ color: #666; font-size: 1.1em; }}
        .status {{ background: #e8f5e9; color: {status_color}; padding: 12px 20px; border-radius: 8px; display: inline-block; margin-top: 15px; font-weight: bold; font-size: 1.1em; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .card {{ background: white; padding: 25px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); }}
        .card h2 {{ color: #667eea; margin-bottom: 20px; font-size: 1.5em; }}
        .stat {{ padding: 15px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-left: 5px solid #667eea; margin: 15px 0; border-radius: 8px; }}
        .stat-label {{ color: #666; font-size: 0.95em; margin-bottom: 5px; }}
        .stat-value {{ color: #667eea; font-weight: bold; font-size: 1.8em; }}
        .big-stat {{ text-align: center; font-size: 3em; color: #667eea; font-weight: bold; padding: 30px 20px; background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); border-radius: 10px; }}
        select {{ width: 100%; padding: 12px 15px; border: 2px solid #667eea; border-radius: 8px; margin: 15px 0; font-size: 1em; background: white; color: #333; cursor: pointer; }}
        select:focus {{ outline: none; border-color: #764ba2; box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1); }}
        button {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; border: none; padding: 12px 30px; border-radius: 8px; cursor: pointer; width: 100%; margin-top: 15px; font-weight: bold; font-size: 1em; transition: all 0.3s; }}
        button:hover {{ transform: translateY(-2px); box-shadow: 0 5px 20px rgba(102, 126, 234, 0.4); }}
        button:active {{ transform: translateY(0); }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 15px; text-align: left; border-bottom: 1px solid #eee; }}
        th {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; font-weight: 600; }}
        tr:hover {{ background: #f9f9f9; }}
        .full-width {{ grid-column: 1 / -1; }}
        .product-details {{ background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%); padding: 20px; border-radius: 10px; margin-top: 20px; }}
        .product-details h3 {{ color: #667eea; margin-bottom: 15px; font-size: 1.3em; }}
        .detail-item {{ padding: 10px 0; border-bottom: 1px solid #ddd; }}
        .detail-label {{ color: #666; font-weight: 500; }}
        .detail-value {{ color: #333; font-weight: bold; margin-top: 5px; }}
        .spinner {{ display: inline-block; width: 20px; height: 20px; border: 3px solid #f3f3f3; border-top: 3px solid #667eea; border-radius: 50%; animation: spin 1s linear infinite; margin-right: 10px; }}
        @keyframes spin {{ 0% {{ transform: rotate(0deg); }} 100% {{ transform: rotate(360deg); }} }}
        .empty-state {{ text-align: center; color: #999; padding: 40px; font-size: 1.1em; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 Ozon Product Tracker</h1>
            <p>Управление товарами из магазина Ozon</p>
            <div class="status">{status_icon} {db.connection_status}</div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>📊 Статистика</h2>
                <div class="big-stat" id="stat-count">-</div>
                <div style="text-align: center; color: #666; margin-bottom: 20px; font-size: 1.1em;">Товаров загружено</div>
                <div class="stat">
                    <div class="stat-label">Общий остаток</div>
                    <div class="stat-value" id="stat-stock">-</div>
                </div>
                <div class="stat">
                    <div class="stat-label">Средняя цена</div>
                    <div class="stat-value" id="stat-price">-</div>
                </div>
            </div>

            <div class="card">
                <h2>🔄 Синхронизация</h2>
                <div class="stat">
                    <div class="stat-label">Последняя синхронизация</div>
                    <div class="stat-value" id="last-sync" style="font-size: 0.85em;">-</div>
                </div>
                <button onclick="sync()" style="margin-top: 30px;">🔄 Синхронизировать</button>
            </div>

            <div class="card">
                <h2>🔗 API Ozon</h2>
                <div class="stat">
                    <div class="stat-label">Статус подключения</div>
                    <div class="stat-value" style="color: {status_color};" id="api-status">-</div>
                </div>
            </div>
        </div>

        <div class="card full-width">
            <h2>📦 Выберите товар</h2>
            <select id="productSelect" onchange="selectProduct()">
                <option value="">-- Выберите товар --</option>
            </select>
            <div id="productDetails"></div>
        </div>

        <div class="card full-width">
            <h2>📋 Все товары</h2>
            <table>
                <thead>
                    <tr><th>ID</th><th>SKU</th><th>Название</th><th>Цена (₽)</th><th>Остаток</th><th>Рейтинг</th></tr>
                </thead>
                <tbody id="products"></tbody>
            </table>
        </div>
    </div>

    <script>
        function loadData() {{
            fetch('/api/products').then(r => r.json()).then(d => {{
                // Загрузить таблицу
                let html = '';
                if (d.products.length === 0) {{
                    html = '<tr><td colspan="6" class="empty-state">Нажмите "Синхронизировать"</td></tr>';
                }} else {{
                    d.products.forEach(p => {{
                        html += '<tr><td>' + p.id + '</td><td>' + p.sku + '</td><td><strong>' + p.name + '</strong></td><td>₽' + p.price.toLocaleString() + '</td><td>' + p.stock + ' шт</td><td>⭐ ' + (p.rating || '—') + '</td></tr>';
                    }});
                }}
                document.getElementById('products').innerHTML = html;
                
                // Загрузить dropdown
                let select = document.getElementById('productSelect');
                select.innerHTML = '<option value="">-- Выберите товар --</option>';
                d.products.forEach(p => {{
                    let option = document.createElement('option');
                    option.value = p.id;
                    option.text = p.name + ' (₽' + p.price + ')';
                    select.appendChild(option);
                }});
            }});
            
            fetch('/api/stats').then(r => r.json()).then(d => {{
                document.getElementById('stat-count').textContent = d.total_products;
                document.getElementById('stat-stock').textContent = (d.total_stock || 0).toLocaleString() + ' шт';
                document.getElementById('stat-price').textContent = '₽' + Math.round(d.average_price || 0).toLocaleString();
                document.getElementById('api-status').textContent = d.connection_status;
                
                if (d.last_sync) {{
                    const date = new Date(d.last_sync).toLocaleString('ru-RU');
                    document.getElementById('last-sync').textContent = date;
                }}
            }});
        }}

        function selectProduct() {{
            const select = document.getElementById('productSelect');
            const productId = select.value;
            
            if (!productId) {{
                document.getElementById('productDetails').innerHTML = '';
                return;
            }}
            
            fetch('/api/product?id=' + productId).then(r => r.json()).then(d => {{
                if (d.product) {{
                    const p = d.product;
                    let html = '<div class="product-details">';
                    html += '<h3>' + p.name + '</h3>';
                    html += '<div class="detail-item">';
                    html += '<div class="detail-label">ID товара</div>';
                    html += '<div class="detail-value">' + p.id + '</div>';
                    html += '</div>';
                    html += '<div class="detail-item">';
                    html += '<div class="detail-label">SKU / Артикул</div>';
                    html += '<div class="detail-value">' + p.sku + '</div>';
                    html += '</div>';
                    html += '<div class="detail-item">';
                    html += '<div class="detail-label">Цена</div>';
                    html += '<div class="detail-value">₽' + p.price.toLocaleString() + '</div>';
                    html += '</div>';
                    html += '<div class="detail-item">';
                    html += '<div class="detail-label">Остаток на складе</div>';
                    html += '<div class="detail-value">' + p.stock + ' шт</div>';
                    html += '</div>';
                    html += '<div class="detail-item">';
                    html += '<div class="detail-label">Статус</div>';
                    html += '<div class="detail-value">' + (p.status === 'active' ? '✓ Активный' : p.status) + '</div>';
                    html += '</div>';
                    html += '<div class="detail-item" style="border-bottom: none;">';
                    html += '<div class="detail-label">Рейтинг</div>';
                    html += '<div class="detail-value">⭐ ' + (p.rating || '—') + '</div>';
                    html += '</div>';
                    html += '</div>';
                    document.getElementById('productDetails').innerHTML = html;
                }}
            }});
        }}

        function sync() {{
            const btn = event.target;
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span>Синхронизация...';
            
            fetch('/api/sync', {{method: 'POST'}}).then(r => r.json()).then(d => {{
                setTimeout(() => {{
                    if (d.success) {{
                        alert('✓ УСПЕШНО!\\n\\nТоваров загружено: ' + d.products_synced);
                    }} else {{
                        alert('❌ ОШИБКА:\\n\\n' + (d.message || 'Неизвестная ошибка'));
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
        print("\n" + "="*80)
        print("🌐 OZON PRODUCT TRACKER - УЛУЧШЕННАЯ ВЕРСИЯ")
        print("="*80)
        print(f"\n✓ Сервер запущен на http://localhost:{port}")
        print(f"\n🛑 Для остановки: Ctrl+C\n")
        print("="*80 + "\n")
        
        with socketserver.TCPServer(("", port), Handler) as httpd:
            httpd.serve_forever()
    
    except KeyboardInterrupt:
        print("\n✓ Остановлен")
        sys.exit(0)
    except OSError as e:
        print(f"\n❌ Ошибка: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ {e}\n")
        sys.exit(1)
