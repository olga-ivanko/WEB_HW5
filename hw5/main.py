import aiohttp
import asyncio
from datetime import datetime, timedelta
from pprint import pprint
import argparse

url = "https://api.privatbank.ua/p24api/exchange_rates?json&date="


class HttpClient:
    async def get_data(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                return await response.json()


class CurExRate:
    def __init__(self, data) -> None:
        self.data = data

    def get_exrates(self, days):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        result = []
        for day in range((end_date - start_date).days + 1):
            lookup_date = start_date + timedelta(days=day)
            formatted_date = lookup_date.strftime("%d.%m.%Y")

            if formatted_date in self.data:
                ex_rate = {
                    "EUR": self.data[formatted_date]["EUR"],
                    "USD": self.data[formatted_date]["USD"],
                }
                result.append({formatted_date: ex_rate})

        return result


async def get_fx_rates(days):
    network_client = HttpClient()

    if days > 10:
        print(f"{days} is more than 10. Try with range up to 10 days")
        return

    data = await asyncio.gather(
        *[
            network_client.get_data(
                url + (datetime.now() - timedelta(days=i)).strftime("%d.%m.%Y")
            )
            for i in range(days)
        ]
    )

    exchange_rates_data = {}
    for d_data in data:
        date = d_data.get("date", "")
        ex_rate = {}
        for rate in d_data.get("exchangeRate", []):
            currency = rate.get("currency", "")
            sale_rate = rate.get("saleRateNB", "")
            purchase_rate = rate.get("purchaseRateNB", "")
            ex_rate[currency] = {
                "sale": sale_rate,
                "purchase": purchase_rate,
            }
        exchange_rates_data[date] = ex_rate

    currency_exchange = CurExRate(exchange_rates_data)
    result = currency_exchange.get_exrates(days)

    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("days", type=int)
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    exchange_rates = loop.run_until_complete(get_fx_rates(args.days))
    pprint(exchange_rates)

