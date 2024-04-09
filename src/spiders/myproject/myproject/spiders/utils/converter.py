"""
This module contains a class that converts currency signs to country codes and vice versa.

Class:
- SignsConverter: Converts currency signs to country codes and vice versa.

The class contains two static methods:
- convert_to_country_code: Converts a currency sign to a country code.
- convert_to_currency_sign: Converts a country code to a currency sign.
"""

class SignsConverter:
    """
    A utility class for converting currency signs to country codes and vice versa.
    """

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
        """
        Converts a currency sign to its corresponding country code.

        Args:
            currency_sign (str): The currency sign to be converted.

        Returns:
            str: The corresponding country code if the currency sign is found in the currency dictionary,
                 otherwise returns the original currency sign.
        """
        if currency_sign in SignsConverter.currency:
            return SignsConverter.currency[currency_sign]
        return currency_sign

    @staticmethod
    def convert_to_currency_sign(country_code: str) -> str:
        """
        Converts a country code to its corresponding currency sign.

        Args:
            country_code (str): The country code to be converted.

        Returns:
            str: The corresponding currency sign if the country code is found in the currency dictionary,
                 otherwise returns the original country code.
        """
        for sign, code in SignsConverter.currency.items():
            if country_code == code:
                return sign
        return country_code
