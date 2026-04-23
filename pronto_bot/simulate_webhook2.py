import requests

payload = {
  "object": "whatsapp_business_account",
  "entry": [{"id": "828692143573688","changes": [{"value": {"messaging_product": "whatsapp", "messages": [
              {"from": "393711741209","type": "text","text": {"body": "Il lavandino perde acqua a dirotto"}}
            ]
          },"field": "messages"}]}]}
requests.post('http://127.0.0.1:5000/webhook', json=payload)
print("Step 2 simulated")
