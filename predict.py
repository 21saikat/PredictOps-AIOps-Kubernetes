import requests
import time
from openai import AzureOpenAI

# ================================
# Paste your Azure OpenAI details here
# ================================

AZURE_ENDPOINT = ""

AZURE_API_KEY = ""

DEPLOYMENT_NAME = ""

# ================================

PROMETHEUS_URL = "http://prometheus-service:9090"

client = AzureOpenAI(
    azure_endpoint=AZURE_ENDPOINT,
    api_key=AZURE_API_KEY,
    api_version="2024-02-15-preview"
)

def get_cpu_trend():
    query = 'app_cpu_simulated'
    resp = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={"query": query})
    result = resp.json()["data"]["result"]
    if result:
        return float(result[0]["value"][1])
    return None

def ask_ai_for_risk(cpu_value):
    prompt = (
        f"Current simulated CPU usage is {cpu_value:.2f}%. "
        "Based on this single reading, respond with only one word: "
        "'SCALE' if this looks like it could lead to overload soon (above 70%), "
        "or 'OK' if it's normal."
    )

    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[{"role": "user", "content": prompt}],
        max_completion_tokens=10
    )

    return response.choices[0].message.content.strip()

def scale_up():
    import subprocess
    subprocess.run([
        "kubectl",
        "scale",
        "deployment",
        "predictops-demo",
        "--replicas=4"
    ])
    print("[ACTION] Scaled deployment to 4 replicas.")

while True:
    cpu = get_cpu_trend()

    if cpu is not None:
        print(f"[DATA] Current CPU: {cpu:.2f}%")
        decision = ask_ai_for_risk(cpu)
        print(f"[AI DECISION] {decision}")

        if "SCALE" in decision.upper():
            scale_up()
    else:
        print("[WARN] No data from Prometheus yet.")

    time.sleep(20)
