from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from asgiref.sync import sync_to_async
import os
import django

# Инициализация Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

# Импортируем модель Product
from app.models import Product

# Функция для команды /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет! Я могу показать товары.')
    await show_products(update)

# Функция для команды /products
async def products(update: Update, context: CallbackContext) -> None:
    products = await get_products()
    if products:
        message = "\n".join([f"{p.name} - {p.price}" for p in products])
    else:
        message = "Товары не найдены."
    await update.message.reply_text(message)

# Функция для получения всех продуктов
@sync_to_async
def get_products():
    return list(Product.objects.all())

# Функция для получения товара по ID
@sync_to_async
def get_product_by_id(product_id):
    return Product.objects.get(id=product_id)

# Функция для добавления нового товара
@sync_to_async
def create_product(name, description, price):
    product = Product(name=name, description=description, price=price)
    product.save()

# Функция для удаления товара
@sync_to_async
def delete_product_by_id(product_id):
    product = Product.objects.get(id=product_id)
    product.delete()

# Функция для отображения всех товаров
async def show_products(update: Update) -> None:
    products = await get_products()
    if products:
        message = "\n".join([f"{p.name} - {p.price}" for p in products])
    else:
        message = "Товары не найдены."
    await update.message.reply_text(message)

# Команды
async def product(update: Update, context: CallbackContext) -> None:
    if context.args:
        product_id = context.args[0]
        try:
            product = await get_product_by_id(product_id)
            message = f"Название: {product.name}\nОписание: {product.description}\nЦена: {product.price}"
        except Product.DoesNotExist:
            message = "Товар с таким ID не найден."
    else:
        message = "Пожалуйста, укажите ID товара."
    await update.message.reply_text(message)

async def add_product(update: Update, context: CallbackContext) -> None:
    if len(context.args) >= 3:
        name = context.args[0]
        description = context.args[1]
        price = context.args[2]
        try:
            price = float(price)
            await create_product(name, description, price)
            message = f"Товар {name} был успешно добавлен!"
        except ValueError:
            message = "Цена должна быть числом."
    else:
        message = "Нужно указать название, описание и цену товара."
    await update.message.reply_text(message)

async def delete_product(update: Update, context: CallbackContext) -> None:
    if context.args:
        product_id = context.args[0]
        try:
            await delete_product_by_id(product_id)
            message = f"Товар с ID {product_id} был удален."
        except Product.DoesNotExist:
            message = "Товар с таким ID не найден."
    else:
        message = "Пожалуйста, укажите ID товара для удаления."
    await update.message.reply_text(message)

async def help(update: Update, context: CallbackContext) -> None:
    help_text = """
    Доступные команды:
    /start - Приветственное сообщение
    /products - Покажет все товары
    /product <id> - Покажет товар по ID
    /add_product <name> <description> <price> - Добавить товар
    /delete_product <id> - Удалить товар по ID
    """
    await update.message.reply_text(help_text)

# Настройка бота
def main():
    application = Application.builder().token("8101975306:AAGD3xofa90HBaKtW7TfK-vzco_HcLbrJ5s").build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("products", products))
    application.add_handler(CommandHandler("product", product))
    application.add_handler(CommandHandler("add_product", add_product))
    application.add_handler(CommandHandler("delete_product", delete_product))
    application.add_handler(CommandHandler("help", help))
    application.run_polling()

if __name__ == '__main__':
    main()