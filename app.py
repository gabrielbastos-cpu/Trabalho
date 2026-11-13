
import sqlite3
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "mequi-experience-chave-secreta"


# ========================================
# CONEXÃO COM O BANCO
# ========================================

def conectar_banco():
    conexao = sqlite3.connect("banco.db")
    conexao.row_factory = sqlite3.Row
    return conexao


# ========================================
# CONFIGURAÇÃO DO BANCO
# ========================================

def configurar_banco():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nome TEXT NOT NULL,
        preco REAL NOT NULL,
        categoria TEXT NOT NULL,
        imagem TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS pedidos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        total REAL NOT NULL,
        data DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("PRAGMA table_info(pedidos)")
    colunas = [coluna["name"] for coluna in cursor.fetchall()]

    if "status" not in colunas:
        cursor.execute("""
            ALTER TABLE pedidos
            ADD COLUMN status TEXT DEFAULT 'Pendente'
        """)

    # Itens dos pedidos
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS itens_pedido (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pedido_id INTEGER NOT NULL,
        produto_id INTEGER NOT NULL,
        quantidade INTEGER NOT NULL,
        preco REAL NOT NULL,
        FOREIGN KEY (pedido_id) REFERENCES pedidos(id),
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
    )
    """)

    # Adiciona informações dos combos
    cursor.execute("PRAGMA table_info(itens_pedido)")
    colunas_itens = [coluna["name"] for coluna in cursor.fetchall()]

    if "tipo" not in colunas_itens:
        cursor.execute("""
            ALTER TABLE itens_pedido
            ADD COLUMN tipo TEXT DEFAULT 'individual'
        """)

    if "descricao" not in colunas_itens:
        cursor.execute("""
            ALTER TABLE itens_pedido
            ADD COLUMN descricao TEXT DEFAULT ''
        """)

    # Tabela de preços promocionais
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS combos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER UNIQUE NOT NULL,
        preco_promocional REAL NOT NULL,
        FOREIGN KEY (produto_id) REFERENCES produtos(id)
    )
    """)

    # Funcionários
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )
    """)

    cursor.execute(
        "SELECT id FROM funcionarios WHERE usuario = ?",
        ("admin",)
    )

    if cursor.fetchone() is None:
        senha_hash = generate_password_hash("Mequi2026!")

        cursor.execute("""
            INSERT INTO funcionarios (usuario, senha)
            VALUES (?, ?)
        """, ("admin", senha_hash))

    # Produtos iniciais
    produtos_iniciais = [
        ("Big Mac", 35.00, "hamburguer", "original.png"),
        ("McChicken", 24.00, "hamburguer", "mchincken.png"),
        ("McMelt", 28.00, "hamburguer", "mcmelt.png"),
        ("McDouble", 32.00, "hamburguer", "duploburguer.png"),
        ("McCheese", 26.00, "hamburguer", "cheese.png"),
        ("Quarteirão com Queijo", 29.00, "hamburguer", "quarterao.png"),
        ("McNífico", 34.00, "hamburguer", "nifico.png"),
        ("McTasty", 35.00, "hamburguer", "tasty.png"),
        ("McCrispy", 35.00, "hamburguer", "crispy.png"),

        ("Casquinha de Baunilha", 7.00, "sorvete", "baunilha.png"),
        ("Casquinha de Chocolate", 7.00, "sorvete", "chocolate.png"),
        ("Casquinha Mista", 7.00, "sorvete", "mista.png"),
        ("McShake de Morango", 15.00, "sorvete", "shakem.png"),
        ("McShake de Ovomaltine", 15.00, "sorvete", "shakeo.png"),
        ("McSundae de Chocolate", 10.00, "sorvete", "sundaec.png"),
        ("McSundae de Morango", 10.00, "sorvete", "sundaem.png"),
        ("McSundae de Caramelo", 10.00, "sorvete", "sundaeca.png"),
        ("McFlurry de Ovomaltine", 18.00, "sorvete", "mcfluryovo.png"),

        ("Batata pequena", 10.00, "acompanhamento", "batatap.png"),
        ("Batata média", 12.00, "acompanhamento", "batatam.png"),
        ("Batata grande", 15.00, "acompanhamento", "batatag.png"),
        ("Batata Grande com Cheddar", 18.00, "acompanhamento", "batatac.png"),
        ("Nuggets", 15.00, "acompanhamento", "Nuggets.png")
    ]

    for produto in produtos_iniciais:
        cursor.execute(
            "SELECT id FROM produtos WHERE nome = ?",
            (produto[0],)
        )

        if cursor.fetchone() is None:
            cursor.execute("""
                INSERT INTO produtos (nome, preco, categoria, imagem)
                VALUES (?, ?, ?, ?)
            """, produto)

    # Preços promocionais dos combos
    precos_combos = {
        "Big Mac": 49.90,
        "McChicken": 39.90,
        "McMelt": 43.90,
        "McDouble": 45.90,
        "McCheese": 40.90,
        "Quarteirão com Queijo": 44.90,
        "McNífico": 49.90,
        "McTasty": 49.90,
        "McCrispy": 49.90
    }

    for nome, preco in precos_combos.items():
        cursor.execute(
            "SELECT id FROM produtos WHERE nome = ?",
            (nome,)
        )

        produto = cursor.fetchone()

        if produto:
            cursor.execute("""
                INSERT OR IGNORE INTO combos
                (produto_id, preco_promocional)
                VALUES (?, ?)
            """, (produto["id"], preco))

    conexao.commit()
    conexao.close()


# ========================================
# OPÇÕES DOS COMBOS
# ========================================

BEBIDAS = {
    "Coca-Cola": 8.00,
    "Fanta": 8.00,
    "Sprite": 8.00,
    "Água": 5.00
}


def buscar_batatas():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT nome, preco
        FROM produtos
        WHERE nome IN (
            'Batata pequena',
            'Batata média',
            'Batata grande'
        )
    """)

    batatas = {
        item["nome"]: item["preco"]
        for item in cursor.fetchall()
    }

    conexao.close()
    return batatas


# ========================================
# PÁGINA INICIAL
# ========================================

@app.route("/")
def inicio():
    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("SELECT * FROM produtos")
    produtos = cursor.fetchall()

    cursor.execute("SELECT produto_id, preco_promocional FROM combos")
    combos = {
        item["produto_id"]: item["preco_promocional"]
        for item in cursor.fetchall()
    }

    conexao.close()

    return render_template(
        "index.html",
        produtos=produtos,
        combos=combos
    )


# ========================================
# CARRINHO
# ========================================

@app.route("/carrinho")
def carrinho():
    return render_template("carrinho.html")


# ========================================
# LOGIN
# ========================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        usuario = request.form.get("usuario")
        senha = request.form.get("senha")

        conexao = conectar_banco()
        cursor = conexao.cursor()

        cursor.execute(
            "SELECT * FROM funcionarios WHERE usuario = ?",
            (usuario,)
        )

        funcionario = cursor.fetchone()
        conexao.close()

        if funcionario and check_password_hash(funcionario["senha"], senha):

            session.clear()
            session["funcionario_id"] = funcionario["id"]
            session["funcionario_usuario"] = funcionario["usuario"]

            return redirect(url_for("funcionarios"))

        return render_template(
            "login.html",
            erro="Usuário ou senha incorretos"
        )

    return render_template("login.html")


# ========================================
# SAIR DA CONTA
# ========================================

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ========================================
# PAINEL DOS FUNCIONÁRIOS
# ========================================

@app.route("/funcionarios")
def funcionarios():

    if "funcionario_id" not in session:
        return redirect(url_for("login"))

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            id,
            total,
            datetime(data, 'localtime') AS data,
            status
        FROM pedidos
        ORDER BY id DESC
    """)

    pedidos = cursor.fetchall()
    pedidos_com_itens = []

    for pedido in pedidos:

        cursor.execute("""
            SELECT
                produtos.nome,
                itens_pedido.quantidade,
                itens_pedido.preco,
                itens_pedido.tipo,
                itens_pedido.descricao
            FROM itens_pedido
            JOIN produtos ON produtos.id = itens_pedido.produto_id
            WHERE itens_pedido.pedido_id = ?
        """, (pedido["id"],))

        itens = cursor.fetchall()

        pedidos_com_itens.append({
            "dados": pedido,
            "itens": itens
        })

    conexao.close()

    return render_template(
        "funcionarios.html",
        pedidos=pedidos_com_itens
    )


# ========================================
# ATUALIZAR STATUS
# ========================================

@app.route("/atualizar-status/<int:pedido_id>", methods=["POST"])
def atualizar_status(pedido_id):

    if "funcionario_id" not in session:
        return redirect(url_for("login"))

    novo_status = request.form.get("status")
    status_validos = ["Pendente", "Em preparo", "Concluído"]

    if novo_status not in status_validos:
        return "Status inválido", 400

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        UPDATE pedidos
        SET status = ?
        WHERE id = ?
    """, (novo_status, pedido_id))

    conexao.commit()
    conexao.close()

    return redirect(url_for("funcionarios"))


# ========================================
# EXCLUIR PEDIDO
# ========================================

@app.route("/excluir-pedido/<int:pedido_id>", methods=["POST"])
def excluir_pedido(pedido_id):

    if "funcionario_id" not in session:
        return redirect(url_for("login"))

    conexao = conectar_banco()

    try:
        cursor = conexao.cursor()

        # Exclui os itens vinculados ao pedido
        cursor.execute("""
            DELETE FROM itens_pedido
            WHERE pedido_id = ?
        """, (pedido_id,))

        # Exclui o pedido
        cursor.execute("""
            DELETE FROM pedidos
            WHERE id = ?
        """, (pedido_id,))

        conexao.commit()

    except sqlite3.Error:
        conexao.rollback()
        return "Não foi possível excluir o pedido.", 500

    finally:
        conexao.close()

    return redirect(url_for("funcionarios"))


# ========================================
# CONFIRMAÇÃO DO PEDIDO
# ========================================

@app.route("/pedidos/<int:pedido_id>")
def pedido_confirmado(pedido_id):

    conexao = conectar_banco()
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            id,
            total,
            datetime(data, 'localtime') AS data,
            status
        FROM pedidos
        WHERE id = ?
    """, (pedido_id,))

    pedido = cursor.fetchone()

    if pedido is None:
        conexao.close()
        return "Pedido não encontrado", 404

    cursor.execute("""
        SELECT
            produtos.nome,
            itens_pedido.quantidade,
            itens_pedido.preco,
            itens_pedido.tipo,
            itens_pedido.descricao
        FROM itens_pedido
        JOIN produtos ON produtos.id = itens_pedido.produto_id
        WHERE itens_pedido.pedido_id = ?
    """, (pedido_id,))

    itens = cursor.fetchall()
    conexao.close()

    return render_template(
        "pedidos.html",
        pedido=pedido,
        itens=itens
    )


# ========================================
# FINALIZAR PEDIDO
# ========================================

@app.route("/finalizar-pedido", methods=["POST"])
def finalizar_pedido():

    dados = request.get_json()

    if (
        not dados
        or not isinstance(dados.get("itens"), list)
        or not dados["itens"]
    ):
        return jsonify({"erro": "Carrinho vazio ou inválido"}), 400

    conexao = conectar_banco()

    try:
        cursor = conexao.cursor()
        total = 0
        itens_validos = []

        batatas = buscar_batatas()

        if "Batata média" not in batatas:
            return jsonify({"erro": "Opção de batata indisponível"}), 400

        for item in dados["itens"]:

            produto_id = item.get("id")
            quantidade = item.get("quantidade")
            tipo = item.get("tipo", "individual")

            if (
                type(produto_id) is not int or produto_id <= 0
                or type(quantidade) is not int or quantidade <= 0
                or quantidade > 50
            ):
                return jsonify({"erro": "Produto ou quantidade inválida"}), 400

            cursor.execute("""
                SELECT id, nome, preco
                FROM produtos
                WHERE id = ?
            """, (produto_id,))

            produto = cursor.fetchone()

            if produto is None:
                return jsonify({"erro": "Produto não encontrado"}), 400

            if tipo == "individual":

                preco = produto["preco"]
                descricao = ""

            elif tipo == "combo":

                cursor.execute("""
                    SELECT preco_promocional
                    FROM combos
                    WHERE produto_id = ?
                """, (produto_id,))

                combo = cursor.fetchone()

                if combo is None:
                    return jsonify({"erro": "Combo indisponível"}), 400

                batata = item.get("batata")
                bebida = item.get("bebida")

                if batata not in batatas or bebida not in BEBIDAS:
                    return jsonify({"erro": "Opção de combo inválida"}), 400

                # O preço promocional inclui batata média e Coca-Cola.
                # Outras escolhas alteram o preço pela diferença.

                preco = (
                    combo["preco_promocional"]
                    + batatas[batata]
                    - batatas["Batata média"]
                    + BEBIDAS[bebida]
                    - BEBIDAS["Coca-Cola"]
                )

                descricao = f"{batata} + {bebida}"

            else:
                return jsonify({"erro": "Tipo de item inválido"}), 400

            total += preco * quantidade

            itens_validos.append((
                produto_id,
                quantidade,
                preco,
                tipo,
                descricao
            ))

        # Cria o pedido
        cursor.execute(
            "INSERT INTO pedidos (total) VALUES (?)",
            (total,)
        )

        pedido_id = cursor.lastrowid

        # Registra os produtos do pedido
        for produto_id, quantidade, preco, tipo, descricao in itens_validos:

            cursor.execute("""
                INSERT INTO itens_pedido
                (pedido_id, produto_id, quantidade, preco, tipo, descricao)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                pedido_id,
                produto_id,
                quantidade,
                preco,
                tipo,
                descricao
            ))

        conexao.commit()

        return jsonify({
            "mensagem": "Pedido registrado com sucesso!",
            "pedido_id": pedido_id,
            "total": total
        })

    except sqlite3.Error:

        conexao.rollback()

        return jsonify({
            "erro": "Não foi possível registrar o pedido"
        }), 500

    finally:
        conexao.close()


# ========================================
# INICIAR A APLICAÇÃO
# ========================================

if __name__ == "__main__":
    configurar_banco()
    app.run(debug=True)




