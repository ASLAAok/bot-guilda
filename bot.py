import os
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ==============================================================================
# CONFIGURAÇÕES DA GREEN API (Puxa os dados direto do Render)
# ==============================================================================
ID_INSTANCE = "710722717263"
API_TOKEN_INSTANCE = os.getenv("API_TOKEN_INSTANCE", "aad70570e44043fa956d2c159e8a3a8a8c1ca3f1a1b44e268d")
URL_BASE = f"https://greenapi.com{ID_INSTANCE}"

# Captura a lista de ADMs salvos no Render e limpa os espaços
admins_env = os.getenv("ADMINS_LIST", "")
ADMINISTRADORES_PERMITIDOS = [adm.strip() + "@c.us" if not adm.endswith("@c.us") else adm.strip() for adm in admins_env.split(",") if adm.strip()]

def enviar_mensagem(chat_id, texto):
    """Função auxiliar para enviar mensagens de texto para o WhatsApp."""
    url = f"{URL_BASE}/sendMessage/{API_TOKEN_INSTANCE}"
    payload = {"chatId": chat_id, "message": texto}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

@app.route("/webhook", methods=["POST"])
def webhook():
    dados = request.get_json()
    type_webhook = dados.get("typeWebhook")

    # --------------------------------------------------------------------------
    # 1. EVENTO DE BOAS-VINDAS (Quando alguém entra no grupo)
    # --------------------------------------------------------------------------
    if type_webhook == "groupNotify":
        status_grupo = dados.get("statusNotify")
        if status_grupo in ["addArea", "inviteArea"]:
            chat_id = dados.get("chatId")
            nome_usuario = dados.get("senderData", {}).get("senderName", "Recruta")
            
            boas_vindas = f"👋 *BOAS VINDAS, {nome_usuario.upper()}!* 🔥\n\n" \
                           "Ficamos muito felizes por entrares na nossa guilda! " \
                           "Dá o teu melhor nos treinos e respeita os crias. Tamo junto! 🚀"
            enviar_mensagem(chat_id, boas_vindas)

    # --------------------------------------------------------------------------
    # 2. EVENTO DE MENSAGENS EM TEMPO REAL (Comandos de Texto)
    # --------------------------------------------------------------------------
    elif type_webhook == "incomingMessageReceived":
        dados_mensagem = dados.get("messageData", {})
        
        if dados_mensagem.get("typeMessage") == "textMessage":
            chat_id = dados["senderData"]["chatId"]
            sender_id = dados["senderData"]["sender"]
            texto_original = dados_mensagem["textMessageData"]["textMessage"].strip()
            texto_minusculo = texto_original.lower()
            
            # FILTRO DE SEGURANÇA: Só responde se o número estiver na lista de ADMs
            if sender_id in ADMINISTRADORES_PERMITIDOS:
                
                # COMANDO: /xtreino "horario1"-"horario2" (Exemplo: /xtreino 20:00-22:00)
                if texto_minusculo.startswith("/xtreino "):
                    horarios = texto_original[9:].strip()
                    if "-" in horarios:
                        try:
                            h1, h2 = horarios.split("-")
                            aviso_xtreino = f"📢 *AVISO DE XTREINO DA GUILDA!* 📢\n\n" \
                                            f"⚔️ *Início:* {h1.strip()}\n" \
                                            f"🏁 *Fim:* {h2.strip()}\n\n" \
                                            f"Sejam pontuais, preparem os vossos squads e fiquem prontos no lobby! 🎮"
                            enviar_mensagem(chat_id, aviso_xtreino)
                        except Exception:
                            enviar_mensagem(chat_id, "⚠️ *Erro no formato!* Usa exatamente assim: `/xtreino 19:00-20:00`")
                    else:
                        enviar_mensagem(chat_id, "⚠️ *Erro!* Separe os horários por um hífen. Exemplo: `/xtreino 20:00-21:00`")

                # COMANDO: /regras
                elif texto_minusculo == "/regras":
                    regras_texto = "📜 *REGRAS OFICIAIS DA GUILDA* 📜\n\n" \
                                   "1️⃣ *Lealdade* – Fechados com a guilda em qualquer situação.\n" \
                                   "2️⃣ *Respeito* – Sem toxicidade com os membros ou liderança.\n" \
                                   "3️⃣ *7.500 Pontos de Honra* Semanais obrigatórios.\n" \
                                   "4️⃣ *50 Pontos* na Guerra de Guilda.\n\n" \
                                   "⚠️ _O descumprimento das regras resultará em remoção direta._"
                    enviar_mensagem(chat_id, regras_texto)

                # COMANDO: /guerraguilda
                elif texto_minusculo == "/guerraguilda":
                    guerra_texto = "⚔️ *GUERRA DE GUILDA (FF)* ⚔️\n\n" \
                                   "📅 *Dias:* Quarta, Sexta e Sábado\n" \
                                   "⏰ *Horário:* Das 18:00 às 22:00\n\n" \
                                   "⚠️ _Fiquem atentos ao grupo! Presença e foco total para pontuar na tabela!_"
                    enviar_mensagem(chat_id, guerra_texto)

            else:
                if texto_minusculo.startswith(("/", "!")):
                    print(f"Comando bloqueado: Usuário comum {sender_id} tentou rodar {texto_minusculo}")

    return jsonify({"status": "sucesso"}), 200

if __name__ == "__main__":
    app.run(port=5000)
