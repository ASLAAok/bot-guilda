import os
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

# ARMAZENAMENTO DE DADOS (Salvo na memória do servidor do Render)
POSICOES_JOGADORES = {}
ADVERTENCIAS_JOGADORES = {}

# BANCO DE DADOS DE SENSIBILIDADE FIXA
BANCO_DE_SENSI = {
    "/iphone 11": "📱 *SENSI: iPHONE 11* 🎯\n\n• Geral: 100\n• Ponto Vermelho: 92\n• Mira 2x: 98\n• Mira 4x: 96\n• AWM: 45\n💡 _Dica: Perfeita para armas de um tiro (Desert/M1014)._",
    "/iphone 12": "📱 *SENSI: iPHONE 12* 🎯\n\n• Geral: 98\n• Ponto Vermelho: 95\n• Mira 2x: 100\n• Mira 4x: 94\n• AWM: 50\n💡 _Dica: Puxada leve e reta para não passar da cabeça!_",
    "/iphone 13": "📱 *SENSI: iPHONE 13* 🎯\n\n• Geral: 95\n• Ponto Vermelho: 90\n• Mira 2x: 96\n• Mira 4x: 92\n• AWM: 40\n💡 _Dica: Mira muito firme. Sobe o capa com suavidade!_",
    "/iphone xr": "📱 *SENSI: iPHONE XR* 🎯\n\n• Geral: 95\n• Ponto Vermelho: 88\n• Mira 2x: 95\n• Mira 4x: 92\n• AWM: 40",
    "/poco x3": "📱 *SENSI: POCO X3* 🎯\n\n• Geral: 97\n• Ponto Vermelho: 95\n• Mira 2x: 100\n• Mira 4x: 98\n• DPI Recomendada: 560\n💡 _Dica: Puxada média com meia-lua no botão._",
    "/poco f5": "📱 *SENSI: POCO F5* 🎯\n\n• Geral: 100\n• Ponto Vermelho: 92\n• Mira 2x: 98\n• Mira 4x: 95\n• DPI Recomendada: 510",
    "/redmi note 10": "📱 *SENSI: REDMI NOTE 10* 🎯\n\n• Geral: 100\n• Ponto Vermelho: 90\n• Mira 2x: 95\n• Mira 4x: 95\n• DPI Recomendada: 600",
    "/redmi note 11": "📱 *SENSI: REDMI NOTE 11* 🎯\n\n• Geral: 98\n• Ponto Vermelho: 93\n• Mira 2x: 96\n• Mira 4x: 94\n• DPI Recomendada: 580",
    "/redmi note 13": "📱 *SENSI: REDMI NOTE 13* 🎯\n\n• Geral: 99\n• Ponto Vermelho: 95\n• Mira 2x: 98\n• Mira 4x: 96\n• DPI Recomendada: 490\n💡 _Dica: Sensi muito estável para dar capas seguidos de SMG!_",
    "/redmi 12": "📱 *SENSI: REDMI 12* 🎯\n\n• Geral: 96\n• Ponto Vermelho: 94\n• Mira 2x: 97\n• Mira 4x: 95\n• DPI Recomendada: 450\n💡 _Dica: Puxada um pouco mais rápida por causa do ecrã de 90Hz._",
    "/redmi 13c": "📱 *SENSI: REDMI 13C* 🎯\n\n• Geral: 100\n• Ponto Vermelho: 96\n• Mira 2x: 95\n• Mira 4x: 93\n• DPI Recomendada: 520\n💡 _Dica: Sensi um pouco pesada, puxa o botão de atirar com força!_",
    "/realme note 60": "📱 *SENSI: REALME NOTE 60* 🎯\n\n• Geral: 100\n• Ponto Vermelho: 95\n• Mira 2x: 98\n• Mira 4x: 96\n• DPI Recomendada: 420\n💡 _Dica: Botão de atirar posicionado em 45% melhora muito o capa!_",
    "/honor 400 lite": "📱 *SENSI: HONOR 400 LITE* 🎯\n\n• Geral: 95\n• Ponto Vermelho: 89\n• Mira 2x: 94\n• Mira 4x: 91\n• DPI Recomendada: 500\n💡 _Dica: Sensi muito leve, ideal para SMG (MP40/UMP)._",
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
        
        if dados_mensagem.get("typeMessage") == "textMessage":
            chat_id = dados["senderData"]["chatId"]
            sender_id = dados["senderData"]["sender"]
            texto_original = dados_mensagem["textMessageData"]["textMessage"].strip()
            texto_minusculo = texto_original.lower()

            # ==================================================================
            # MENU DE AJUDA APENAS COM OS COMANDOS QUE JÁ APLICASTE 🇵🇹
            # ==================================================================
            if texto_minusculo == "/ajuda":
                menu_ajuda = "🤖 *PAINEL DE COMANDOS – BOT DA GUILDA* 🇵🇹\n\n" \
                             "🟢 *COMANDOS DOS JOGADORES (Gerais):*\n" \
                             "• `/sensi` – Mostra os telemóveis cadastrados no bot.\n" \
                             "• `/[telemóvel]` – Vê a sensi exata (Ex: `/redmi 12`).\n" \
                             "• `/posicoes` – Lista as 4 funções oficiais da guilda.\n" \
                             "• `/escolherposicao [nome]` – Salva a tua função (Ex: `full gas`).\n\n" \
                             "👑 *COMANDOS EXCLUSIVOS DE ADM (Bloqueados):*\n" \
                             "• `/advertencia [número] [motivo]` – Aplica advertência.\n" \
                             "• `/regras` – Envia as regras oficiais da guilda.\n" \
                             "• `/guerraguilda` – Envia os dias e horários da Guerra.\n" \
                             "• `/xtreino [hora-hora]` – Cria o aviso de treino (Ex: `21:00-23:00`)."
                enviar_mensagem(chat_id, menu_ajuda)
            # ==================================================================
            # SISTEMA SÉRIO: SISTEMA DE ADVERTÊNCIAS (MÁXIMO 4)
            # ==================================================================
            elif texto_minusculo.startswith("/advertencia"):
                if sender_id in ADMINISTRADORES_PERMITIDOS:
                    try:
                        partes = texto_original.split(maxsplit=2)
                        
                        if len(partes) == 2:
                            num_alvo = partes.replace("+", "").replace(" ", "")
                            id_alvo = num_alvo if num_alvo.endswith("@c.us") else num_alvo + "@c.us"
                            qtd = ADVERTENCIAS_JOGADORES.get(id_alvo, 0)
                            enviar_mensagem(chat_id, f"📋 *FICHA DISCIPLINAR:* O jogador @{num_alvo} possui atualmente *{qtd}/4* advertências registadas.")
                        
                        elif len(partes) >= 3:
                            num_alvo = partes.replace("+", "").replace(" ", "")
                            motivo = partes.strip()
                            id_alvo = num_alvo if num_alvo.endswith("@c.us") else num_alvo + "@c.us"
                            
                            ADVERTENCIAS_JOGADORES[id_alvo] = ADVERTENCIAS_JOGADORES.get(id_alvo, 0) + 1
                            nova_qtd = ADVERTENCIAS_JOGADORES[id_alvo]
                            
                            if nova_qtd >= 4:
                                ADVERTENCIAS_JOGADORES[id_alvo] = 4
                                alerta_vermelho = f"🚨 *PUNIÇÃO MÁXIMA ATINGIDA!* 🚨\n\nO jogador @{num_alvo} recebeu a sua *4ª advertência*.\n• *Motivo final:* {motivo}\n\n❌ *SISTEMA:* Limite de 4/4 atingido. Os Administradores devem **REMOVER IMEDIATAMENTE** este gajo da guilda!"
                                enviar_mensagem(chat_id, alerta_vermelho)
                            else:
                                msg_adv = f"⚠️ *ADVERTÊNCIA APLICADA!* ⚠️\n\nO jogador @{num_alvo} foi advertido oficialmente.\n• *Motivo:* {motivo}\n• *Ficha Atual:* *{nova_qtd}/4* advertências.\n\n📌 _Lembrete: Ao atingir a 4ª advertência, a remoção da guilda será automática!_"
                                enviar_mensagem(chat_id, msg_adv)
                    except Exception:
                        enviar_mensagem(chat_id, "⚠️ *Erro!* Use: `/advertencia [Número] [Motivo]`")

            # SISTEMA DE POSIÇÕES DA GUILDA
            elif texto_minusculo == "/posicoes":
                enviar_mensagem(chat_id, "⚔️ *POSIÇÕES OFICIAIS DA GUILDA* 🛡️\n\n💥 1️⃣ *Rush* – Avança primeiro.\n🎯 2️⃣ *Suporte* – Dá cobertura com Snipers.\n🏃‍♂️ 3️⃣ *Full Gas* – Mestre da rotação.\n🩹 4️⃣ *Curandeiro* – Focado em reviver.\n\n📌 *Como escolher:* `/escolherposicao [Nome]`")

            elif texto_minusculo.startswith("/escolherposicao "):
                escolha = texto_minusculo[17:].strip()
                if escolha in ["rush", "suporte", "full gas", "curandeiro"]:
                    POSICOES_JOGADORES[sender_id] = escolha.upper()
                    enviar_mensagem(chat_id, f"✅ *FUNÇÃO ATUALIZADA!* A tua posição oficial é: *{escolha.upper()}*! 🔥")

            # COMANDOS DE SENSI MANTIDOS
            elif texto_minusculo == "/sensi":
                enviar_mensagem(chat_id, "📱 *TELEMÓVEIS DISPONÍVEIS NO BOT* 🎯\n\n🍏 *iPhones:* `/iphone 11` | `/iphone 12` | `/iphone 13` | `/iphone xr`\n🔥 *Xiaomi/Poco:* `/poco x3` | `/poco f5` | `/redmi note 10` | `/redmi note 11` | `/redmi note 13` | `/redmi 12` | `/redmi 13c`\n⚡ *Novos:* `/realme note 60` | `/honor 400 lite`\n🔷 *Outros:* `/samsung a32` | `/samsung a54` | `/moto g60` | `/moto g200`\n\n⚠️ *Se o seu telemóvel não aparecer diga o seu que nós adicionamos!*")
            
            elif texto_minusculo in BANCO_DE_SENSI:
                enviar_mensagem(chat_id, BANCO_DE_SENSI[texto_minusculo])

            # COMANDOS DE ADMINISTRAÇÃO BLOQUEADOS (MANTIDOS)
            if sender_id in ADMINISTRADORES_PERMITIDOS:
                if texto_minusculo.startswith("/xtreino "):
                    horarios = texto_original[9:].strip()
                    if "-" in horarios:
                        try:
                            h1, h2 = horarios.split("-")
                            enviar_mensagem(chat_id, f"📢 *AVISO DE XTREINO DA GUILDA!* 📢\n\n⚔️ *Início:* {h1.strip()}\n🏆 *Fim:* {h2.strip()}\n\nSejam pontuais! 🎮")
                        except Exception: enviar_mensagem(chat_id, "⚠️ *Erro!* Usa: `/xtreino 19:00-20:00`")

                elif texto_minusculo == "/regras":
                    enviar_mensagem(chat_id, "📜 *REGRAS OFICIAIS DA GUILDA* 📜\n\n1️⃣ Lealdade total.\n2️⃣ Sem toxicidade.\n3️⃣ 7.500 Pontos de Honra.\n4️⃣ 50 Pontos na Guerra.")

                elif texto_minusculo == "/guerraguilda":
                    enviar_mensagem(chat_id, "⚔️ *GUERRA DE GUILDA (FF)* ⚔️\n\n📅 Dias: Quarta, Sexta e Sábado\n⏰ Horário: Das 18:00 às 22:00")
    return jsonify({"status": "sucesso"}), 200

if __name__ == "__main__":
    app.run(port=5000)
