import os
import json
from datetime import datetime
import discord
from discord.ext import commands
from dotenv import load_dotenv

# =========================
# CONFIG
# =========================

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

GUILD_ID = 1442149654971027488
LOG_CHANNEL_ID = 1442149655361093745
RECRUTAMENTO_CHANNEL_ID = 1491457861732274248
INDICACAO_CHANNEL_ID = 1498645764836954182

CARGO_ADV_ID = 1442149654971027490
CARGO_MEMBROS_ID = 1442149655340388458

CARGOS_PERMISSAO_IDS = [
    1497247550304948344,
    1491094392704995490,
    1442149655340388459,
    1442149655340388462,
    1442149655340388460,
    1496913805366657215,
    1442149655340388461,
    1496914534999523588,
    1442149655361093743,
    1497260871469109248,
    1442149655361093745
]

NOME_FACCAO = "Croácia"
TAG_MEMBRO = "Mᴇᴍʙʀᴏ •"
RADIO_FAC = "173"
LOCAL_AREA_RISCO = "Número 4"
COR_PADRAO = discord.Color.dark_red()

FUNCAO_CHEFE_PADRAO = "Líder geral da facção, toma decisões e comanda operações."

CHEFES = {
    "00": {"nome": "Connor", "funcao": FUNCAO_CHEFE_PADRAO},
    "01": {"nome": "Lincon", "funcao": FUNCAO_CHEFE_PADRAO},
    "02": {"nome": "Mudo", "funcao": FUNCAO_CHEFE_PADRAO}
}

REGRAS = [
    "Respeitar todos os membros da facção.",
    "Sem ordem da liderança, não iniciar ações.",
    "Sempre usar a rádio 173 durante ações e movimentações importantes.",
    "Não abandonar companheiro em ação.",
    "Farmar e contribuir com a organização.",
    "Não vazar informações internas da Croácia.",
    "Problemas internos devem ser tratados com a liderança.",
    "Quebra de disciplina pode gerar advertência ou remoção."
]

ROTAS = {
    "sequencial": "Rotas sequenciais: siga a ordem definida pela facção.",
    "aleatoria": "Rotas aleatórias: escolha livre conforme a situação do RP."
}

# =========================
# DADOS SALVOS
# =========================

ARQUIVO = "dados.json"

if os.path.exists(ARQUIVO):
    with open(ARQUIVO, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {}

data.setdefault("saldos", {})
data.setdefault("farms", {})
data.setdefault("registros", {})
data.setdefault("advertencias", {})
data.setdefault("blacklist", [])
data.setdefault("caixa", 0)
data.setdefault("recrutamentos", {})
data.setdefault("indicacoes", {})
data.setdefault("metas_farm", {"five": 500, "ak47": 500, "outros": 500})
data.setdefault("farms_semanais", {})
data.setdefault("historico_farms", [])


def salvar():
    with open(ARQUIVO, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# =========================
# BOT
# =========================

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)


# =========================
# FUNÇÕES
# =========================

def tem_permissao(member: discord.Member) -> bool:
    return member.guild_permissions.administrator or any(role.id in CARGOS_PERMISSAO_IDS for role in member.roles)


def embed_base(titulo: str, descricao: str = None, cor=COR_PADRAO):
    embed = discord.Embed(title=titulo, description=descricao, color=cor)
    embed.set_footer(text=f"{NOME_FACCAO} RP • Sistema Oficial")
    return embed


async def enviar_log(guild: discord.Guild, titulo: str, descricao: str, cor=discord.Color.dark_gold()):
    canal = guild.get_channel(LOG_CHANNEL_ID)
    if canal:
        embed = embed_base(titulo, descricao, cor)
        await canal.send(embed=embed)


def montar_apelido_membro(nome: str) -> str:
    nome_limpo = nome.strip()
    apelido = f"{TAG_MEMBRO} {nome_limpo}"

    # Limite do Discord para apelidos.
    if len(apelido) > 32:
        apelido = apelido[:32]

    return apelido


async def aplicar_apelido_membro(membro: discord.Member, nome: str, motivo: str):
    novo_apelido = montar_apelido_membro(nome)

    try:
        await membro.edit(nick=novo_apelido, reason=motivo)
        return True, novo_apelido, None
    except discord.Forbidden:
        return False, novo_apelido, "Sem permissão para alterar apelido. O cargo do bot precisa estar acima do membro e ele precisa da permissão Gerenciar Apelidos."
    except discord.HTTPException:
        return False, novo_apelido, "Erro do Discord ao alterar apelido."


# =========================
# EVENTO
# =========================

@bot.event
async def on_ready():
    guild = discord.Object(id=GUILD_ID)
    try:
        bot.tree.copy_global_to(guild=guild)
        synced = await bot.tree.sync(guild=guild)
        print(f"🇭🇷 {NOME_FACCAO} online como {bot.user}")
        print(f"Comandos sincronizados: {len(synced)}")
    except Exception as e:
        print(f"Erro ao sincronizar comandos: {e}")



@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    print(f"ERRO EM COMANDO SLASH: {repr(error)}")

    mensagem = "❌ Deu erro nesse comando. Veja o terminal do bot para detalhes."

    try:
        if interaction.response.is_done():
            await interaction.followup.send(mensagem, ephemeral=True)
        else:
            await interaction.response.send_message(mensagem, ephemeral=True)
    except Exception:
        pass


# =========================
# INFORMAÇÕES DA FACÇÃO
# =========================

@bot.tree.command(name="regras", description="Mostra as regras da facção")
async def regras(interaction: discord.Interaction):
    embed = embed_base(
        f"📜 Regras da {NOME_FACCAO}",
        "Leia com atenção. Disciplina mantém a família de pé."
    )
    for i, regra in enumerate(REGRAS, start=1):
        embed.add_field(name=f"Regra {i}", value=regra, inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="radio", description="Mostra a rádio oficial da facção")
async def radio(interaction: discord.Interaction):
    embed = embed_base(
        f"📻 Rádio da {NOME_FACCAO}",
        f"A rádio oficial da facção é **{RADIO_FAC}**.",
        discord.Color.red()
    )
    embed.add_field(name="Uso obrigatório", value="Entre na rádio antes de ações, farms e movimentações importantes.", inline=False)
    embed.add_field(name="Aviso", value="Sem rádio, sem operação.", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="local", description="Mostra locais importantes da facção")
async def local(interaction: discord.Interaction):
    embed = embed_base(
        f"📍 Local da {NOME_FACCAO}",
        "Locais importantes para organização e operações.",
        discord.Color.dark_gold()
    )
    embed.add_field(name="Área de risco", value=f"**{LOCAL_AREA_RISCO}**", inline=False)
    embed.add_field(name="Orientação", value="Não vá sozinho. Confirme com a liderança antes.", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="chefes", description="Mostra os chefes da facção")
async def chefes(interaction: discord.Interaction):
    embed = embed_base(f"👑 Chefes da {NOME_FACCAO}", "Hierarquia principal da facção.", discord.Color.gold())
    for codigo, dados in CHEFES.items():
        embed.add_field(
            name=f"Chefe {codigo} - {dados['nome']}",
            value=dados["funcao"],
            inline=False
        )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="rotas", description="Mostra os tipos de rotas")
async def rotas(interaction: discord.Interaction):
    embed = embed_base(
        f"📦 Rotas da {NOME_FACCAO}",
        "Use `/farm membro munição quantidade` para registrar munições vendidas.",
        discord.Color.dark_red()
    )
    for tipo, descricao in ROTAS.items():
        embed.add_field(name=tipo.capitalize(), value=descricao, inline=False)
    await interaction.response.send_message(embed=embed)


# =========================
# ALERTA
# =========================

@bot.tree.command(name="alerta", description="Envia alerta de emergência personalizado")
async def alerta(interaction: discord.Interaction, tipo: str, mensagem: str):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    tipo_limpo = tipo.lower()

    if tipo_limpo == "invasao":
        titulo = "🚨 ALERTA DE INVASÃO"
        cor = discord.Color.red()
    elif tipo_limpo == "operacao":
        titulo = "⚔️ ALERTA DE OPERAÇÃO"
        cor = discord.Color.orange()
    elif tipo_limpo == "reuniao":
        titulo = "📢 ALERTA DE REUNIÃO"
        cor = discord.Color.gold()
    elif tipo_limpo == "urgente":
        titulo = "🔥 ALERTA URGENTE"
        cor = discord.Color.dark_red()
    elif tipo_limpo == "farm":
        titulo = "📦 ALERTA DE FARM"
        cor = discord.Color.green()
    else:
        titulo = f"🚨 ALERTA - {tipo.upper()}"
        cor = discord.Color.dark_red()

    embed = embed_base(titulo, mensagem, cor)
    embed.add_field(name="Tipo", value=tipo, inline=True)
    embed.add_field(name="Enviado por", value=interaction.user.mention, inline=True)
    embed.add_field(name="Ação", value="A liderança solicita atenção imediata.", inline=False)

    await interaction.channel.send(embed=embed)
    await enviar_log(
        interaction.guild,
        "🚨 Alerta enviado",
        f"**Tipo:** {tipo}\n**Por:** {interaction.user.mention}\n**Canal:** {interaction.channel.mention}\n**Mensagem:** {mensagem}",
        cor
    )
    await interaction.response.send_message("✅ Alerta enviado.", ephemeral=True)


# =========================
# FARM SEMANAL / METAS / DINHEIRO / CAIXA
# =========================

TIPOS_MUNICAO = {
    "five": "FIVE",
    "5": "FIVE",
    "five-seven": "FIVE",
    "fiveseven": "FIVE",
    "ak47": "AK-47",
    "ak-47": "AK-47",
    "ak": "AK-47",
    "outros": "OUTROS",
    "outro": "OUTROS",
    "outras": "OUTROS"
}

METAS_PADRAO = {
    "five": 500,
    "ak47": 500,
    "outros": 500
}


def semana_atual() -> str:
    agora = datetime.now()
    ano, semana, _ = agora.isocalendar()
    return f"{ano}-S{semana:02d}"


def nome_semana(semana: str | None = None) -> str:
    return semana or semana_atual()


def normalizar_municao(municao: str):
    chave = municao.lower().strip().replace("_", "-").replace(" ", "")

    if chave in ["ak47", "ak-47", "ak"]:
        return "ak47", "AK-47"
    if chave in ["five", "5", "five-seven", "fiveseven"]:
        return "five", "FIVE"
    if chave in ["outros", "outro", "outras"]:
        return "outros", "OUTROS"

    return None, None


def garantir_estrutura_farm():
    data.setdefault("metas_farm", METAS_PADRAO.copy())
    data.setdefault("farms_semanais", {})
    data.setdefault("historico_farms", [])

    for chave, valor in METAS_PADRAO.items():
        data["metas_farm"].setdefault(chave, valor)


def garantir_farm_usuario(uid: str, semana: str | None = None):
    garantir_estrutura_farm()
    semana = nome_semana(semana)
    data["farms_semanais"].setdefault(semana, {})
    data["farms_semanais"][semana].setdefault(uid, {"five": 0, "ak47": 0, "outros": 0})

    for chave in METAS_PADRAO:
        data["farms_semanais"][semana][uid].setdefault(chave, 0)

    return data["farms_semanais"][semana][uid]


def total_farm_usuario(uid: str, semana: str | None = None) -> int:
    farm = garantir_farm_usuario(uid, semana)
    return farm.get("five", 0) + farm.get("ak47", 0) + farm.get("outros", 0)


def status_meta(valor: int, meta: int) -> str:
    if valor >= meta:
        return "✅ Batida"
    falta = meta - valor
    return f"❌ Falta {falta}"


def progresso_meta_texto(farm: dict) -> str:
    metas = data.get("metas_farm", METAS_PADRAO)
    linhas = []
    nomes = {"five": "FIVE", "ak47": "AK-47", "outros": "OUTROS"}

    for chave in ["five", "ak47", "outros"]:
        valor = farm.get(chave, 0)
        meta = metas.get(chave, METAS_PADRAO[chave])
        linhas.append(f"**{nomes[chave]}:** {valor}/{meta} • {status_meta(valor, meta)}")

    return "\n".join(linhas)


def bateu_todas_metas(farm: dict) -> bool:
    metas = data.get("metas_farm", METAS_PADRAO)
    return all(farm.get(chave, 0) >= metas.get(chave, METAS_PADRAO[chave]) for chave in METAS_PADRAO)


@bot.tree.command(name="farm", description="Registra farm semanal de munições para um membro")
async def farm(interaction: discord.Interaction, membro: discord.Member, municao: str, quantidade: int):
    await interaction.response.defer(ephemeral=True)

    try:
        if not tem_permissao(interaction.user):
            await interaction.followup.send("❌ Sem permissão.", ephemeral=True)
            return

        if quantidade <= 0:
            await interaction.followup.send("❌ Quantidade inválida.", ephemeral=True)
            return

        chave, nome = normalizar_municao(municao)
        if not chave:
            await interaction.followup.send(
                "❌ Munição inválida. Use: `five`, `ak47` ou `outros`.",
                ephemeral=True
            )
            return

        semana = semana_atual()
        uid = str(membro.id)
        farm_membro = garantir_farm_usuario(uid, semana)
        farm_membro[chave] += quantidade

        data["farms"][uid] = data["farms"].get(uid, 0) + quantidade
        data["historico_farms"].append({
            "semana": semana,
            "membro_id": membro.id,
            "membro": str(membro),
            "municao": chave,
            "quantidade": quantidade,
            "registrado_por_id": interaction.user.id,
            "registrado_por": str(interaction.user),
            "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
        salvar()

        await enviar_log(
            interaction.guild,
            "📦 Farm semanal registrado",
            f"**Membro:** {membro.mention}\n"
            f"**Munição:** {nome}\n"
            f"**Quantidade:** {quantidade}\n"
            f"**Semana:** {semana}\n"
            f"**Registrado por:** {interaction.user.mention}",
            discord.Color.green()
        )

        embed = embed_base("✅ Farm registrado", f"Farm lançado para {membro.mention}.", discord.Color.green())
        embed.add_field(name="Semana", value=semana, inline=True)
        embed.add_field(name="Munição", value=nome, inline=True)
        embed.add_field(name="Quantidade", value=str(quantidade), inline=True)
        embed.add_field(name="Progresso semanal", value=progresso_meta_texto(farm_membro), inline=False)
        embed.add_field(name="Situação geral", value="✅ Todas as metas batidas" if bateu_todas_metas(farm_membro) else "⚠️ Ainda falta bater meta", inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as erro:
        print(f"ERRO NO COMANDO /farm: {repr(erro)}")
        await interaction.followup.send(
            "❌ Deu erro ao registrar o farm. Veja o terminal do bot para detalhes.",
            ephemeral=True
        )

@bot.tree.command(name="meufarm", description="Mostra seu farm semanal de munições")
async def meufarm(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    try:
        uid = str(interaction.user.id)
        semana = semana_atual()
        farm_membro = garantir_farm_usuario(uid, semana)
        salvar()

        embed = embed_base("📦 Meu farm semanal", f"Semana atual: **{semana}**", discord.Color.gold())
        embed.add_field(name="Membro", value=interaction.user.mention, inline=False)
        embed.add_field(name="Progresso", value=progresso_meta_texto(farm_membro), inline=False)
        embed.add_field(name="Total entregue", value=str(total_farm_usuario(uid, semana)), inline=True)
        embed.add_field(name="Situação", value="✅ Todas as metas batidas" if bateu_todas_metas(farm_membro) else "⚠️ Meta pendente", inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as erro:
        print(f"ERRO NO COMANDO /meufarm: {repr(erro)}")
        await interaction.followup.send("❌ Deu erro ao consultar seu farm.", ephemeral=True)

@bot.tree.command(name="farmusuario", description="Mostra o farm semanal de um membro")
async def farmusuario(interaction: discord.Interaction, membro: discord.Member):
    await interaction.response.defer(ephemeral=True)

    try:
        if not tem_permissao(interaction.user):
            await interaction.followup.send("❌ Sem permissão.", ephemeral=True)
            return

        uid = str(membro.id)
        semana = semana_atual()
        farm_membro = garantir_farm_usuario(uid, semana)
        salvar()

        embed = embed_base("📦 Farm semanal do membro", f"Semana atual: **{semana}**", discord.Color.dark_red())
        embed.add_field(name="Membro", value=membro.mention, inline=False)
        embed.add_field(name="Progresso", value=progresso_meta_texto(farm_membro), inline=False)
        embed.add_field(name="Total entregue", value=str(total_farm_usuario(uid, semana)), inline=True)
        embed.add_field(name="Situação", value="✅ Todas as metas batidas" if bateu_todas_metas(farm_membro) else "⚠️ Meta pendente", inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as erro:
        print(f"ERRO NO COMANDO /farmusuario: {repr(erro)}")
        await interaction.followup.send("❌ Deu erro ao consultar o farm desse membro.", ephemeral=True)

@bot.tree.command(name="metasfarm", description="Mostra as metas semanais de farm")
async def metasfarm(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    try:
        garantir_estrutura_farm()
        metas = data["metas_farm"]

        embed = embed_base("🎯 Metas semanais de farm", "Metas mínimas por membro na semana.", discord.Color.gold())
        embed.add_field(name="FIVE", value=f"{metas.get('five', 500)} unidades", inline=True)
        embed.add_field(name="AK-47", value=f"{metas.get('ak47', 500)} unidades", inline=True)
        embed.add_field(name="OUTROS", value=f"{metas.get('outros', 500)} unidades", inline=True)
        embed.add_field(name="Semana atual", value=semana_atual(), inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as erro:
        print(f"ERRO NO COMANDO /metasfarm: {repr(erro)}")
        await interaction.followup.send("❌ Deu erro ao mostrar as metas.", ephemeral=True)

@bot.tree.command(name="setmeta", description="Altera a meta semanal de uma munição")
async def setmeta(interaction: discord.Interaction, municao: str, quantidade: int):
    await interaction.response.defer(ephemeral=True)

    try:
        if not tem_permissao(interaction.user):
            await interaction.followup.send("❌ Sem permissão.", ephemeral=True)
            return

        if quantidade < 0:
            await interaction.followup.send("❌ Quantidade inválida.", ephemeral=True)
            return

        chave, nome = normalizar_municao(municao)
        if not chave:
            await interaction.followup.send("❌ Munição inválida. Use: `five`, `ak47` ou `outros`.", ephemeral=True)
            return

        garantir_estrutura_farm()
        antiga = data["metas_farm"].get(chave, METAS_PADRAO[chave])
        data["metas_farm"][chave] = quantidade
        salvar()

        await enviar_log(
            interaction.guild,
            "🎯 Meta semanal alterada",
            f"**Munição:** {nome}\n**Meta antiga:** {antiga}\n**Nova meta:** {quantidade}\n**Por:** {interaction.user.mention}",
            discord.Color.gold()
        )

        embed = embed_base("✅ Meta atualizada", color=discord.Color.green())
        embed.add_field(name="Munição", value=nome, inline=True)
        embed.add_field(name="Meta antiga", value=str(antiga), inline=True)
        embed.add_field(name="Nova meta", value=str(quantidade), inline=True)
        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as erro:
        print(f"ERRO NO COMANDO /setmeta: {repr(erro)}")
        await interaction.followup.send("❌ Deu erro ao alterar a meta.", ephemeral=True)

@bot.tree.command(name="resetfarmsemana", description="Zera os farms da semana atual. Apenas autorizados")
async def resetfarmsemana(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    try:
        if not tem_permissao(interaction.user):
            await interaction.followup.send("❌ Sem permissão.", ephemeral=True)
            return

        garantir_estrutura_farm()
        semana = semana_atual()
        data["farms_semanais"][semana] = {}
        salvar()

        await enviar_log(
            interaction.guild,
            "♻️ Farm semanal resetado",
            f"**Semana:** {semana}\n**Por:** {interaction.user.mention}",
            discord.Color.orange()
        )

        embed = embed_base("♻️ Farm semanal resetado", f"Os farms da semana **{semana}** foram zerados.", discord.Color.orange())
        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as erro:
        print(f"ERRO NO COMANDO /resetfarmsemana: {repr(erro)}")
        await interaction.followup.send("❌ Deu erro ao resetar os farms da semana.", ephemeral=True)

@bot.tree.command(name="ranking", description="Mostra ranking semanal de farms por munições")
async def ranking(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    try:
        garantir_estrutura_farm()
        semana = semana_atual()
        farms_semana = data.get("farms_semanais", {}).get(semana, {})

        if not farms_semana:
            await interaction.followup.send("Ainda não há farms registrados nesta semana.", ephemeral=True)
            return

        top = sorted(farms_semana.items(), key=lambda item: sum(item[1].values()), reverse=True)[:10]
        texto = ""
        for pos, (uid, farm_membro) in enumerate(top, start=1):
            total = sum(farm_membro.values())
            texto += (
                f"**{pos}.** <@{uid}> - **{total}** unidades "
                f"• FIVE: {farm_membro.get('five', 0)} "
                f"• AK-47: {farm_membro.get('ak47', 0)} "
                f"• OUTROS: {farm_membro.get('outros', 0)}\n"
            )

        embed = embed_base("🏆 Ranking semanal de Farm", texto, discord.Color.gold())
        embed.add_field(name="Semana", value=semana, inline=False)
        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as erro:
        print(f"ERRO NO COMANDO /ranking: {repr(erro)}")
        await interaction.followup.send("❌ Deu erro ao mostrar o ranking.", ephemeral=True)

@bot.tree.command(name="pendentesfarm", description="Mostra membros registrados que ainda não bateram a meta semanal")
async def pendentesfarm(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)

    try:
        if not tem_permissao(interaction.user):
            await interaction.followup.send("❌ Sem permissão.", ephemeral=True)
            return

        garantir_estrutura_farm()
        semana = semana_atual()
        registros = data.get("registros", {})
        pendentes = []

        for uid, ficha in registros.items():
            farm_membro = garantir_farm_usuario(uid, semana)
            if not bateu_todas_metas(farm_membro):
                nome = ficha.get("nome", f"<@{uid}>")
                pendentes.append(f"<@{uid}> • **{nome}**\n{progresso_meta_texto(farm_membro)}")

        salvar()

        if not pendentes:
            await interaction.followup.send("✅ Todos os membros registrados bateram as metas da semana.", ephemeral=True)
            return

        texto = "\n\n".join(pendentes[:10])
        embed = embed_base("⚠️ Pendentes de farm semanal", texto, discord.Color.orange())
        embed.add_field(name="Semana", value=semana, inline=False)

        if len(pendentes) > 10:
            embed.add_field(name="Aviso", value=f"Mostrando 10 de {len(pendentes)} pendentes.", inline=False)

        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as erro:
        print(f"ERRO NO COMANDO /pendentesfarm: {repr(erro)}")
        await interaction.followup.send("❌ Deu erro ao listar pendentes.", ephemeral=True)

@bot.tree.command(name="saldo", description="Mostra seu saldo")
async def saldo(interaction: discord.Interaction):
    valor = data["saldos"].get(str(interaction.user.id), 0)
    embed = embed_base("💰 Saldo", f"{interaction.user.mention}, seu saldo é **R$ {valor}**.", discord.Color.green())
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="depositar", description="Deposita dinheiro no próprio saldo")
async def depositar(interaction: discord.Interaction, valor: int):
    if valor <= 0:
        await interaction.response.send_message("❌ Valor inválido.", ephemeral=True)
        return
    uid = str(interaction.user.id)
    data["saldos"][uid] = data["saldos"].get(uid, 0) + valor
    salvar()
    embed = embed_base("✅ Depósito realizado", color=discord.Color.green())
    embed.add_field(name="Valor", value=f"R$ {valor}", inline=True)
    embed.add_field(name="Saldo atual", value=f"R$ {data['saldos'][uid]}", inline=True)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="sacar", description="Saca dinheiro do próprio saldo")
async def sacar(interaction: discord.Interaction, valor: int):
    if valor <= 0:
        await interaction.response.send_message("❌ Valor inválido.", ephemeral=True)
        return
    uid = str(interaction.user.id)
    saldo_atual = data["saldos"].get(uid, 0)
    if valor > saldo_atual:
        await interaction.response.send_message("❌ Saldo insuficiente.", ephemeral=True)
        return
    data["saldos"][uid] = saldo_atual - valor
    salvar()
    embed = embed_base("💸 Saque realizado", color=discord.Color.dark_gold())
    embed.add_field(name="Valor", value=f"R$ {valor}", inline=True)
    embed.add_field(name="Saldo atual", value=f"R$ {data['saldos'][uid]}", inline=True)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="caixa", description="Mostra o caixa da facção")
async def caixa(interaction: discord.Interaction):
    embed = embed_base("🏦 Caixa da facção", f"Caixa atual da {NOME_FACCAO}: **R$ {data.get('caixa', 0)}**.", discord.Color.gold())
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="addcaixa", description="Adiciona dinheiro ao caixa. Apenas autorizados")
async def addcaixa(interaction: discord.Interaction, valor: int):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return
    if valor <= 0:
        await interaction.response.send_message("❌ Valor inválido.", ephemeral=True)
        return
    data["caixa"] = data.get("caixa", 0) + valor
    salvar()
    await enviar_log(interaction.guild, "🏦 Caixa atualizado", f"{interaction.user.mention} adicionou **R$ {valor}** ao caixa.")
    embed = embed_base("✅ Caixa atualizado", color=discord.Color.green())
    embed.add_field(name="Adicionado", value=f"R$ {valor}", inline=True)
    embed.add_field(name="Total", value=f"R$ {data['caixa']}", inline=True)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="removercaixa", description="Remove dinheiro do caixa. Apenas autorizados")
async def removercaixa(interaction: discord.Interaction, valor: int):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return
    if valor <= 0 or valor > data.get("caixa", 0):
        await interaction.response.send_message("❌ Valor inválido ou saldo insuficiente no caixa.", ephemeral=True)
        return
    data["caixa"] -= valor
    salvar()
    await enviar_log(interaction.guild, "🏦 Caixa atualizado", f"{interaction.user.mention} removeu **R$ {valor}** do caixa.")
    embed = embed_base("✅ Caixa atualizado", color=discord.Color.dark_gold())
    embed.add_field(name="Removido", value=f"R$ {valor}", inline=True)
    embed.add_field(name="Total", value=f"R$ {data['caixa']}", inline=True)
    await interaction.response.send_message(embed=embed)


# =========================
# REGISTRO / CARGOS / MEMBRO
# =========================

@bot.tree.command(name="registrar", description="Registra membro na facção")
async def registrar(interaction: discord.Interaction, membro: discord.Member, nome: str):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return
    if membro.id in data["blacklist"]:
        await interaction.response.send_message("❌ Esse membro está na blacklist.", ephemeral=True)
        return

    data["registros"][str(membro.id)] = {"nome": nome, "cargo": "Recruta"}
    salvar()
    await enviar_log(interaction.guild, "📥 Membro registrado", f"**Membro:** {membro.mention}\n**Nome:** {nome}\n**Por:** {interaction.user.mention}", discord.Color.green())
    embed = embed_base("✅ Membro registrado", color=discord.Color.green())
    embed.add_field(name="Membro", value=membro.mention, inline=True)
    embed.add_field(name="Nome", value=nome, inline=True)
    embed.add_field(name="Cargo inicial", value="Recruta", inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="cargo", description="Define o cargo interno do membro")
async def cargo(interaction: discord.Interaction, membro: discord.Member, cargo: str):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    uid = str(membro.id)
    if uid not in data["registros"]:
        await interaction.response.send_message("❌ Membro não registrado.", ephemeral=True)
        return

    antigo = data["registros"][uid].get("cargo", "Sem cargo")
    data["registros"][uid]["cargo"] = cargo
    salvar()
    await enviar_log(interaction.guild, "🎖️ Cargo interno alterado", f"**Membro:** {membro.mention}\n**De:** {antigo}\n**Para:** {cargo}\n**Por:** {interaction.user.mention}")
    embed = embed_base("🎖️ Cargo atualizado", color=discord.Color.gold())
    embed.add_field(name="Membro", value=membro.mention, inline=True)
    embed.add_field(name="Cargo anterior", value=antigo, inline=True)
    embed.add_field(name="Novo cargo", value=cargo, inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="membro", description="Mostra a ficha de um membro")
async def membro(interaction: discord.Interaction, membro: discord.Member):
    uid = str(membro.id)
    dados = data["registros"].get(uid)

    tem_cargo_membro = any(role.name.lower() in ["membro", "membros"] for role in membro.roles)

    if not dados and not tem_cargo_membro:
        await interaction.response.send_message(
            "❌ Esse usuário não está registrado e também não possui o cargo Membro/Membros.",
            ephemeral=True
        )
        return

    nome_ficha = dados["nome"] if dados else membro.display_name
    cargo_interno = dados["cargo"] if dados else "Membro"

    advs = data["advertencias"].get(uid, [])
    saldo_membro = data["saldos"].get(uid, 0)
    farms_membro = total_farm_usuario(uid, semana_atual())

    embed = embed_base(f"📄 Ficha de {nome_ficha}", color=discord.Color.dark_red())
    embed.add_field(name="Discord", value=membro.mention, inline=False)
    embed.add_field(name="Status", value="Registrado" if dados else "Cargo Membro detectado", inline=False)
    embed.add_field(name="Cargo interno", value=cargo_interno, inline=True)
    embed.add_field(name="Saldo", value=f"R$ {saldo_membro}", inline=True)
    embed.add_field(name="Farm semanal", value=f"{farms_membro} munições", inline=True)
    embed.add_field(name="Advertências", value=str(len(advs)), inline=True)

    if advs:
        embed.add_field(name="Última advertência", value=advs[-1], inline=False)

    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="remover", description="Remove membro do sistema da facção")
async def remover(interaction: discord.Interaction, membro: discord.Member):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    uid = str(membro.id)
    data["registros"].pop(uid, None)
    data["advertencias"].pop(uid, None)
    data["saldos"].pop(uid, None)
    data["farms"].pop(uid, None)
    for semana in data.get("farms_semanais", {}).values():
        semana.pop(uid, None)
    salvar()
    await enviar_log(interaction.guild, "❌ Membro removido", f"**Membro:** {membro.mention}\n**Por:** {interaction.user.mention}", discord.Color.red())
    embed = embed_base("❌ Membro removido", f"{membro.mention} foi removido do sistema da facção.", discord.Color.red())
    await interaction.response.send_message(embed=embed)


# =========================
# ADVERTÊNCIA / BLACKLIST
# =========================

@bot.tree.command(name="adv", description="Aplica advertência e dá cargo ADV")
async def adv(interaction: discord.Interaction, membro: discord.Member, motivo: str):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    cargo_adv = interaction.guild.get_role(CARGO_ADV_ID)
    if not cargo_adv:
        await interaction.response.send_message("❌ Cargo ADV não encontrado. Confira o ID.", ephemeral=True)
        return

    uid = str(membro.id)
    lista = data["advertencias"].get(uid, [])
    lista.append(motivo)
    data["advertencias"][uid] = lista
    salvar()

    try:
        await membro.add_roles(cargo_adv, reason=f"Advertência aplicada por {interaction.user}")
    except discord.Forbidden:
        await interaction.response.send_message("❌ Não tenho permissão para dar esse cargo. Meu cargo precisa estar acima do ADV.", ephemeral=True)
        return

    await enviar_log(interaction.guild, "⚠️ Advertência aplicada", f"**Membro:** {membro.mention}\n**Motivo:** {motivo}\n**Por:** {interaction.user.mention}", discord.Color.orange())

    embed = embed_base("⚠️ Advertência aplicada", color=discord.Color.orange())
    embed.add_field(name="Membro", value=membro.mention, inline=False)
    embed.add_field(name="Motivo", value=motivo, inline=False)
    embed.add_field(name="Total de advertências", value=str(len(lista)), inline=True)
    embed.add_field(name="Cargo aplicado", value=cargo_adv.mention, inline=True)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="limparadv", description="Limpa advertências e remove cargo ADV")
async def limparadv(interaction: discord.Interaction, membro: discord.Member):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    uid = str(membro.id)
    data["advertencias"].pop(uid, None)
    salvar()

    cargo_adv = interaction.guild.get_role(CARGO_ADV_ID)
    if cargo_adv and cargo_adv in membro.roles:
        try:
            await membro.remove_roles(cargo_adv, reason=f"Advertências limpas por {interaction.user}")
        except discord.Forbidden:
            await interaction.response.send_message("❌ Limpei os dados, mas não tenho permissão para remover o cargo ADV.", ephemeral=True)
            return

    await enviar_log(interaction.guild, "✅ Advertências limpas", f"**Membro:** {membro.mention}\n**Por:** {interaction.user.mention}", discord.Color.green())
    embed = embed_base("✅ Advertências limpas", f"Advertências de {membro.mention} foram removidas.", discord.Color.green())
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="blacklist", description="Coloca membro na blacklist")
async def blacklist(interaction: discord.Interaction, membro: discord.Member, motivo: str):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    if membro.id not in data["blacklist"]:
        data["blacklist"].append(membro.id)
    salvar()
    await enviar_log(interaction.guild, "🚫 Blacklist aplicada", f"**Membro:** {membro.mention}\n**Motivo:** {motivo}\n**Por:** {interaction.user.mention}", discord.Color.red())
    embed = embed_base("🚫 Blacklist aplicada", color=discord.Color.red())
    embed.add_field(name="Membro", value=membro.mention, inline=True)
    embed.add_field(name="Motivo", value=motivo, inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="unblacklist", description="Remove membro da blacklist")
async def unblacklist(interaction: discord.Interaction, membro: discord.Member):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    if membro.id in data["blacklist"]:
        data["blacklist"].remove(membro.id)
        salvar()
    await enviar_log(interaction.guild, "✅ Blacklist removida", f"**Membro:** {membro.mention}\n**Por:** {interaction.user.mention}", discord.Color.green())
    embed = embed_base("✅ Blacklist removida", f"{membro.mention} foi removido da blacklist.", discord.Color.green())
    await interaction.response.send_message(embed=embed)


# =========================
# MENSAGEM / EMBED
# =========================

@bot.tree.command(name="msgtdc", description="Faz o bot enviar uma mensagem normal")
async def msgtdc(interaction: discord.Interaction, mensagem: str):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    await interaction.channel.send(mensagem)
    await enviar_log(interaction.guild, "📨 Mensagem enviada pelo bot", f"**Por:** {interaction.user.mention}\n**Canal:** {interaction.channel.mention}\n**Mensagem:** {mensagem}")
    await interaction.response.send_message("✅ Mensagem enviada.", ephemeral=True)


@bot.tree.command(name="embed", description="Envia um embed personalizado")
async def embed_cmd(interaction: discord.Interaction, titulo: str, mensagem: str):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    embed = embed_base(titulo, mensagem, discord.Color.dark_red())
    embed.set_footer(text=f"{NOME_FACCAO} • Enviado por {interaction.user}")
    await interaction.response.send_message(embed=embed)
    await enviar_log(interaction.guild, "🧾 Embed enviado", f"**Por:** {interaction.user.mention}\n**Título:** {titulo}")


@bot.tree.command(name="embed2", description="Envia embed avançado com imagem, thumbnail, cor e rodapé")
async def embed2(
    interaction: discord.Interaction,
    titulo: str,
    descricao: str,
    cor_hex: str = "8B0000",
    imagem_url: str = None,
    thumbnail_url: str = None,
    rodape: str = None,
    canal: discord.TextChannel = None
):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    cor_hex = cor_hex.replace("#", "")

    try:
        cor = discord.Color(int(cor_hex, 16))
    except ValueError:
        await interaction.response.send_message("❌ Cor inválida. Use HEX, exemplo: `8B0000` ou `#8B0000`.", ephemeral=True)
        return

    embed = discord.Embed(title=titulo, description=descricao, color=cor)

    if imagem_url:
        embed.set_image(url=imagem_url)

    if thumbnail_url:
        embed.set_thumbnail(url=thumbnail_url)

    embed.set_footer(text=rodape or f"{NOME_FACCAO} • Enviado por {interaction.user}")

    canal_destino = canal or interaction.channel
    await canal_destino.send(embed=embed)

    await enviar_log(
        interaction.guild,
        "🧾 Embed avançado enviado",
        f"**Por:** {interaction.user.mention}\n**Canal:** {canal_destino.mention}\n**Título:** {titulo}",
        discord.Color.dark_gold()
    )
    await interaction.response.send_message("✅ Embed avançado enviado.", ephemeral=True)


@bot.tree.command(name="anunciar", description="Envia aviso oficial da liderança")
async def anunciar(interaction: discord.Interaction, mensagem: str):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    embed = embed_base(f"📢 Aviso Oficial da {NOME_FACCAO}", mensagem, discord.Color.gold())
    await interaction.response.send_message(embed=embed)
    await enviar_log(interaction.guild, "📢 Anúncio enviado", f"**Por:** {interaction.user.mention}\n**Mensagem:** {mensagem}", discord.Color.gold())


# =========================
# RECRUTAMENTO
# =========================

class RecrutamentoModal(discord.ui.Modal, title="Recrutamento Croácia"):
    nome = discord.ui.TextInput(label="Seu nome", placeholder="Ex: Brenno")
    personagem = discord.ui.TextInput(label="Nome do personagem", placeholder="Ex: Carlos Silva")
    idade = discord.ui.TextInput(label="Idade", placeholder="Ex: 18")
    motivo = discord.ui.TextInput(
        label="Por que quer entrar na Croácia?",
        style=discord.TextStyle.paragraph,
        placeholder="Explique seu motivo..."
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)

        try:
            cargo_membros = interaction.guild.get_role(CARGO_MEMBROS_ID)

            if not cargo_membros:
                await interaction.followup.send(
                    "❌ Cargo Membros não encontrado. Avise a liderança para conferir o ID.",
                    ephemeral=True
                )
                return

            try:
                await interaction.user.add_roles(
                    cargo_membros,
                    reason="Recrutamento preenchido automaticamente"
                )
            except discord.Forbidden:
                await interaction.followup.send(
                    "❌ Não consegui aplicar o cargo Membros. Meu cargo precisa estar acima dele e eu preciso da permissão Gerenciar Cargos.",
                    ephemeral=True
                )
                return
            except discord.HTTPException:
                await interaction.followup.send(
                    "❌ O Discord recusou a aplicação do cargo. Confira permissões e hierarquia de cargos.",
                    ephemeral=True
                )
                return

            apelido_alterado, novo_apelido, erro_apelido = await aplicar_apelido_membro(
                interaction.user,
                self.personagem.value,
                "Apelido alterado após recrutamento"
            )

            uid = str(interaction.user.id)

            # Garante que todas as áreas existam no dados.json.
            data.setdefault("saldos", {})
            data.setdefault("farms", {})
            data.setdefault("registros", {})
            data.setdefault("advertencias", {})
            data.setdefault("blacklist", [])
            data.setdefault("caixa", 0)
            data.setdefault("recrutamentos", {})
            data.setdefault("metas_farm", {"five": 500, "ak47": 500, "outros": 500})
            data.setdefault("farms_semanais", {})
            data.setdefault("historico_farms", [])

            # Salva o membro no sistema principal.
            data["registros"][uid] = {
                "nome": self.personagem.value,
                "cargo": "Membros",
                "apelido": novo_apelido
            }

            # Salva o formulário completo do recrutamento.
            data["recrutamentos"][uid] = {
                "discord_id": interaction.user.id,
                "discord": str(interaction.user),
                "nome": self.nome.value,
                "personagem": self.personagem.value,
                "idade": self.idade.value,
                "motivo": self.motivo.value,
                "cargo_recebido": "Membros",
                "apelido_definido": novo_apelido,
                "apelido_alterado": apelido_alterado
            }

            # Garante campos iniciais.
            data["saldos"].setdefault(uid, 0)
            data["farms"].setdefault(uid, 0)
            data["advertencias"].setdefault(uid, [])

            salvar()

            embed = embed_base(
                "📋 Novo Recrutamento Aprovado Automaticamente",
                "Novo membro entrou pela ficha de recrutamento.",
                discord.Color.green()
            )
            embed.add_field(name="Usuário", value=interaction.user.mention, inline=False)
            embed.add_field(name="Nome", value=self.nome.value, inline=True)
            embed.add_field(name="Personagem", value=self.personagem.value, inline=True)
            embed.add_field(name="Idade", value=self.idade.value, inline=True)
            embed.add_field(name="Motivo", value=self.motivo.value, inline=False)
            embed.add_field(name="Cargo aplicado", value=cargo_membros.mention, inline=False)
            embed.add_field(name="Apelido definido", value=novo_apelido, inline=False)

            if not apelido_alterado:
                embed.add_field(
                    name="Aviso",
                    value=erro_apelido or "Não consegui alterar o apelido.",
                    inline=False
                )

            canal = interaction.guild.get_channel(RECRUTAMENTO_CHANNEL_ID)
            if canal:
                await canal.send(embed=embed)

            await enviar_log(
                interaction.guild,
                "✅ Recrutamento automático",
                f"**Membro:** {interaction.user.mention}\n"
                f"**Cargo aplicado:** {cargo_membros.mention}\n"
                f"**Personagem:** {self.personagem.value}\n"
                f"**Apelido:** {novo_apelido}\n"
                f"**Apelido alterado:** {'Sim' if apelido_alterado else 'Não'}\n"
                f"**Formulário:** salvo em dados.json",
                discord.Color.green()
            )

            resposta = f"✅ Recrutamento enviado e salvo! Você recebeu o cargo {cargo_membros.mention}."

            if apelido_alterado:
                resposta += f"\n✅ Seu apelido foi alterado para: **{novo_apelido}**"
            else:
                resposta += f"\n⚠️ Não consegui alterar seu apelido: {erro_apelido}"

            await interaction.followup.send(resposta, ephemeral=True)

        except Exception as erro:
            print(f"ERRO NO RECRUTAMENTO: {repr(erro)}")
            await interaction.followup.send(
                "❌ Ocorreu um erro ao concluir o recrutamento. Avise a liderança e veja o erro no terminal.",
                ephemeral=True
            )


class RecrutamentoView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Entrar na Croácia", style=discord.ButtonStyle.danger)
    async def recrutar(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(RecrutamentoModal())


@bot.tree.command(name="recrutamento", description="Cria painel de recrutamento")
async def recrutamento(interaction: discord.Interaction):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    embed = embed_base(
        "🇭🇷 Recrutamento Croácia",
        "Clique no botão abaixo para iniciar seu recrutamento.",
        discord.Color.dark_red()
    )
    embed.add_field(
        name="Requisitos",
        value="• Ser ativo\n• Respeitar a hierarquia\n• Ter compromisso com a facção",
        inline=False
    )
    embed.add_field(
        name="Como funciona",
        value="Clique no botão, responda o formulário e receba o cargo Membros automaticamente e fique salvo no sistema.",
        inline=False
    )

    await interaction.response.send_message(embed=embed, view=RecrutamentoView())


@bot.tree.command(name="verrecrutamento", description="Mostra o formulário salvo de um membro")
async def verrecrutamento(interaction: discord.Interaction, membro: discord.Member):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    uid = str(membro.id)
    ficha = data.get("recrutamentos", {}).get(uid)

    if not ficha:
        await interaction.response.send_message("❌ Esse membro não tem formulário salvo.", ephemeral=True)
        return

    embed = embed_base("📋 Formulário de Recrutamento", color=discord.Color.dark_red())
    embed.add_field(name="Usuário", value=membro.mention, inline=False)
    embed.add_field(name="Nome", value=ficha.get("nome", "Não informado"), inline=True)
    embed.add_field(name="Personagem", value=ficha.get("personagem", "Não informado"), inline=True)
    embed.add_field(name="Idade", value=ficha.get("idade", "Não informado"), inline=True)
    embed.add_field(name="Motivo", value=ficha.get("motivo", "Não informado"), inline=False)
    embed.add_field(name="Cargo recebido", value=ficha.get("cargo_recebido", "Membros"), inline=False)

    await interaction.response.send_message(embed=embed)



# =========================
# SISTEMA DE INDICAÇÃO
# =========================

@bot.tree.command(name="indicado", description="Informa quem indicou você e oculta o canal de indicação")
async def indicado(interaction: discord.Interaction, indicado_por: discord.Member):
    if indicado_por.id == interaction.user.id:
        await interaction.response.send_message("❌ Você não pode indicar você mesmo.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=True)

    uid = str(interaction.user.id)
    data.setdefault("indicacoes", {})

    if uid in data["indicacoes"]:
        antigo_id = data["indicacoes"][uid].get("indicado_por_id")
        await interaction.followup.send(
            f"❌ Sua indicação já foi registrada anteriormente por <@{antigo_id}>.",
            ephemeral=True
        )
        return

    canal_indicacao = interaction.guild.get_channel(INDICACAO_CHANNEL_ID)
    if not canal_indicacao:
        await interaction.followup.send(
            "❌ Canal de indicação não encontrado. Confira o ID configurado no bot.",
            ephemeral=True
        )
        return

    data["indicacoes"][uid] = {
        "membro_id": interaction.user.id,
        "membro": str(interaction.user),
        "indicado_por_id": indicado_por.id,
        "indicado_por": str(indicado_por),
        "canal_id": INDICACAO_CHANNEL_ID,
        "canal": str(canal_indicacao),
        "data": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    salvar()

    await enviar_log(
        interaction.guild,
        "🤝 Indicação registrada",
        f"**Membro:** {interaction.user.mention}\n"
        f"**Indicado por:** {indicado_por.mention}\n"
        f"**Canal ocultado:** {canal_indicacao.mention}\n"
        f"**Ação:** canal de indicação ocultado para o membro.",
        discord.Color.green()
    )

    await interaction.followup.send(
        f"✅ Indicação registrada! Você informou que foi indicado por {indicado_por.mention}.\n"
        f"🔒 O canal {canal_indicacao.mention} será ocultado para você agora.",
        ephemeral=True
    )

    try:
        await canal_indicacao.set_permissions(
            interaction.user,
            view_channel=False,
            reason="Indicação registrada automaticamente"
        )
    except discord.Forbidden:
        await enviar_log(
            interaction.guild,
            "⚠️ Falha ao ocultar canal de indicação",
            f"**Membro:** {interaction.user.mention}\n"
            f"**Canal:** {canal_indicacao.mention}\n"
            "**Erro:** o bot não tem permissão para gerenciar permissões do canal.",
            discord.Color.orange()
        )
    except discord.HTTPException:
        await enviar_log(
            interaction.guild,
            "⚠️ Falha ao ocultar canal de indicação",
            f"**Membro:** {interaction.user.mention}\n"
            f"**Canal:** {canal_indicacao.mention}\n"
            "**Erro:** o Discord recusou a alteração de permissão.",
            discord.Color.orange()
        )


@bot.tree.command(name="verindicacao", description="Mostra quem indicou um membro")
async def verindicacao(interaction: discord.Interaction, membro: discord.Member):
    await interaction.response.defer(ephemeral=True)

    try:
        if not tem_permissao(interaction.user):
            await interaction.followup.send("❌ Sem permissão.", ephemeral=True)
            return

        uid = str(membro.id)
        data.setdefault("indicacoes", {})
        ficha = data.get("indicacoes", {}).get(uid)

        if not ficha:
            await interaction.followup.send("❌ Esse membro ainda não registrou indicação.", ephemeral=True)
            return

        if not isinstance(ficha, dict):
            await interaction.followup.send(
                "❌ A indicação desse membro está salva em formato antigo/incorreto. Use `/resetindicacao` e peça para registrar novamente.",
                ephemeral=True
            )
            return

        indicado_por_id = ficha.get("indicado_por_id")
        canal_id = ficha.get("canal_id", INDICACAO_CHANNEL_ID)
        data_registro = ficha.get("data", "Não informado")

        indicado_por_texto = f"<@{indicado_por_id}>" if indicado_por_id else "Não informado"
        canal_texto = f"<#{canal_id}>" if canal_id else "Não informado"

        embed = embed_base("🤝 Ficha de Indicação", color=discord.Color.dark_red())
        embed.add_field(name="Membro", value=membro.mention, inline=False)
        embed.add_field(name="Indicado por", value=indicado_por_texto, inline=False)
        embed.add_field(name="Canal", value=canal_texto, inline=True)
        embed.add_field(name="Data", value=data_registro, inline=True)

        await interaction.followup.send(embed=embed, ephemeral=True)

    except Exception as erro:
        print(f"ERRO NO /verindicacao: {repr(erro)}")
        try:
            await interaction.followup.send(
                "❌ Ocorreu um erro ao consultar essa indicação. Veja o erro no terminal do bot.",
                ephemeral=True
            )
        except Exception:
            pass


@bot.tree.command(name="liberarindicacao", description="Libera novamente o canal de indicação para um membro")
async def liberarindicacao(interaction: discord.Interaction, membro: discord.Member):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    canal_indicacao = interaction.guild.get_channel(INDICACAO_CHANNEL_ID)
    if not canal_indicacao:
        await interaction.response.send_message("❌ Canal de indicação não encontrado. Confira o ID configurado no bot.", ephemeral=True)
        return

    try:
        await canal_indicacao.set_permissions(
            membro,
            overwrite=None,
            reason=f"Canal de indicação liberado por {interaction.user}"
        )
    except discord.Forbidden:
        await interaction.response.send_message("❌ Não tenho permissão para alterar permissões deste canal.", ephemeral=True)
        return
    except discord.HTTPException:
        await interaction.response.send_message("❌ O Discord recusou a alteração de permissão.", ephemeral=True)
        return

    await enviar_log(
        interaction.guild,
        "🔓 Canal de indicação liberado",
        f"**Membro:** {membro.mention}\n**Canal:** {canal_indicacao.mention}\n**Por:** {interaction.user.mention}",
        discord.Color.gold()
    )

    await interaction.response.send_message(f"✅ {membro.mention} voltou a ter a permissão normal em {canal_indicacao.mention}.", ephemeral=True)


@bot.tree.command(name="resetindicacao", description="Apaga o registro de indicação de um membro")
async def resetindicacao(interaction: discord.Interaction, membro: discord.Member):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    uid = str(membro.id)
    data.setdefault("indicacoes", {})

    if uid not in data["indicacoes"]:
        await interaction.response.send_message("❌ Esse membro não tem indicação registrada.", ephemeral=True)
        return

    data["indicacoes"].pop(uid, None)
    salvar()

    await enviar_log(
        interaction.guild,
        "♻️ Indicação resetada",
        f"**Membro:** {membro.mention}\n**Por:** {interaction.user.mention}",
        discord.Color.orange()
    )

    await interaction.response.send_message(f"✅ Indicação de {membro.mention} foi resetada.", ephemeral=True)


# =========================
# SISTEMA DE NOMES / TAGS
# =========================

@bot.tree.command(name="renomear", description="Aplica a tag Membro no apelido de um membro")
async def renomear(interaction: discord.Interaction, membro: discord.Member, nome: str):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    sucesso, novo_apelido, erro = await aplicar_apelido_membro(
        membro,
        nome,
        f"Renomeado por {interaction.user}"
    )

    uid = str(membro.id)
    data.setdefault("registros", {})
    if uid not in data["registros"]:
        data["registros"][uid] = {"nome": nome, "cargo": "Membros", "apelido": novo_apelido}
    else:
        data["registros"][uid]["nome"] = nome
        data["registros"][uid]["apelido"] = novo_apelido

    salvar()

    if not sucesso:
        await interaction.response.send_message(f"❌ Não consegui alterar o apelido: {erro}", ephemeral=True)
        return

    await enviar_log(
        interaction.guild,
        "🏷️ Apelido alterado",
        f"**Membro:** {membro.mention}\n**Novo apelido:** {novo_apelido}\n**Por:** {interaction.user.mention}",
        discord.Color.green()
    )

    embed = embed_base("🏷️ Apelido atualizado", color=discord.Color.green())
    embed.add_field(name="Membro", value=membro.mention, inline=False)
    embed.add_field(name="Novo apelido", value=novo_apelido, inline=False)
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="arrumarnome", description="Aplica a tag Membro usando o nome já salvo na ficha")
async def arrumarnome(interaction: discord.Interaction, membro: discord.Member):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    uid = str(membro.id)
    dados = data.get("registros", {}).get(uid)

    if not dados:
        await interaction.response.send_message("❌ Esse membro não está registrado no sistema.", ephemeral=True)
        return

    nome = dados.get("nome", membro.display_name)
    sucesso, novo_apelido, erro = await aplicar_apelido_membro(
        membro,
        nome,
        f"Nome ajustado por {interaction.user}"
    )

    dados["apelido"] = novo_apelido
    salvar()

    if not sucesso:
        await interaction.response.send_message(f"❌ Não consegui alterar o apelido: {erro}", ephemeral=True)
        return

    embed = embed_base("✅ Nome ajustado", f"{membro.mention} agora está como **{novo_apelido}**.", discord.Color.green())
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="minhatag", description="Mostra como seu nome ficaria com a tag de membro")
async def minhatag(interaction: discord.Interaction, nome: str):
    apelido = montar_apelido_membro(nome)
    embed = embed_base("🏷️ Prévia da tag", f"Seu apelido ficaria:\n**{apelido}**", discord.Color.gold())
    await interaction.response.send_message(embed=embed, ephemeral=True)



# =========================
# EMBED BUILDER AVANÇADO
# =========================

EMBED_SESSIONS = {}


def quebrar_linhas(texto: str | None):
    if not texto:
        return None
    return texto.replace("\\n", "\n")


def cor_por_nome(nome: str):
    cores = {
        "vermelho": discord.Color.red(),
        "vermelhoescuro": discord.Color.dark_red(),
        "dourado": discord.Color.gold(),
        "verde": discord.Color.green(),
        "azul": discord.Color.blue(),
        "roxo": discord.Color.purple(),
        "preto": discord.Color.from_rgb(10, 10, 10),
        "branco": discord.Color.from_rgb(245, 245, 245),
        "cinza": discord.Color.dark_grey(),
    }
    return cores.get(nome.lower().replace(" ", ""), discord.Color.dark_red())


class EmbedDraft:
    def __init__(self, autor: discord.Member):
        self.user_id = autor.id
        self.titulo = "Título do Embed"
        self.descricao = "Descrição do embed.\n\nUse o botão **Texto** para editar."
        self.cor = discord.Color.dark_red()
        self.imagem_url = None
        self.thumbnail_url = None
        self.autor_nome = None
        self.autor_icone = None
        self.rodape = f"{NOME_FACCAO} • Embed personalizado"
        self.rodape_icone = None
        self.mencoes = ""
        self.canal_id = None

    def gerar_embed(self):
        embed = discord.Embed(
            title=self.titulo,
            description=self.descricao,
            color=self.cor
        )

        if self.imagem_url:
            embed.set_image(url=self.imagem_url)

        if self.thumbnail_url:
            embed.set_thumbnail(url=self.thumbnail_url)

        if self.autor_nome:
            embed.set_author(name=self.autor_nome, icon_url=self.autor_icone or None)

        if self.rodape:
            embed.set_footer(text=self.rodape, icon_url=self.rodape_icone or None)

        return embed


class EmbedTextoModal(discord.ui.Modal, title="Editar texto do Embed"):
    titulo = discord.ui.TextInput(
        label="Título",
        placeholder="Ex: Recrutamento Aberto",
        max_length=256,
        required=False
    )

    descricao = discord.ui.TextInput(
        label="Descrição",
        placeholder="Use \\n para pular linha. Ex: Linha 1\\n\\nLinha 3",
        style=discord.TextStyle.paragraph,
        max_length=4000,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        draft = EMBED_SESSIONS.get(interaction.user.id)
        if not draft:
            await interaction.response.send_message("❌ Sessão de embed expirada. Use `/embedbuilder` de novo.", ephemeral=True)
            return

        if self.titulo.value:
            draft.titulo = quebrar_linhas(self.titulo.value)

        if self.descricao.value:
            draft.descricao = quebrar_linhas(self.descricao.value)

        await interaction.response.send_message("✅ Texto atualizado.", ephemeral=True)


class EmbedVisualModal(discord.ui.Modal, title="Visual do Embed"):
    cor_hex = discord.ui.TextInput(
        label="Cor HEX",
        placeholder="Ex: #8B0000",
        default="#8B0000",
        required=False,
        max_length=7
    )

    imagem_url = discord.ui.TextInput(
        label="Imagem grande URL",
        placeholder="https://site.com/imagem.png",
        required=False
    )

    thumbnail_url = discord.ui.TextInput(
        label="Thumbnail URL",
        placeholder="https://site.com/thumb.png",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        draft = EMBED_SESSIONS.get(interaction.user.id)
        if not draft:
            await interaction.response.send_message("❌ Sessão de embed expirada. Use `/embedbuilder` de novo.", ephemeral=True)
            return

        if self.cor_hex.value:
            cor_limpa = self.cor_hex.value.replace("#", "").strip()
            try:
                draft.cor = discord.Color(int(cor_limpa, 16))
            except ValueError:
                await interaction.response.send_message("❌ Cor inválida. Use formato HEX, exemplo: `#8B0000`.", ephemeral=True)
                return

        draft.imagem_url = self.imagem_url.value.strip() or None
        draft.thumbnail_url = self.thumbnail_url.value.strip() or None

        await interaction.response.send_message("✅ Visual atualizado.", ephemeral=True)


class EmbedExtraModal(discord.ui.Modal, title="Autor e rodapé"):
    autor_nome = discord.ui.TextInput(
        label="Nome do autor",
        placeholder="Ex: Liderança Croácia",
        required=False,
        max_length=256
    )

    autor_icone = discord.ui.TextInput(
        label="Ícone do autor URL",
        placeholder="https://site.com/icon.png",
        required=False
    )

    rodape = discord.ui.TextInput(
        label="Rodapé",
        placeholder="Ex: Croácia RP • Sistema Oficial",
        required=False,
        max_length=2048
    )

    rodape_icone = discord.ui.TextInput(
        label="Ícone do rodapé URL",
        placeholder="https://site.com/footer.png",
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        draft = EMBED_SESSIONS.get(interaction.user.id)
        if not draft:
            await interaction.response.send_message("❌ Sessão de embed expirada. Use `/embedbuilder` de novo.", ephemeral=True)
            return

        draft.autor_nome = self.autor_nome.value.strip() or None
        draft.autor_icone = self.autor_icone.value.strip() or None
        draft.rodape = self.rodape.value.strip() or f"{NOME_FACCAO} • Embed personalizado"
        draft.rodape_icone = self.rodape_icone.value.strip() or None

        await interaction.response.send_message("✅ Autor e rodapé atualizados.", ephemeral=True)


class EmbedMencoesModal(discord.ui.Modal, title="Menções e destino"):
    mencoes = discord.ui.TextInput(
        label="Menções antes do embed",
        placeholder="Ex: @Membros ou cole <@&ID_DO_CARGO>",
        required=False,
        max_length=1000
    )

    canal_id = discord.ui.TextInput(
        label="Canal de destino ID ou menção",
        placeholder="Opcional. Ex: 123456789 ou #avisos",
        required=False,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        draft = EMBED_SESSIONS.get(interaction.user.id)
        if not draft:
            await interaction.response.send_message("❌ Sessão de embed expirada. Use `/embedbuilder` de novo.", ephemeral=True)
            return

        draft.mencoes = self.mencoes.value.strip()

        canal_texto = self.canal_id.value.strip()
        draft.canal_id = None

        if canal_texto:
            numeros = "".join(ch for ch in canal_texto if ch.isdigit())
            if numeros:
                draft.canal_id = int(numeros)

        await interaction.response.send_message("✅ Menções e destino atualizados.", ephemeral=True)


class EmbedCamposModal(discord.ui.Modal, title="Adicionar campo"):
    nome = discord.ui.TextInput(
        label="Nome do campo",
        placeholder="Ex: Requisitos",
        max_length=256
    )

    valor = discord.ui.TextInput(
        label="Valor do campo",
        placeholder="Use \\n para pular linha.",
        style=discord.TextStyle.paragraph,
        max_length=1024
    )

    async def on_submit(self, interaction: discord.Interaction):
        draft = EMBED_SESSIONS.get(interaction.user.id)
        if not draft:
            await interaction.response.send_message("❌ Sessão de embed expirada. Use `/embedbuilder` de novo.", ephemeral=True)
            return

        # Guarda campos em atributo criado sob demanda.
        if not hasattr(draft, "campos"):
            draft.campos = []

        if len(draft.campos) >= 10:
            await interaction.response.send_message("❌ Limite de 10 campos atingido neste builder.", ephemeral=True)
            return

        draft.campos.append((self.nome.value, quebrar_linhas(self.valor.value)))
        await interaction.response.send_message("✅ Campo adicionado.", ephemeral=True)


class EmbedBuilderView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=900)

    async def _get_draft(self, interaction: discord.Interaction):
        draft = EMBED_SESSIONS.get(interaction.user.id)
        if not draft:
            await interaction.response.send_message("❌ Sessão expirada. Use `/embedbuilder` de novo.", ephemeral=True)
            return None
        return draft

    @discord.ui.button(label="Texto", style=discord.ButtonStyle.primary, emoji="✏️", row=0)
    async def editar_texto(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not tem_permissao(interaction.user):
            await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
            return
        await interaction.response.send_modal(EmbedTextoModal())

    @discord.ui.button(label="Visual", style=discord.ButtonStyle.primary, emoji="🖼️", row=0)
    async def editar_visual(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not tem_permissao(interaction.user):
            await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
            return
        await interaction.response.send_modal(EmbedVisualModal())

    @discord.ui.button(label="Autor/Rodapé", style=discord.ButtonStyle.secondary, emoji="🏷️", row=0)
    async def editar_extra(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not tem_permissao(interaction.user):
            await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
            return
        await interaction.response.send_modal(EmbedExtraModal())

    @discord.ui.button(label="Menções", style=discord.ButtonStyle.secondary, emoji="📣", row=1)
    async def editar_mencoes(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not tem_permissao(interaction.user):
            await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
            return
        await interaction.response.send_modal(EmbedMencoesModal())

    @discord.ui.button(label="Campo", style=discord.ButtonStyle.secondary, emoji="➕", row=1)
    async def adicionar_campo(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not tem_permissao(interaction.user):
            await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
            return
        await interaction.response.send_modal(EmbedCamposModal())

    @discord.ui.button(label="Vermelho", style=discord.ButtonStyle.danger, emoji="🔴", row=2)
    async def cor_vermelha(self, interaction: discord.Interaction, button: discord.ui.Button):
        draft = await self._get_draft(interaction)
        if not draft:
            return
        draft.cor = discord.Color.dark_red()
        await interaction.response.send_message("✅ Cor definida: vermelho escuro.", ephemeral=True)

    @discord.ui.button(label="Dourado", style=discord.ButtonStyle.secondary, emoji="🟡", row=2)
    async def cor_dourada(self, interaction: discord.Interaction, button: discord.ui.Button):
        draft = await self._get_draft(interaction)
        if not draft:
            return
        draft.cor = discord.Color.gold()
        await interaction.response.send_message("✅ Cor definida: dourado.", ephemeral=True)

    @discord.ui.button(label="Verde", style=discord.ButtonStyle.success, emoji="🟢", row=2)
    async def cor_verde(self, interaction: discord.Interaction, button: discord.ui.Button):
        draft = await self._get_draft(interaction)
        if not draft:
            return
        draft.cor = discord.Color.green()
        await interaction.response.send_message("✅ Cor definida: verde.", ephemeral=True)

    @discord.ui.button(label="Preview", style=discord.ButtonStyle.secondary, emoji="👁️", row=3)
    async def preview(self, interaction: discord.Interaction, button: discord.ui.Button):
        draft = await self._get_draft(interaction)
        if not draft:
            return

        embed = draft.gerar_embed()
        if hasattr(draft, "campos"):
            for nome, valor in draft.campos:
                embed.add_field(name=nome, value=valor, inline=False)

        await interaction.response.send_message(
            content=draft.mencoes or None,
            embed=embed,
            ephemeral=True,
            allowed_mentions=discord.AllowedMentions(users=True, roles=True, everyone=False)
        )

    @discord.ui.button(label="Enviar", style=discord.ButtonStyle.success, emoji="✅", row=3)
    async def enviar(self, interaction: discord.Interaction, button: discord.ui.Button):
        draft = await self._get_draft(interaction)
        if not draft:
            return

        canal_destino = interaction.channel
        if draft.canal_id:
            canal_encontrado = interaction.guild.get_channel(draft.canal_id)
            if canal_encontrado:
                canal_destino = canal_encontrado

        embed = draft.gerar_embed()
        if hasattr(draft, "campos"):
            for nome, valor in draft.campos:
                embed.add_field(name=nome, value=valor, inline=False)

        await canal_destino.send(
            content=draft.mencoes or None,
            embed=embed,
            allowed_mentions=discord.AllowedMentions(users=True, roles=True, everyone=False)
        )

        await enviar_log(
            interaction.guild,
            "🎨 EmbedBuilder enviado",
            f"**Por:** {interaction.user.mention}\n"
            f"**Canal:** {canal_destino.mention}\n"
            f"**Título:** {draft.titulo}",
            discord.Color.dark_gold()
        )

        await interaction.response.send_message(f"✅ Embed enviado em {canal_destino.mention}.", ephemeral=True)


@bot.tree.command(name="embedbuilder", description="Criador avançado de embed com imagem, menções, cores e campos")
async def embedbuilder(interaction: discord.Interaction):
    if not tem_permissao(interaction.user):
        await interaction.response.send_message("❌ Sem permissão.", ephemeral=True)
        return

    EMBED_SESSIONS[interaction.user.id] = EmbedDraft(interaction.user)

    embed = embed_base(
        "🎨 EmbedBuilder Completo",
        "**Painel avançado para criar embeds grandes e personalizados.**\n\n"
        "Use os botões abaixo para configurar:\n"
        "• Texto com espaços entre linhas usando `\\n`\n"
        "• Cor HEX ou cores pré-selecionadas\n"
        "• Imagem grande\n"
        "• Thumbnail\n"
        "• Autor e rodapé\n"
        "• Menção de cargo ou usuário\n"
        "• Canal de destino\n"
        "• Campos extras\n\n"
        "Quando terminar, clique em **Enviar**.",
        discord.Color.dark_red()
    )

    await interaction.response.send_message(embed=embed, view=EmbedBuilderView(), ephemeral=True)


# =========================
# START
# =========================

if not TOKEN:
    raise ValueError("Token não encontrado. Confira o arquivo .env")

bot.run(TOKEN)
