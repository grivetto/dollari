import requests

payload = {
  "object": "whatsapp_business_account",
  "entry": [{"id": "828692143573688","changes": [{"value": {"messaging_product": "whatsapp", "messages": [
              {"from": "393711741209","type": "image","image": {"id": "123456"}}
            ]
          },"field": "messages"}]}]}
requests.post('http://127.0.0.1:5000/webhook', json=payload)
print("Step 3 simulated")
