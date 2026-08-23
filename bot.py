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

# ARMAZENAMENTO DE POSIÇÕES DOS JOGADORES (Salvo na memória do servidor)
POSICOES_JOGADORES = {}

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
    "/redmi 12": "📱 *SENSI: REDMI 12* 🎯\n\n• Geral: 96\n• Ponto Vermelho: 94\n• Mira 2x: 97\n• Mira 4x: 95\n• DPI Recomendada: 450\n💡 _Dica: Puxada um pouco mais rápida por causa do ecrã de 90Hz._",
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
            # NOVO COMANDO: MENU DE AJUDA DO BOT (/ajuda)
            # ==================================================================
            if texto_minusculo == "/ajuda":
                menu_ajuda = "🤖 *PAINEL DE COMANDOS – BOT DA GUILDA* 🇵🇹\n\n" \
                             "Aqui tens todos os comandos ativos organizados para a tropa:\n\n" \
                             "🟢 *COMANDOS DOS JOGADORES (Todos Podem Usar):*\n" \
                             "• `/sensi` – Lista de telemóveis e configurações para dar capa.\n" \
                             "• `/[nome do telemóvel]` – Mostra a sensi exata (Ex: `/redmi 12`).\n" \
                             "• `/posicoes` – Abre a lista de funções oficiais da guilda.\n" \
                             "• `/escolherposicao [nome]` – Registra a tua função (Ex: `/escolherposicao rush`).\n" \
                             "• `/minhaposicao` – Consulta qual é a tua função ativa na guilda.\n\n" \
                             "👑 *COMANDOS EXCLUSIVOS DE ADM (Bloqueados):*\n" \
                             "• `/regras` – Dispara a lista com as regras oficiais do grupo.\n" \
                             "• `/guerraguilda` – Envia os dias e horários da Guerra de Guildas.\n" \
                             "• `/xtreino [hora-hora]` – Cria um aviso oficial de treino (Ex: `/xtreino 21:00-23:00`).\n\n" \
                             "💡 _Nota: Digita os comandos exatamente como estão escritos para o bot responder._"
                enviar_mensagem(chat_id, menu_ajuda)

            # ==================================================================
            # SISTEMA DE POSIÇÕES DA GUILDA
            # ==================================================================
            elif texto_minusculo == "/posicoes":
                menu_posicoes = "⚔️ *POSIÇÕES OFICIAIS DA GUILDA* 🛡️\n\n" \
                                "Aqui tens as 4 funções disponíveis para o competitivo:\n\n" \
                                "💥 1️⃣ *Rush* – O gajo que avança primeiro e abre espaço a dar capa.\n" \
                                "🎯 2️⃣ *Suporte* – Fica atrás a dar cobertura com armas de sniper/carapina.\n" \
                                "🏃‍♂️ 3️⃣ *Full Gas* – O mestre da rotação que garante os pontos de mapa.\n" \
                                "🩹 4️⃣ *Curandeiro* – Focado em salvar a equipa, reviver e gerir os kits.\n\n" \
                                "📌 *Como escolher a tua:* Digita `/escolherposicao [Nome]`\n" \
                                "💡 _Exemplo: /escolherposicao full gas_"
                enviar_mensagem(chat_id, menu_posicoes)

            elif texto_minusculo.startswith("/escolherposicao "):
                escolha = texto_minusculo[17:].strip()
                if escolha in ["rush", "suporte", "full gas", "curandeiro"]:
                    POSICOES_JOGADORES[sender_id] = escolha.upper()
                    enviar_mensagem(chat_id, f"✅ *FUNÇÃO ATUALIZADA!* A partir de agora a tua posição oficial na guilda é: *{escolha.upper()}*! Destrói nos treinos! 🔥")
                else:
                    enviar_mensagem(chat_id, "⚠️ *Posição inválida!* Escolha exatamente uma destas quatro:\n• `rush`\n• `suporte`\n• `full gas`\n• `curandeiro`")

            elif texto_minusculo == "/minhaposicao":
                if sender_id in POSICOES_JOGADORES:
                    enviar_mensagem(chat_id, f"🔰 *TUA FICHA:* Atualmente estás registado no sistema como: *{POSICOES_JOGADORES[sender_id]}* ⚔️")
                else:
                    enviar_mensagem(chat_id, "⚠️ Ainda não tens nenhuma função registada. Digita `/posicoes` para escolheres uma!")

            # ==================================================================
            # COMANDOS DE SENSI MANTIDOS
            # ==================================================================
            elif texto_minusculo == "/sensi":
                lista_telemoveis = "📱 *TELEMÓVEIS DISPONÍVEIS NO BOT* 🎯\n\n" \
                                   "Digita um dos comandos abaixo exatamente como está escrito para veres a sensi:\n\n" \
                                   "🍏 *iPhones:*\n" \
                                   "• `/iphone 11`\n• `/iphone 12`\n• `/iphone 13`\n• `/iphone xr`\n\n" \
                                   "🔥 *Xiaomi / Poco / Redmi:*\n" \
                                   "• `/poco x3`\n• `/poco f5`\n• `/redmi note 10`\n• `/redmi note 11`\n• `/redmi 12`\n\n" \
                                   "⚡ *Novos Adicionados:*\n" \
                                   "• `/realme note 60`\n• `/honor 400 lite`\n\n" \
                                   "🔷 *Samsung & Motorola:*\n" \
                                   "• `/samsung a32`\n• `/samsung a54`\n• `/moto g60`\n• `/moto g200`\n\n" \
                                   "⚠️ *Se o seu telemóvel não aparecer diga o seu que nós adicionamos!*\n\n" \
                                   "💡 _Exemplo: Se digitares /redmi 12 o bot responde na hora!_"
                enviar_mensagem(chat_id, lista_telemoveis)
            
            elif texto_minusculo in BANCO_DE_SENSI:
                enviar_mensagem(chat_id, BANCO_DE_SENSI[texto_minusculo])

            # ==================================================================
            # COMANDOS DE ADMINISTRAÇÃO BLOQUEADOS (APENAS ADMs)
            # ==================================================================
            if sender_id in ADMINISTRADORES_PERMITIDOS:
                if texto_minusculo.startswith("/xtreino "):
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
