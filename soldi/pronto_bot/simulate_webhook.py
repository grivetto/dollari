import requests

payload = {
  "object": "whatsapp_business_account",
  "entry": [
    {
      "id": "828692143573688",
      "changes": [
        {
          "value": {
            "messaging_product": "whatsapp",
            "metadata": {
              "display_phone_number": "15555555555",
              "phone_number_id": "1043648508828754"
            },
            "contacts": [
              {
                "profile": {
                  "name": "Sergio"
                },
                "wa_id": "393711741209"
              }
            ],
            "messages": [
              {
                "from": "393711741209",
                "id": "wamid.HBgLMSY4Nzg3Njg5MjYVAgASGAEQAT",
                "timestamp": "1710924000",
                "text": {
                  "body": "Ho un problema con la caldaia"
                },
                "type": "text"
              }
            ]
          },
          "field": "messages"
        }
      ]
    }
  ]
}

requests.post('http://127.0.0.1:5000/webhook', json=payload)
print("Webhook simulated!")
