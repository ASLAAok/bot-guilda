import os
import random
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
            # MENU DE AJUDA EXPANDIDO (/ajuda)
            # ==================================================================
            if texto_minusculo == "/ajuda":
                menu_ajuda = "🤖 *PAINEL DE COMANDOS – BOT DA GUILDA* 🇵🇹\n\n" \
                             "🟢 *COMANDOS DOS JOGADORES:*\n" \
                             "• `/sensi` – Lista de telemóveis disponíveis.\n" \
                             "• `/[telemóvel]` – Vê a sensi exata (Ex: `/iphone 13`).\n" \
                             "• `/sensirapida` – Gera uma sensi aleatória coringa na hora. ⚡\n" \
                             "• `/posicoes` – Lista de funções da guilda.\n" \
                             "• `/escolherposicao [nome]` – Escolhe a tua função.\n" \
                             "• `/minhaposicao` – Vê a tua ficha ativa.\n\n" \
                             "🔥 *RESENHA DOS CRIAS (Portugal):*\n" \
                             "• `/gajo` | `/soro` | `/pinar` | `/looteou` | `/squadpt`\n\n" \
                             "👑 *COMANDOS EXCLUSIVOS DE ADM:*\n" \
                             "• `/regras` | `/guerraguilda` | `/xtreino [hora-hora]`"
                enviar_mensagem(chat_id, menu_ajuda)
            # ==================================================================
            # NOVO COMANDO: GERADOR DE SENSIBILIDADE ALEATÓRIA (/sensirapida) - CORRIGIDO
            # ==================================================================
            elif texto_minusculo == "/sensirapida":
                geral = random.randint(90, 100)
                ponto_vermelho = random.randint(85, 100)
                mira_2x = random.randint(90, 100)
                mira_4x = random.randint(88, 100)
                botao = random.randint(40, 55)
                dpi = random.choice(["410", "480", "520", "580", "600", "720"])
                
                txt_sensi_rapida = f"⚡ *SENSI RÁPIDA ALEATÓRIA* 🎯\n\n" \
                                   f"Aqui tens uma configuração gerada na hora para testares em qualquer telemóvel:\n\n" \
                                   f"• Geral: {geral}\n" \
                                   f"• Ponto Vermelho: {ponto_vermelho}\n" \
                                   f"• Mira 2x: {mira_2x}\n" \
                                   f"• Mira 4x: {mira_4x}\n" \
                                   f"• Botão de Atirar: {botao}%\n" \
                                   f"• DPI Recomendada: {dpi}\n\n" \
                                   f"💡 _Dica: Testa no modo treino. Se a mira passar da cabeça, reduz a Geral em 2 pontos!_"
                enviar_mensagem(chat_id, txt_sensi_rapida)

            # ==================================================================
            # COMANDOS: RESENHA PORTUGAL
            # ==================================================================
            elif texto_minusculo == "/gajo":
                acoes = [
                    "passou a partida toda escondido no gás a curar-se com fogueira para segurar pontos! 🐀",
                    "ficou a camperar em cima da fábrica e morreu para a primeira safe! 💀",
                    "comprou duas Vector e descarregou o pente todo no peito do inimigo. Que crime!",
                    "gastou 4 gelos de uma vez para se salvar de um gajo que estava de pistola de plasma. 🤡"
                ]
                txt_gajo = f"🤖 *EXPOSTO:* Esse gajo que acabou de mandar mensagem {random.choice(acoes)}"
                enviar_mensagem(chat_id, txt_gajo)

            elif texto_minusculo == "/soro":
                hps = [
                    "🩸 *ESTÁS A SORO!* Levaste 3 capas seguidos de Carapina, o teu colete está partido e só tens 1 de HP. Mete gelo rápido! 🧊",
                    "🛡️ *VIDA CHEIA:* O teu colete está blindado a nível 4, tens o Alok ativo e estás pronto para o rush!",
                    "🩹 *A CURAR:* Estás sem mulas de gelo mas encontraste 4 kits médicos na guarita. Salvaste-te por pouco!"
                ]
                enviar_mensagem(chat_id, random.choice(hps))

            elif texto_minusculo == "/pinar":
                taxa = random.randint(10, 100)
                if taxa > 80:
                    msg = f"❌ *TAXA DE PINO: {taxa}%!* Hoje não dás um capa nem que o gajo esteja parado na tua frente. Desliga o telemóvel e vai dormir! 🛌"
                else:
                    msg = f"🎯 *TAXA DE PINO: {taxa}%!* A tua mira está colada na cabeça. É só vermelho nos treinos de hoje! 🔥"
                enviar_mensagem(chat_id, msg)

            elif texto_minusculo == "/looteou":
                drops = [
                    "📦 Encontraste uma Groza lendária, colete 4 e 5 mulas de gelo! Vais amassar a safe. 😎",
                    "📦 Abriste o drop e só lá tinha uma besta e uma Flashbang... Foste roubado pelos mitras. 😭",
                    "📦 O drop caiu em cima de ti e morreste esmagado antes de ver o loot. Grande nabo! 💀"
                ]
                enviar_mensagem(chat_id, f"🎯 **AIRDROP:** {random.choice(drops)}")

            elif texto_minusculo == "/squadpt":
                squad_msg = "🎮 *SQUAD DOS CRIAS MONTADO PELO BOT:* 🇵🇹\n\n" \
                            "💥 *O Rushador:* Aquele gajo que vai à frente abrir espaço.\n" \
                            "🎯 *O Suporte:* Fica atrás a dar cobertura de Sniper.\n" \
                            "🏃‍♂️ *O Full Gás:* Garante as rotações seguras.\n" \
                            "💀 *O Isqueiro:* Aquele gajo que morre sempre primeiro no lobby!\n\n" \
                            "📌 _Pede a um ADM para organizar o treino e dividir a equipa!_"
                enviar_mensagem(chat_id, squad_msg)

            # ==================================================================
            # SISTEMA DE POSIÇÕES DA GUILDA
            # ==================================================================
            elif texto_minusculo == "/posicoes":
                menu_posicoes = "⚔️ *POSIÇÕES OFICIAIS DA GUILDA* 🛡️\n\n" \
                                "💥 1️⃣ *Rush* – O gajo que avança primeiro e abre espaço.\n" \
                                "🎯 2️⃣ *Suporte* – Fica atrás a dar cobertura com Snipers.\n" \
                                "🏃‍♂️ 3️⃣ *Full Gas* – O mestre da rotação que garante o mapa.\n" \
                                "🩹 4️⃣ *Curandeiro* – Focado em reviver e gerir os kits.\n\n" \
                                "📌 *Como escolher a tua:* Digita `/escolherposicao [Nome]`"
                enviar_mensagem(chat_id, menu_posicoes)

            elif texto_minusculo.startswith("/escolherposicao "):
                escolha = texto_minusculo[17:].strip()
                if escolha in ["rush", "suporte", "full gas", "curandeiro"]:
                    POSICOES_JOGADORES[sender_id] = escolha.upper()
                    enviar_mensagem(chat_id, f"✅ *FUNÇÃO ATUALIZADA!* A tua posição oficial é: *{escolha.upper()}*! 🔥")
                else:
                    enviar_mensagem(chat_id, "⚠️ *Posição inválida!* Escolha: `rush`, `suporte`, `full gas` ou `curandeiro`")

            elif texto_minusculo == "/minhaposicao":
                if sender_id in POSICOES_JOGADORES:
                    enviar_mensagem(chat_id, f"🔰 *TUA FICHA:* Atualmente estás registado como: *{POSICOES_JOGADORES[sender_id]}* ⚔️")
                else:
                    enviar_mensagem(chat_id, "⚠️ Ainda não tens nenhuma função. Digita `/posicoes` para escolheres uma!")

            # ==================================================================
            # COMANDOS DE SENSI MANTIDOS
            # ==================================================================
            elif texto_minusculo == "/sensi":
                lista_telemoveis = "📱 *TELEMÓVEIS DISPONÍVEIS NO BOT* 🎯\n\n" \
                                   "🍏 *iPhones:* `/iphone 11` | `/iphone 12` | `/iphone 13` | `/iphone xr`\n" \
                                   "🔥 *Xiaomi/Poco:* `/poco x3` | `/poco f5` | `/redmi note 10` | `/redmi note 11` | `/redmi note 13` | `/redmi 12` | `/redmi 13c`\n" \
                                   "⚡ *Novos:* `/realme note 60` | `/honor 400 lite`\n" \
                                   "🔷 *Outros:* `/samsung a32` | `/samsung a54` | `/moto g60` | `/moto g200`\n\n" \
                                   "⚠️ *Se o seu telemóvel não aparecer diga o seu que nós adicionamos!*"
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
                            aviso_xtreino = f"📢 *AVISO DE XTREINO DA GUILDA!* 📢\n\n⚔️ *Início:* {h1.strip()}\n🏆 *Fim:* {h2.strip()}\n\nSejam pontuais, preparem os squads! 🎮"
                            enviar_mensagem(chat_id, aviso_xtreino)
                        except Exception:
                            enviar_mensagem(chat_id, "⚠️ *Erro!* Usa: `/xtreino 19:00-20:00`")
                    else:
                        enviar_mensagem(chat_id, "⚠️ *Erro!* Use hífen. Exemplo: `/xtreino 20:00-21:00`")

                elif texto_minusculo == "/regras":
                    regras_texto = "📜 *REGRAS OFICIAIS DA GUILDA* 📜\n\n1️⃣ Lealdade total.\n2️⃣ Sem toxicidade.\n3️⃣ 7.500 Pontos de Honra.\n4️⃣ 50 Pontos na Guerra."
                    enviar_mensagem(chat_id, regras_texto)

                elif texto_minusculo == "/guerraguilda":
                    guerra_texto = "⚔️ *GUERRA DE GUILDA (FF)* ⚔️\n\n📅 Dias: Quarta, Sexta e Sábado\n⏰ Horário: Das 18:00 às 22:00"
                    enviar_mensagem(chat_id, guerra_texto)
    return jsonify({"status": "sucesso"}), 200

if __name__ == "__main__":
    app.run(port=5000)

