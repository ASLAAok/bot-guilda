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
                             "• `/[telemóvel]` – Vê a sensi exata (Ex: `/redmi note 13`).\n" \
                             "• `/sensirapida` – Gera uma sensi coringa aleatória.\n" \
                             "• `/posicoes` | `/escolherposicao` | `/minhaposicao`\n\n" \
                             "🔥 *RESENHA DOS CRIAS (Portugal):*\n" \
                             "• `/gajo` | `/soro` | `/pinar` | `/looteou` | `/squadpt`\n\n" \
                             "👑 *COMANDOS EXCLUSIVOS DE ADM:*\n" \
                             "• `/advertencia [número] [motivo]` – Aplica uma advertência.\n" \
                             "• `/regras` | `/guerraguilda` | `/xtreino [hora-hora]`"
                enviar_mensagem(chat_id, menu_ajuda)
            # ==================================================================
            # NOVO SISTEMA SÉRIO: SISTEMA DE ADVERTÊNCIAS (MÁXIMO 4)
            # ==================================================================
            if texto_minusculo.startswith("/advertencia"):
                # Apenas administradores listados podem aplicar ou consultar advertências
                if sender_id in ADMINISTRADORES_PERMITIDOS:
                    try:
                        partes = texto_original.split(maxsplit=2)
                        
                        # Se o ADM digitou apenas /advertencia [Número] -> Consulta a ficha
                        if len(partes) == 2:
                            num_alvo = partes[1].replace("+", "").replace(" ", "")
                            id_alvo = num_alvo if num_alvo.endswith("@c.us") else num_alvo + "@c.us"
                            
                            qtd = ADVERTENCIAS_JOGADORES.get(id_alvo, 0)
                            enviar_mensagem(chat_id, f"📋 *FICHA DISCIPLINAR:* O jogador @{num_alvo} possui atualmente *{qtd}/4* advertências registadas.")
                        
                        # Se o ADM digitou /advertencia [Número] [Motivo] -> Aplica +1 advertência
                        elif len(partes) >= 3:
                            num_alvo = partes[1].replace("+", "").replace(" ", "")
                            motivo = partes[2].strip()
                            id_alvo = num_alvo if num_alvo.endswith("@c.us") else num_alvo + "@c.us"
                            
                            # Soma +1 advertência na ficha do meliante
                            ADVERTENCIAS_JOGADORES[id_alvo] = ADVERTENCIAS_JOGADORES.get(id_alvo, 0) + 1
                            nova_qtd = ADVERTENCIAS_JOGADORES[id_alvo]
                            
                            if nova_qtd >= 4:
                                # PUNIÇÃO MÁXIMA ALCANÇADA
                                ADVERTENCIAS_JOGADORES[id_alvo] = 4 # Trava no limite máximo
                                alerta_vermelho = f"🚨 *PUNIÇÃO MÁXIMA ATINGIDA!* 🚨\n\n" \
                                                  f"O jogador @{num_alvo} acabou de receber a sua *4ª advertência*.\n" \
                                                  f"• *Motivo final:* {motivo}\n\n" \
                                                  f"❌ *SISTEMA:* Limite máximo de 4/4 atingido. Os Administradores devem **REMOVER IMEDIATAMENTE** este jogador da guilda por comportamento inadequado!"
                                enviar_mensagem(chat_id, alerta_vermelho)
                            else:
                                # ADVERTÊNCIA PARCIAL
                                msg_adv = f"⚠️ *ADVERTÊNCIA APLICADA!* ⚠️\n\n" \
                                          f"O jogador @{num_alvo} foi advertido oficialmente pela liderança.\n" \
                                          f"• *Motivo:* {motivo}\n" \
                                          f"• *Ficha Atual:* *{nova_qtd}/4* advertências.\n\n" \
                                          f"📌 _Lembrete: Ao atingir a 4ª advertência, a remoção da guilda será automática!_"
                                enviar_mensagem(chat_id, msg_adv)
                    except Exception:
                        enviar_mensagem(chat_id, "⚠️ *Erro no formato!* Use:\n• Para aplicar: `/advertencia [Número] [Motivo]`\n• Para consultar: `/advertencia [Número]`")
                else:
                    # Se um membro comum tentar usar o comando, o bot ignora ou dá bronca
                    print(f"Mensagem bloqueada: Usuário comum tentou dar advertência.")

            # ==================================================================
            # COMANDOS DE INTERAÇÃO E RESENHA MANTIDOS
            # ==================================================================
            elif texto_minusculo == "/sensirapida":
                geral, red, m2x, m4x, bot = random.randint(90, 100), random.randint(85, 100), random.randint(90, 100), random.randint(88, 100), random.randint(40, 55)
                dpi = random.choice(["410", "480", "520", "580", "600", "720"])
                enviar_mensagem(chat_id, f"⚡ *SENSI RÁPIDA ALEATÓRIA* 🎯\n\n• Geral: {geral}\n• Ponto Vermelho: {red}\n• Mira 2x: {m2x}\n• Mira 4x: {m4x}\n• Botão: {bot}%\n• DPI: {dpi}")

            elif texto_minusculo == "/gajo":
                acoes = ["passou a partida toda escondido no gás! 🐀", "ficou a camperar na fábrica e morreu! 💀", "comprou duas Vector. Que crime!", "gastou 4 gelos de uma vez de bobeira. 🤡"]
                enviar_mensagem(chat_id, f"🤖 *EXPOSTO:* Esse gajo que acabou de mandar mensagem {random.choice(acoes)}")

            elif texto_minusculo == "/soro":
                hps = ["🩸 *ESTÁS A SORO!* Levaste 3 capas seguidos de Carapina. 1 HP! 🧊", "🛡️ *VIDA CHEIA:* Colete blindado nível 4 ativo e pronto pro rush!", "🩹 *A CURAR:* Encontraste 4 kits médicos na guarita. Salvaste-te!"]
                enviar_mensagem(chat_id, random.choice(hps))

            elif texto_minusculo == "/pinar":
                taxa = random.randint(10, 100)
                msg = f"❌ *TAXA DE PINO: {taxa}%!* Vai dormir! 🛌" if taxa > 80 else f"🎯 *TAXA DE PINO: {taxa}%!* É só vermelho hoje! 🔥"
                enviar_mensagem(chat_id, msg)

            elif texto_minusculo == "/looteou":
                drops = ["📦 Groza lendária, colete 4 e 5 mulas de gelo! 😎", "📦 Só tinha uma besta e uma Flashbang... 😭", "📦 O drop caiu em cima de ti e morreste esmagado. 💀"]
                enviar_mensagem(chat_id, f"🎯 **AIRDROP:** {random.choice(drops)}")

            elif texto_minusculo == "/squadpt":
                enviar_mensagem(chat_id, "🎮 *SQUAD MONTADO:* 🇵🇹\n\n💥 *O Rushador:* Vai à frente.\n🎯 *O Suporte:* Dá cobertura.\n🏃‍♂️ *O Full Gás:* Garante rotações.\n💀 *O Isqueiro:* Morre sempre primeiro!")

            # SISTEMA DE POSIÇÕES E SENSI MANTIDOS
            elif texto_minusculo == "/posicoes":
                enviar_mensagem(chat_id, "⚔️ *POSIÇÕES OFICIAIS DA GUILDA* 🛡️\n\n💥 1️⃣ *Rush* | 🎯 2️⃣ *Suporte* | 🏃‍♂️ 3️⃣ *Full Gas* | 🩹 4️⃣ *Curandeiro*\n\n📌 *Como escolher:* `/escolherposicao [Nome]`")

            elif texto_minusculo.startswith("/escolherposicao "):
                escolha = texto_minusculo[17:].strip()
                if escolha in ["rush", "suporte", "full gas", "curandeiro"]:
                    POSICOES_JOGADORES[sender_id] = escolha.upper()
                    enviar_mensagem(chat_id, f"✅ *FUNÇÃO ATUALIZADA!* A tua posição oficial é: *{escolha.upper()}*! 🔥")

            elif texto_minusculo == "/minhaposicao":
                msg = f"🔰 *TUA FICHA:* Atualmente estás registado como: *{POSICOES_JOGADORES[sender_id]}* ⚔️" if sender_id in POSICOES_JOGADORES else "⚠️ Sem função registada. Digita `/posicoes`!"

            elif texto_minusculo == "/sensi":
                enviar_mensagem(chat_id, "📱 *TELEMÓVEIS DISPONÍVEIS NO BOT* 🎯\n\n🍏 *iPhones:* `/iphone 11` | `/iphone 12` | `/iphone 13` | `/iphone xr`\n🔥 *Xiaomi/Poco:* `/poco x3` | `/poco f5` | `/redmi note 10` | `/redmi note 11` | `/redmi note 13` | `/redmi 12` | `/redmi 13c`\n⚡ *Novos:* `/realme note 60` | `/honor 400 lite`\n🔷 *Outros:* `/samsung a32` | `/samsung a54` | `/moto g60` | `/moto g200`")
            
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
