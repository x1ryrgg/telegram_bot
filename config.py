def format_order(order):
    """Форматирует один заказ в красивый блок"""
    return (
        f"┌{'─' * 30}┐\n"
        f"│ 🆔 Заказ: #{order['id']}\n"
        f"│ 🏷️ Товар: {order['product']['name']}\n"
        f"│ 💰 Цена: {order['user_price']} руб.\n"
        f"│ ✖️ Количество: {order['quantity']} шт.\n"
        f"│ 🚚 Статус: {get_status_orders(order['status'])}\n"
        f"└{'─' * 30}┘"
    )

def get_status_orders(status):
    """Возвращает эмодзи для статуса"""
    status_emojis = {
        'delivered': '✅ Доставлен',
        'on the way': '⏳ В пути',
        'processing': '🔄 В обработке',
        'canceled': '❌ Отменен'
    }
    return status_emojis.get(status, status)

def get_status_history(status):
    status_variants = {
        'delivered': '✅ Товар принят',
        'denied': '❌ Товар отменен'
    }
    return status_variants.get(status, status)

def format_history(item):
    """Форматирует один заказ в красивый блок"""
    return (
        f"┌{'─' * 30}┐\n"
        f"│ 🆔 Заказ: #{item['id']}\n"
        f"│ 📅 Дата: {item['created_at']}\n"
        f"│ 🏷️ Товар: {item['product']['name']}\n"
        f"│ 💵 Цена: {item['product']['price']} руб.\n"
        f"│ 🔖 Со скидкой: {item['user_price']} руб.\n"
        f"│ ️ ✖️ Количество: {item['quantity']} шт.\n"
        f"│ 🚚 Статус: {get_status_history(item['status'])}\n"
        f"└{'─' * 30}┘"
    )