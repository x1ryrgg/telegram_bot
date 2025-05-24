def format_order(order):
    """Форматирует один заказ в красивый блок"""
    return (
        f"┌{'─' * 30}┐\n"
        f"│ 🆔 Заказ: #{order['id']}\n"
        f"│ 🏷️ Товар: {order['product']['name']}\n"
        f"│ 💰 Цена: {order['user_price']} руб.\n"
        f"│ ✖️ Количество: {order['quantity']} шт.\n"
        f"│ 🚚 Статус: {get_status_emoji(order['status'])}\n"
        f"└{'─' * 30}┘"
    )

def get_status_emoji(status):
    """Возвращает эмодзи для статуса"""
    status_emojis = {
        'delivered': '✅ Доставлен',
        'on the way': '⏳ В пути',
        'processing': '🔄 В обработке',
        'canceled': '❌ Отменен'
    }
    return status_emojis.get(status, status)