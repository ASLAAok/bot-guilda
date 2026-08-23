import os
import time
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# ==============================================================================
# CONFIGURAÇÕES DA GREEN API (MANTIDAS)
# ==============================================================================
ID_INSTANCE = "710722717263"
API_TOKEN_INSTANCE = os.getenv("API_TOKEN_INSTANCE", "aad70570e44043fa956d2c159e8a3a8a8c1ca3f1a1b44e268d")
URL_BASE = os.getenv("URL_BASE", f"https://greenapi.com{ID_INSTANCE}")

admins_env = os.getenv("ADMINS_LIST", "")
ADMINISTRADORES_PERMITIDOS = [adm.strip() + "@c.us" if not adm.endswith("@c.us") else adm.strip() for adm in admins_env.split(",") if adm.strip()]

# BANCO DE DADOS DE SILENCIADOS (Guarda quem está mutado e até que horas)
MEMBROS_MUTADOS = {}

# BANCO DE DADOS DE SENSIBILIDADE
BANCO_DE_SENSI = {
    "/iphone 11": "📱 *SENSI: iPHONE 11* 🎯\n\n• Geral: 100\n• Ponto Vermelho: 92\n• Mira 2x: 98\n• Mira 4x: 96\n• AWM: 45\n💡 _Dica: Perfeita para armas de um tiro (Desert/M1014)._",
    "/iphone 12": "📱 *SENSI: iPHONE 12* 🎯\n\n• Geral: 98\n• Ponto Vermelho: 95\n• Mira 2x: 100\n• Mira 4x: 94\n• AWM: 50\n💡 _Dica: Puxada leve e reta para não passar da cabeça!_",
    "/iphone 13": "📱 *SENSI: iPHONE 13* 🎯\n\n• Geral: 95\n• Ponto Vermelho: 90\n• Mira 2x: 96\n• Mira 4x: 92\n• AWM: 40",
    "/iphone xr": "📱 *SENSI: iPHONE XR* 🎯\n\n• Geral: 95\n• Ponto Vermelho: 88\n• Mira 2x: 95\n• Mira 4x: 92\n• AWM: 40",
    "/poco x3": "📱 *SENSI: POCO X3* 🎯\n\n• Geral: 97\n• Ponto Vermelho: 95\n• Mira 2x: 100\n• Mira 4x: 98\n• DPI Recomendada: 560\n💡 _Dica: Puxada média com meia-lua no botão._",
    "/poco f5": "📱 *SENSI: POCO F5* 🎯\n\n• Geral: 100\n• Ponto Vermelho: 92\n• Mira 2x: 98\n• Mira 4x: 95\n• DPI Recomendada: 510",
    "/redmi note 10": "📱 *SENSI: REDMI NOTE 10* 🎯\n\n• Geral: 100\n• Ponto Vermelho: 90\n• Mira 2x: 95\n• Mira 4x: 95\n• DPI Recomendada: 600",
    "/redmi note 11": "📱 *SENSI: REDMI NOTE 11* 🎯\n\n• Geral: 98\n• Ponto Vermelho: 93\n• Mira 2x: 96\n• Mira 4x: 94\n• DPI Recomendada: 580",
    "/samsung a32": "📱 *SENSI: SAMSUNG A32* 🎯\n\n• Geral: 92\n• Ponto Vermelho: 92\n• Mira 2x: 96\n• Mira 4x: 90\n• DPI Recomendada: 720",
    "/samsung a54": "📱 *SENSI: SAMSUNG A54* 🎯\n\n• Geral: 96\n• Ponto Vermelho: 89\n• Mira 2x: 94\n• Mira 4x: 92\n• DPI Recomendada: 620",
    "/moto g60": "📱 *SENSI: MOTOROLA G60* 🎯\n\n• Geral: 100\n• Ponto Vermelho: 95\n• Mira 2x: 100\n• Mira 4x: 97\n• DPI Recomendada: 540",
    "/moto g200": "📱 *SENSI: MOTOROLA G200* 🎯\n\n• Geral: 94\n• Ponto Vermelho: 91\n• Mira 2x: 95\n• Mira 4x: 90\n• DPI Recomendada: 480"
}

def enviar_mensagem(chat_id, texto):
    url = f"{URL_BASE}/sendMessage/{API_TOKEN_INSTANCE}"
    payload = {"chatId": chat_id, "message": texto}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

def apagar_mensagem(chat_id, message_id):
    url = f"{URL_BASE}/deleteMessage/{API_TOKEN_INSTANCE}"
    payload = {"chatId": chat_id, "messageId": message_id}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Erro ao apagar mensagem: {e}")
@app.route("/webhook", methods=["POST"])
def webhook():
    dados = request.get_json()
    type_webhook = dados.get("typeWebhook")

    if type_webhook == "groupNotify":
        status_grupo = dados.get("statusNotify")
        if status_grupo in ["addArea", "inviteArea"]:
            chat_id = dados.get("chatId")
            nome_usuario = dados.get("senderData", {}).get("senderName", "Recruta")
            boas_vindas = f"👋 *BOAS VINDAS, {nome_usuario.upper()}!* 🔥\n\nFicamos muito felizes por entrares na nossa guilda! Dá o teu melhor nos treinos e respeita os crias. Tamo junto! 🚀"
            enviar_mensagem(chat_id, boas_vindas)

    elif type_webhook == "incomingMessageReceived":
        dados_mensagem = dados.get("messageData", {})
        message_id = dados.get("idMessage")
        
        if dados_mensagem.get("typeMessage") == "textMessage":
            chat_id = dados["senderData"]["chatId"]
            sender_id = dados["senderData"]["sender"]
            texto_original = dados_mensagem["textMessageData"]["textMessage"].strip()
            texto_minusculo = texto_original.lower()
            
            # ==================================================================
            # CONTROLO DE MUTE (Se o jogador estiver mutado, apaga instantaneamente)
            # ==================================================================
            if sender_id in MEMBROS_MUTADOS:
                if time.time() < MEMBROS_MUTADOS[sender_id]:
                    apagar_mensagem(chat_id, message_id)
                    return jsonify({"status": "apagado"}), 200
                else:
                    del MEMBROS_MUTADOS[sender_id]

            # ==================================================================
            # COMANDOS LIBERADOS PARA QUALQUER MEMBRO
            # ==================================================================
            if texto_minusculo == "/sensi":
                lista_telemoveis = "📱 *TELEMÓVEIS DISPONÍVEIS NO BOT* 🎯\n\n" \
                                   "Digita um dos comandos abaixo exatamente como está escrito para veres a sensi:\n\n" \
                                   "🍏 *iPhones:*\n" \
                                   "• `/iphone 11`\n• `/iphone 12`\n• `/iphone 13`\n• `/iphone xr`\n\n" \
                                   "🔥 *Xiaomi / Poco / Redmi:*\n" \
                                   "• `/poco x3`\n• `/poco f5`\n• `/redmi note 10`\n• `/redmi note 11`\n\n" \
                                   "🔷 *Samsung & Motorola:*\n" \
                                   "• `/samsung a32`\n• `/samsung a54`\n• `/moto g60`\n• `/moto g200`\n\n" \
                                   "⚠️ *Se o seu telemóvel não aparecer diga o seu que nós adicionamos!*\n\n" \
                                   "💡 _Exemplo: Se digitares /iphone 12 o bot responde na hora!_"
                enviar_mensagem(chat_id, lista_telemoveis)
            
            elif texto_minusculo in BANCO_DE_SENSI:
                enviar_mensagem(chat_id, BANCO_DE_SENSI[texto_minusculo])

            # ==================================================================
            # COMANDOS DE ADMINISTRAÇÃO BLOQUEADOS (APENAS ADMs)
            # ==================================================================
            if sender_id in ADMINISTRADORES_PERMITIDOS:
                
                # COMANDO CORRIGIDO DE MUTE
                if texto_minusculo.startswith("/mute "):
                    try:
                        partes = texto_original.split()
                        num_alvo = partes[1].replace("+", "").replace(" ", "")
                        minutos = int(partes[2])
                        
                        versao_com_9 = num_alvo if num_alvo.endswith("@c.us") else num_alvo + "@c.us"
                        versao_sem_9 = versao_com_9
                        
                        if versao_com_9.startswith("3519"):
                            versao_sem_9 = "351" + versao_com_9[4:]
                        elif versao_com_9.startswith("55"):
                            versao_sem_9 = versao_com_9[:4] + versao_com_9[5:]

                        tempo_fim = time.time() + (minutos * 60)
                        MEMBROS_MUTADOS[versao_com_9] = tempo_fim
                        MEMBROS_MUTADOS[versao_sem_9] = tempo_fim
                        
                        enviar_mensagem(chat_id, f"🤫 *CRIADO CASTIGADO!* O jogador @{num_alvo} foi silenciado por *{minutos} minutos* por quebrar as regras.")
                    except Exception:
                        enviar_mensagem(chat_id, "⚠️ *Erro!* Usa: `/mute [Número] [Minutos]`\nExemplo: `/mute 351912345678 10`")

                # COMANDO CORRIGIDO DE UNMUTE
                elif texto_minusculo.startswith("/unmute "):
                    try:
                        partes = texto_original.split()
                        num_alvo = partes[1].replace("+", "").replace(" ", "")
                        
                        versao_com_9 = num_alvo if num_alvo.endswith("@c.us") else num_alvo + "@c.us"
                        versao_sem_9 = versao_com_9
                        
                        if versao_com_9.startswith("3519"):
                            versao_sem_9 = "351" + versao_com_9[4:]
                        elif versao_com_9.startswith("55"):
                            versao_sem_9 = versao_com_9[:4] + versao_com_9[5:]
                            
                        encontrado = False
                        if versao_com_9 in MEMBROS_MUTADOS:
                            del MEMBROS_MUTADOS[versao_com_9]
                            encontrado = True
                        if versao_sem_9 in MEMBROS_MUTADOS:
                            del MEMBROS_MUTADOS[versao_sem_9]
                            encontrado = True
                            
                        if encontrado:
                            enviar_mensagem(chat_id, f"🔊 *PERDÃO CONCEDIDO!* O jogador @{num_alvo} foi desmutado e já pode voltar a falar.")
                        else:
                            enviar_mensagem(chat_id, "⚠️ Este jogador não está mutado de momento.")
                    except Exception:
                        enviar_mensagem(chat_id, "⚠️ *Erro!* Usa: `/unmute [Número]`")

                # OUTROS COMANDOS MANTIDOS
                elif texto_minusculo.startswith("/xtreino "):
                    horarios = texto_original[9:].strip()
                    if "-" in horarios:
                        try:
                            h1, h2 = horarios.split("-")
                            aviso_xtreino = f"📢 *AVISO DE XTREINO DA GUILDA!* 📢\n\n⚔️ *Início:* {h1.strip()}\n🏆 *Fim:* {h2.strip()}\n\nSejam pontuais, preparem os vossos squads e fiquem prontos no lobby! 🎮"
                            enviar_mensagem(chat_id, aviso_xtreino)
                        except Exception:
                            enviar_mensagem(chat_id, "⚠️ *Erro no formato!* Usa exatamente assim: `/xtreino 19:00-20:00`")
                    else:
                        enviar_mensagem(chat_id, "⚠️ *Erro!* Separe os horários por um hífen. Exemplo: `/xtreino 20:00-21:00`")

                elif texto_minusculo == "/regras":
                    regras_texto = "📜 *REGRAS OFICIAIS DA GUILDA* 📜\n\n1️⃣ *Lealdade* – Fechados com a guilda em qualquer situação.\n2️⃣ *Respeito* – Sem toxicidade com os membros ou liderança.\n3️⃣ *7.500 Pontos de Honra* Semanais obrigatórios.\n4️⃣ *50 Pontos* na Guerra de Guilda.\n\n⚠️ _O descumprimento das regras resultará em remoção direta._"
                    enviar_mensagem(chat_id, regras_texto)

                elif texto_minusculo == "/guerraguilda":
                    guerra_texto = "⚔️ *GUERRA DE GUILDA (FF)* ⚔️\n\n📅 *Dias:* Quarta, Sexta e Sábado\n⏰ *Horário:* Das 18:00 às 22:00\n\n⚠️ _Fiquem atentos ao grupo! Presença e foco total para pontuar na tabela!_"
                    enviar_mensagem(chat_id, guerra_texto)

    return jsonify({"status": "sucesso"}), 200

if __name__ == "__main__":
    app.run(port=5000)

