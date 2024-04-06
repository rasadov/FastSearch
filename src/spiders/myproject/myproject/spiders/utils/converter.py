class SignsConverter:
    currency = {
        '$': 'USD',
        '€': 'EUR',
        '£': 'GBP',
        '¥': 'JPY',
        '₹': 'INR',
        '₽': 'RUB',
        '₩': 'KRW',
        '₴': 'UAH',
        '₿': 'BTC',
        '₸': 'KZT',
        '₺': 'TRY',
        '₼': 'AZN',
        '₾': 'GEL',
    }

    @staticmethod
    def convert_to_country_code(currency_sign: str) -> str:
        return SignsConverter.currency[currency_sign] if currency_sign in SignsConverter.currency else currency_sign
    
    @staticmethod
    def convert_to_currency_sign(country_code: str):
        for sign, code in SignsConverter.currency.items():
            if country_code == code:
                return sign
        return country_code