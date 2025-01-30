import os
import json
import requests
from flask import Flask, request
from dotenv import load_dotenv
import telebot

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
MERCADO_PAGO_ACCESS_TOKEN = os.getenv("MERCADO_PAGO_ACCESS_TOKEN_PROD")
CHAVE_API = os.getenv("CHAVE_API")
GRUPO_ID = os.getenv("GRUPO_ID")  # ID do grupo no Telegram
bot = telebot.TeleBot(CHAVE_API)

app = Flask(__name__)


# Webhook para notificações de pagamento
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if not data:
        return "Nenhum dado recebido", 400

    # Verificar se o pagamento foi aprovado
    if "type" in data and data["type"] == "payment":
        payment_id = data.get("data", {}).get("id")
        if payment_id:
            processar_pagamento(payment_id)

    return "OK", 200


def processar_pagamento(payment_id):
    """
    Verifica o status do pagamento no Mercado Pago e, se aprovado, envia um link temporário do grupo no Telegram.
    """
    url = f"https://api.mercadopago.com/v1/payments/{payment_id}?access_token={MERCADO_PAGO_ACCESS_TOKEN}"
    response = requests.get(url)

    if response.status_code == 200:
        payment_info = response.json()

        if payment_info.get("status") == "approved":
            user_id = payment_info.get("payer", {}).get("id")
            enviar_link_grupo(user_id)
        else:
            print("Pagamento ainda não aprovado.")
    else:
        print("Erro ao verificar pagamento.")


def enviar_link_grupo(user_id):
    """
    Gera um link temporário de convite e envia para o usuário no Telegram.
    """
    url = f"https://api.telegram.org/bot{CHAVE_API}/exportChatInviteLink?chat_id={GRUPO_ID}"
    response = requests.get(url)

    if response.status_code == 200:
        link_grupo = response.json().get("result")

        if link_grupo:
            bot.send_message(user_id,
                             f"🎉 Seu pagamento foi confirmado! Acesse o grupo através deste link:\n{link_grupo}")
        else:
            print("Erro ao gerar o link do grupo.")
    else:
        print("Erro ao obter link de convite.")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
