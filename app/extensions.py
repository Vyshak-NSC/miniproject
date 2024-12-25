import requests
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()


def get_category_data(Category):
    categories = Category.query.all()
    category_data = {}
    for category in categories:
        category_data[category.name] = category.value
    return category_data


def fetch_articles(api_key, query, max_results=30):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}&pageSize={max_results}"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        articles = data["articles"]
        articles_dict = {}

        for article in articles:
            title = article["title"]
            description = article["description"]

            if (
                description and title != "[removed]"
            ):  # Check if the description is not empty and title is not "[removed]"
                articles_dict[title] = {
                    "description": description,
                    "url": article["url"],
                }

        return articles_dict
    else:
        print("Failed to fetch articles:", response.status_code)
        return {}


# Replace 'YOUR_API_KEY' with your actual News API key
API_KEY = ""
QUERY = "money saving tips"
