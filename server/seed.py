# seed.py

from app import app
from models import db, Users, Products, Cart_item, Orders, Order_item
from datetime import datetime

with app.app_context():
    print("🔄 Resetting database...")

    # Optional: Clear all data
    db.session.query(Order_item).delete()
    db.session.query(Cart_item).delete()
    db.session.query(Orders).delete()
    db.session.query(Products).delete()
    db.session.query(Users).delete()

    db.session.commit()

    print("✅ Seeding users...")

    user1 = Users(name="Alice", email="alice@example.com", password_hash=12345, role="customer")
    user2 = Users(name="Bob", email="bob@example.com", password_hash=67890, role="admin")

    db.session.add_all([user1, user2])
    db.session.commit()

    print("✅ Seeding products...")

    p1 = Products(
        name="Laptop", description="Powerful laptop", price=1500.00,
        stock_quantity=10, image_url="http://example.com/laptop.png"
    )
    p2 = Products(
        name="Smartphone", description="Android phone", price=800.00,
        stock_quantity=25, image_url="http://example.com/phone.png"
    )

    db.session.add_all([p1, p2])
    db.session.commit()

    print("🛒 Seeding cart items...")

    cart1 = Cart_item(user_id=user1.id, product_id=p1.id, quantity=1)
    cart2 = Cart_item(user_id=user1.id, product_id=p2.id, quantity=2)

    db.session.add_all([cart1, cart2])
    db.session.commit()

    print("📦 Seeding order...")

    order = Orders(
        user_id=user1.id,
        order_date=datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        status="Pending",
        total_amount=0  # will update after items
    )
    db.session.add(order)
    db.session.flush()  # to get order.id before commit

    item1 = Order_item(
        order_id=order.id,
        product_id=p1.id,
        quantity=1,
        price_at_purchase=p1.price
    )
    item2 = Order_item(
        order_id=order.id,
        product_id=p2.id,
        quantity=2,
        price_at_purchase=p2.price
    )

    total = (item1.quantity * item1.price_at_purchase) + (item2.quantity * item2.price_at_purchase)
    order.total_amount = total

    db.session.add_all([item1, item2])
    db.session.commit()

    print("✅ Seed complete.")
