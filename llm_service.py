import requests

def ask_qwen(question, language="urdu"):
    try:
        API_KEY = "sk-ws-H.DDIDPLL.0zeM.MEQCIEaM3kV7oPXQYO7GIXFyDJgHNcV1ItAU2B2ViW5KU-JwAiBVZmgDEwtf4brHaFBs9TO5XwOn3DoLZWbxmcxVXjobww"
        BASE_URL = "https://ws-y4bws78w64auokrv.ap-southeast-1.maas.aliyuncs.com/compatible-mode/v1"
        MODEL = "qwen-max"
        
        response = requests.post(
            f"{BASE_URL}/chat/completions",
            headers={
                "Authorization": f"Bearer {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": "You are AI Dost. Help with Pakistan government services: NADRA, Healthcare, Education, FBR, Pensions, BISP. Be specific with details."},
                    {"role": "user", "content": question}
                ],
                "temperature": 0.3,
                "max_tokens": 500
            },
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            return "Error: API not responding"
    
    except Exception as e:
        return f"Error: {str(e)}"
