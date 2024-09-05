import json
import requests
from datetime import datetime, timedelta
from mail_notification import send_email

credentials = json.load(open("credentials.json"))
config = json.load(open("config.json"))

def send_notification(subject, body, msg_type="plain"):
    sender = config.get('mail_notification_sender')
    recipients = config.get('mail_notification_recipients')
    password = credentials.get('mail_notification_password')

    if not sender or not recipients or not password:
        # Notification not configured
        return

    send_email(subject, body, sender, recipients, password, msg_type=msg_type)

def process_response(response):
    aggregations = response[0]['aggregations']
    graph_data = response[0]['data']

    return aggregations, graph_data

def mean_data(data: list[list], last_time: int = 60):
    data_range = data[-last_time:]
    time, received, sent = zip(*data_range)
    return sum(received) / len(received), sum(sent) / len(sent)

def check_network_load():
    messages = []
    truenas_url = config.get('truenas_url')
    url = f"{truenas_url}/api/v2.0/reporting/get_data"

    payload = {
        "graphs": [{
            "name": "interface",
            "identifier": "eno1"
            }],
        "reporting_query": {
            "unit": "HOUR",
            "page": 1
            }
        }

    response = requests.post(url, headers=headers, json=payload)
    aggregations, graph_data = process_response(response.json())

    # Last hour mean activity
    mean_sent = aggregations['mean']['sent']
    mean_received = aggregations['mean']['received']

    # Last 60 seconds mean activity
    mean_data_sent, mean_data_received = mean_data(graph_data, last_time=60)

    messages.append(f"Last hour mean activity: {mean_sent} / {mean_received}")
    messages.append(f"Last 60 seconds mean activity: {mean_data_sent} / {mean_data_received}")

    if mean_data_sent > 25 or mean_data_received > 50:
        messages.append("Recent network load detected " + str(mean_data_sent) + " / " + str(mean_data_received))
        return True, messages

    if mean_sent > 25 or mean_received > 50:
        messages.append("Network load detected " + str(mean_sent) + " / " + str(mean_received))
        return True, messages

    messages.append("Low Network load detected " + str(mean_sent) + " / " + str(mean_received))
    return False, messages

def check_cpu_load():
    messages = []
    truenas_url = config.get('truenas_url')
    url = f"{truenas_url}/api/v2.0/reporting/get_data"

    payload = {
        "graphs": [{
            "name": "load",
            }],
        "reporting_query": {
            "unit": "HOUR",
            "page": 1
            }
        }


    response = requests.post(url, headers=headers, json=payload)
    aggregations, graph_data = process_response(response.json())
    mean_midterm = aggregations['mean']['midterm']

    if mean_midterm > 0.9:
        messages.append("Above idle CPU load detected " + str(mean_midterm))
        return True, messages

    messages.append("Low CPU load detected " + str(mean_midterm))
    return False, messages

def check_device_status():
    messages = []
    url = f"{config.get('url')}/status?device={TRUENAS_WOL_SERVER_ID}"
    response = requests.get(url)
    messages.append("Device Status: " + str(response.json()))
    return response.json()['online'], messages

def shutdown_nas():
    messages = []
    url = f"{config.get('url')}/shutdown"
    response = requests.post(url, json={"id": TRUENAS_WOL_SERVER_ID, "delay": SHUTDOWN_DELAY})
    messages.append("Shutdown Response: " + str(response.json()))    

    # Send notification
    cancelation_url = f"{config.get('url')}/shutdown/cancel?id=" + str(TRUENAS_WOL_SERVER_ID)
    subject = "NAS Monitoring - Shutdown Notification"
    body = f"""
    <html>
    <head></head>
    <body>
        Shutting down NAS in {SHUTDOWN_DELAY} minutes. Shut down at {(datetime.now() + timedelta(minutes=SHUTDOWN_DELAY)).strftime("%Y-%m-%d %H:%M:%S")}.
        <br>

        <a href="{cancelation_url}">Cancel</a>
        <br>

        { "<br>".join(messages) }
    </body>
    </html>
    """

    send_notification(subject, body, msg_type="html")

    return messages

def main():
    messages = []
    messages.append("--------- Monitoring Truenas NAS " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " ---------\n")
    if not check_device_status()[0]:
        messages.append("NAS Offline")
        return messages

    cpu_load, messages_cpu = check_cpu_load()
    network_load, messages_network = check_network_load()
    messages.extend(messages_cpu)
    messages.extend(messages_network)
    if not cpu_load and not network_load:
        messages.append("Low CPU and network load detected. Shutting down NAS.\n")
        shutdown_nas()
        return messages

    messages.append("CPU and network load detected. Not shutting down NAS.\n")
    return messages

if __name__ == '__main__':
    try:
        TRUENAS_WOL_SERVER_ID = config.get('truenas_wol_server_id', 1)
        SHUTDOWN_DELAY = config.get('shutdown_delay', 1)

        headers = {
            "Accept": "application/json",
            "Authorization": f"Basic {credentials['truenas_wol_auth']}",
            "Content-Type": "application/json",
        }

        res_messages = main()

        print("\n".join(res_messages))
    except Exception as e:
        # Notify error
        subject = "NAS Monitoring - Error Notification"
        body = "NAS Error: " + str(e) + "\n"
        send_notification(subject, body)
        print("\n".join([subject, body]))
