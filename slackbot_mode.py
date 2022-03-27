from modes import req
from modes import antibot, region_check, zyte_api, netlocksmith, auto_xtract_product, auto_xtract_article
from invalid_url import check_url
from slack_sdk import WebClient
import os
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, request, Response, render_template
import json
import requests
import threading
import validators
from flask import Flask, request, make_response, Response
from slack import WebClient

# from slack import SlackClient

env_path = Path(".") / ".env"
load_dotenv(dotenv_path=env_path)

app = Flask(__name__)

# client = slack.WebClient(token=os.environ['SLACK_TOKEN']) => For Old version of Slack-SDK
client = WebClient(token=os.environ["SLACK_TOKEN"])
api = os.environ["APIKEY"]
# common webhook where the data will be posted to the bot directly and it will be visible to everyone.
slack_webhook_url = os.environ["SLACK_WEB_HOOK"]
auto_x_url = os.environ["AUTO_X_URL"]
spm_api = os.environ["SPM_API"]
auto_x_api = os.environ["AUTO_X_API"]
headers = {
    "Content-type": "application/json",
}
#SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]


# slack_client = SlackClient(SLACK_BOT_TOKEN)


@app.route("/", methods=["GET"])
def home():
    return render_template("home.html")


@app.route("/antibot", methods=["POST"])
def slack_response():
    data = request.form
    text = data.get("text")
    validators.url(text)
    user = data.get("user_name")
    response_url = data["response_url"]
    message = {"text": "Connection successful!"}
    resp = requests.post(response_url, json=message)
    print(resp.status_code)
    x = threading.Thread(target=check_antibot, args=(
        data, text, user, response_url))
    x.start()
    return "Processing, Please wait!!"


def check_antibot(data, text, user, response_url):
    # print(response_url)
    print(response_url)
    print(data)
    print(user)
    url = f"{text}"
    if validators.url(url) is True:

        initial_message = antibot.initial_message(
            user, slack_webhook_url, headers)
        print(initial_message.status_code)

        client.chat_postMessage(
            channel="#antibot-checker",
            text="Sending request to Antibotpedia",
            response_type="in_channel",
        )

# the below is using get_page_id function from a custom module antibot under modes package.
        page_id = antibot.get_page_id(url, api)
        print(page_id)

        print(page_id.text)
        dict1 = json.loads(page_id.text)
        page = dict1["response"]["check_id"]

        client.chat_postMessage(
            channel="#antibot-checker",
            text="Please wait. The scan takes atleast 1-2 mins time. Even on GUI",
            response_type="in_channel",
        )
        client.chat_postMessage(
            channel="#antibot-checker",
            text=f"If you have access, you can check in the Web-UI: https://antibotpedia.scrapinghub.com/checks/pages/{page}",
            response_type="in_channel",
        )

# the below is using final_result function from a custom module antibot under modes package.
        final_result = antibot.final_result(page, api)
        print(final_result)

# the below is using final_result function from a custom module antibot under modes package.
        final_antibot_result = antibot.post_antibot_results(
            slack_webhook_url, headers, user, url, final_result)
        print(final_antibot_result.status_code)
    else:

        # the below is using check_url function from a custom module invalid_url.
        incorrect_url_message = check_url(
            user, response_url, headers)
        print(incorrect_url_message)

    return Response(), 200


@app.route("/help", methods=["POST"])
def slack_help():
    data = request.form
    user = data.get("user_name")
    # response_url = data["response_url"]
    help_message = {
        "text": "Antibot Details",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"@{user} Please use the command: /antibot http://example.com",
                },
            },
        ],
    }
    resp = requests.post(
        url=slack_webhook_url, headers=headers, data=json.dumps(help_message)
    )
    print(resp.status_code)

    return Response(), 200


# Region Checking Endpoint


@app.route("/regioncheck", methods=["POST"])
# the below function is to send a response as 200 to slack's post request within 3 sec to avoid the "operation_timed_out" error.
def slack_crawlbot_response():
    data = request.form
    text = data.get("text")
    validators.url(text)
    user = data.get("user_name")
    response_url = data["response_url"]
    message = {"text": "Connection successful!"}
    resp = requests.post(response_url, json=message)
    print(resp.status_code)
    crawl_bot = threading.Thread(
        target=crawlbot, args=(data, text, user, response_url))
    crawl_bot.start()
    return "Processing, Please wait!!"


def crawlbot(data, text, user, response_url):
    print(data)
    print(user)
    url = f'{text}'
    if validators.url(text) is True:
        regions = [
            "AU",
            "AT",
            "BY",
            "BE",
            "BO",
            "BR",
            "CA",
            "CL",
            "CN",
            "DK",
            "FI",
            "FR",
            "GE",
            "DE",
            "GR",
            "HK",
            "IN",
            "ID",
            "IE",
            "IL",
            "IT",
            "JP",
            "MY",
            "MX",
            "NL",
            "NG",
            "PH",
            "PL",
            "PT",
            "RO",
            "RU",
            "SG",
            "ZA",
            "KR",
            "ES",
            "SE",
            "CH",
            "TW",
            "TH",
            "TR",
            "AE",
            "GB",
            "US",
            "UY",
        ]

        proxy_host = "proxy.crawlera.com"
        proxy_port = "8010"
        # Make sure to include ':' at the end
        proxy_auth = f"{spm_api}:"
        proxies = {
            "https": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
            "http": "http://{}@{}:{}/".format(proxy_auth, proxy_host, proxy_port),
        }
        ok_result = []
        error_result = []
        threads = []

# posting the results to slack using a initial_message function from a region_check modulde in mode package.
        initial_message = region_check.initial_message(response_url, user)
        print(initial_message)

        def send(text, headers, region):

            res = requests.get(
                url=f"{text}",
                headers=headers,
                proxies=proxies,
                verify="/home/wolfman_crack007/app/slack-bot/zyte-proxy-ca.crt",
            )
            print(res.headers)
            if "x-crawlera-slave" in res.headers:
                proxy_ip = res.headers["X-Crawlera-Slave"]
                print(
                    f"The region {region} has a response of {res.status_code} status code from SPM. Proxy IP is {proxy_ip}"
                )
                ok_result.append(
                    f"Country: {region} - Status: {res.status_code} - Proxy Details: {proxy_ip}"
                )

            elif "X-Crawlera-Error" in res.headers:
                proxy_ip = res.headers["X-Crawlera-Error"]
                print(
                    f"The region {region} has a response of {res.status_code} status code from SPM. Proxy IP is {proxy_ip}"
                )
                error_result.append(
                    f"Country: {region} - Status: {res.status_code} - Proxy Details: {proxy_ip}"
                )

        def main():

            for region in regions:
                headers = {"X-Crawlera-Region": f"{region}"}
                thread = threading.Thread(
                    target=send, args=[text, headers, region])
                thread.start()
                threads.append(thread)

            for thread in threads:
                thread.join()

            send(text, headers, region)

        main()

        print(ok_result)
        print(error_result)

# posting the results to slack using a post_result_to_slack function from a region_check modulde in mode package.
        post_result_to_slack = region_check.post_result_to_slack(
            response_url, headers, url, user, ok_result, error_result)
        print(post_result_to_slack)

# Using a function check_url from zyte_api module of mode package
    else:
        incorrect_url_message = check_url(user, response_url, headers)
        print(incorrect_url_message)
    return Response(), 200


@app.route("/zytedataapi", methods=["POST"])
# the below function is to send a response as 200 to slack's post request within 3 sec to avoid the "operation_timed_out" error.
def slack_zyteapi_response():
    data = request.form
    text = data.get("text")
    validators.url(text)
    user = data.get("user_name")
    response_url = data["response_url"]
    message = {"text": "Connection successful!"}
    resp = requests.post(response_url, json=message)
    print(resp.status_code)
    zyte_api = threading.Thread(
        target=zytedataapi, args=(data, text, user, response_url)
    )
    zyte_api.start()
    return "Processing, Please wait!!"


def zytedataapi(data, text, user, response_url):
    print(data)
    print(user)
    url = f'{text}'

    if validators.url(text) is True:

        # Using a function initial_message from zyte_api module of mode package

        initial_msg = zyte_api.initial_message(response_url, user)
        print(initial_msg)

# Using a function zyte_api_req from zyte_api module of mode package
        zyte_resp = zyte_api.zyte_api_req(
            url, user, slack_webhook_url, headers)
        print(zyte_resp)

    else:

        # Using a function check_url from invalid_url module
        incorrect_url_warning = check_url(user, response_url, headers)
        print(incorrect_url_warning.status_code)

    return Response(), 200


@app.route("/netlock-dc", methods=["POST"])
# the below function is to send a response as 200 to slack's post request within 3 sec to avoid the "operation_timed_out" error.
def slack_netlock_dc_response():
    data = request.form
    text = data.get("text")
    validators.url(text)
    user = data.get("user_name")
    response_url = data["response_url"]
    message = {"text": "Connection successful!"}
    resp = requests.post(response_url, json=message)
    print(resp.status_code)
    netlocksmith_dc = threading.Thread(
        target=netlock_dc, args=(data, text, user, response_url)
    )
    netlocksmith_dc.start()
    return "Processing, Please wait!!"


def netlock_dc(data, text, user, response_url):
    if validators.url(text) is True:
        print(data)
        print(user)
        url = f"{text}"
# For netlocsmith, it is using a netloc function from netlocksmith module from mode package.

        netlock_dc_resp = netlocksmith.netloc(url, user, response_url, headers)
        print(netlock_dc_resp)
    else:
        incorrect_url_warning = check_url(user, response_url, headers)
        print(incorrect_url_warning.status_code)

    return Response(), 200

# Single Product Only


@app.route("/auto-x-product", methods=["POST"])
# the below function is to send a response as 200 to slack's post request within 3 sec to avoid the "operation_timed_out" error.
def slack_auto_x_product_response():
    data = request.form
    text = data.get("text")
    validators.url(text)
    user = data.get("user_name")
    response_url = data["response_url"]
    message = {"text": "Connection successful!"}
    resp = requests.post(response_url, json=message)
    print(resp.status_code)
    auto_product = threading.Thread(
        target=auto_x_product, args=(data, text, user, response_url)
    )
    auto_product.start()
    return "Processing, Please wait!!"


def auto_x_product(data, text, user, response_url):
    if validators.url(text) is True:
        print(data)
        print(user)
        url = f"{text}"

# it is using a initial_message function from auto_xtract_product module from mode package.
        initial_msg = auto_xtract_product.initial_message(
            response_url, headers, user)
        print(initial_msg)

# For product-extraction, it is using a product function from auto_xtract_product module from mode package.
        auto_x_product_results = auto_xtract_product.product(
            url, response_url, headers, user, slack_webhook_url)
        print(auto_x_product_results)
    else:

        # this is using a function check_url from a module name invalid_url
        incorrect_url_warning = check_url(user, response_url, headers)
        print(incorrect_url_warning.status_code)

    return Response(), 200

# Product Listing


@app.route("/auto-x-product-listing", methods=["POST"])
# the below function is to send a response as 200 to slack's post request within 3 sec to avoid the "operation_timed_out" error.
def slack_auto_x_product_lisitng_response():
    data = request.form
    text = data.get("text")
    validators.url(text)
    user = data.get("user_name")
    response_url = data["response_url"]
    message = {"text": "Connection successful!"}
    resp = requests.post(response_url, json=message)
    print(resp.status_code)
    auto_product_listing = threading.Thread(
        target=auto_x_product_lisitng, args=(data, text, user, response_url)
    )
    auto_product_listing.start()
    return "Processing, Please wait!!"


def auto_x_product_lisitng(data, text, user, response_url):
    if validators.url(text) is True:
        print(data)
        print(user)
        url = f"{text}"

# it is using a initial_message function from auto_xtract_product module from mode package.
        initial_msg = auto_xtract_product.initial_message(
            response_url, headers, user)
        print(initial_msg)

# For product-extraction, it is using a product function from auto_xtract_product module from mode package.
        auto_x_product_list_response = auto_xtract_product.product_list(
            url, response_url, headers, user, slack_webhook_url)
        print(auto_x_product_list_response)
    else:

        # this is using a function check_url from a module name invalid_url
        incorrect_url_warning = check_url(user, response_url, headers)
        print(incorrect_url_warning.status_code)

    return Response(), 200


# Article Only

@app.route("/auto-x-article", methods=["POST"])
# the below function is to send a response as 200 to slack's post request within 3 sec to avoid the "operation_timed_out" error.
def slack_auto_x_article_response():
    data = request.form
    text = data.get("text")
    validators.url(text)
    user = data.get("user_name")
    response_url = data["response_url"]
    message = {"text": "Connection successful!"}
    resp = requests.post(response_url, json=message)
    print(resp.status_code)
    auto_article = threading.Thread(
        target=auto_x_article, args=(data, text, user, response_url)
    )
    auto_article.start()
    return "Processing, Please wait!!"


def auto_x_article(data, text, user, response_url):
    if validators.url(text) is True:
        print(data)
        print(user)
        url = f"{text}"

# For article-extraction, it is using a initial_message function from auto_xtract_article module from mode package.
        initial_msg = auto_xtract_article.initial_message(
            response_url, headers, user)
        print(initial_msg)

# For article-extraction, it is using a article function from auto_xtract_article module from mode package.
        auto_x_article_response = auto_xtract_article.article(
            url, response_url, headers, user, slack_webhook_url)
        print(auto_x_article_response)
    else:
        # this is using a function check_url from a module name invalid_url
        incorrect_url_warning = check_url(user, response_url, headers)
        print(incorrect_url_warning.status_code)

    return Response(), 200

# article_list only


@app.route("/auto-x-article-list", methods=["POST"])
# the below function is to send a response as 200 to slack's post request within 3 sec to avoid the "operation_timed_out" error.
def slack_auto_x_article_lisitng_response():
    data = request.form
    text = data.get("text")
    validators.url(text)
    user = data.get("user_name")
    response_url = data["response_url"]
    message = {"text": "Connection successful!"}
    resp = requests.post(response_url, json=message)
    print(resp.status_code)
    auto_article_list = threading.Thread(
        target=auto_x_article_lisitng, args=(data, text, user, response_url)
    )
    auto_article_list.start()
    return "Processing, Please wait!!"


def auto_x_article_lisitng(data, text, user, response_url):
    if validators.url(text) is True:
        print(data)
        print(user)
        url = f"{text}"

# For article-extraction, it is using a initial_message function from auto_xtract_article module from mode package.
        initial_msg = auto_xtract_article.initial_message(
            response_url, headers, user)
        print(initial_msg)

# For article-extraction, it is using a article function from auto_xtract_article module from mode package.
        auto_x_article_response = auto_xtract_article.article_list(
            url, response_url, headers, user, slack_webhook_url)
        print(auto_x_article_response)

    else:
        # this is using a function check_url from a module name invalid_url
        incorrect_url_warning = check_url(user, response_url, headers)
        print(incorrect_url_warning.status_code)

    return Response(), 200


if __name__ == "__main__":
    app.run(port=5050, debug=True)