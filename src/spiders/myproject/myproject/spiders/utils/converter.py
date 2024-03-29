import country_converter as coco

def get_country_code(country_name: str) -> str:
    """
    Convert a country name to a country code.

    Args:
        country_name (str): The name of the country.

    Returns:
        str: The country code.

    """
    return coco.convert(names=country_name, to="ISO3")

def get_country_name(country_code: str) -> str:
    """
    Convert a country code to a country name.

    Args:
        country_code (str): The country code.

    Returns:
        str: The name of the country.

    """

    print(country_code)
    return "USD"


    try:
        return coco.convert(names=country_code, to="name")
    except Exception:
        return "Invalid country code"