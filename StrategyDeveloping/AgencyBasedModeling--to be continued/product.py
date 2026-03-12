# product.py

class FinancialProduct:
    """
    简单的金融产品类，只包含价格。
    """
    def __init__(self, initial_price: float = 1000.0):
        self.price = float(initial_price)
