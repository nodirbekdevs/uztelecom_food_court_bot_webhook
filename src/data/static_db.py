from src.helpers.keyboard_buttons import option

users = [
    dict(id=1, telegram_id=465817343, phone_number='+998977041815', language=option['language']['uz']),
    dict(id=2, telegram_id=348297382, phone_number='+998977091815', language=option['language']['uz'])
]

foods = [
    dict(id=1, title='Set 1', description='SET 1', price='30000'),
    dict(id=2, title='Set 2', description='SET 2', price='28000'),
    dict(id=3, title='Set 3', description='SET 3', price='26000'),
    dict(id=4, title='Set 4', description='SET 4', price='24000'),
]

orders = [
    dict(id=1, user=1, date='20.05.2023', payment_type='salary', items=[1, 2, 3], status='active'),
    dict(id=2, user=2, date='20.05.2023', payment_type='salary', items=[4, 5, 6], status='ended'),
]

order_items = [
    dict(id=1, order=1, food=1, count=3, amount=5000, comment='d,amdakdma'),
    dict(id=2, order=1, food=2, count=3, amount=5000, comment='d,amdakdma'),
    dict(id=3, order=1, food=3, count=3, amount=5000, comment='d,amdakdma'),
    dict(id=4, order=2, food=4, count=3, amount=5000, comment='d,amdakdma'),
    dict(id=5, order=2, food=3, count=3, amount=5000, comment='d,amdakdma'),
    dict(id=6, order=2, food=2, count=3, amount=5000, comment='d,amdakdma'),
]
