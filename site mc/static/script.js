
/* ========================================
   1. CONFIGURAÇÕES DO CARRINHO
======================================== */

let carrinho = carregarCarrinho();
let finalizandoPedido = false;

let comboSelecionado = null;

const PRECO_BATATAS = {
    "Batata pequena": 10,
    "Batata média": 12,
    "Batata grande": 15
};

const PRECO_BEBIDAS = {
    "Coca-Cola": 8,
    "Fanta": 8,
    "Sprite": 8,
    "Água": 5
};


/* ========================================
   2. IDENTIFICAR CADA ITEM
======================================== */

function criarChave(produto) {
    return [
        produto.id,
        produto.tipo || "individual",
        produto.batata || "",
        produto.bebida || ""
    ].join("-");
}


/* ========================================
   3. CARREGAR E SALVAR CARRINHO
======================================== */

function carregarCarrinho() {

    try {

        const dados = JSON.parse(localStorage.getItem("carrinho")) || [];

        if (!Array.isArray(dados)) return [];

        return dados
            .filter(produto =>
                Number.isInteger(produto.id) &&
                typeof produto.nome === "string" &&
                Number.isFinite(produto.preco) &&
                produto.preco >= 0 &&
                Number.isInteger(produto.quantidade) &&
                produto.quantidade > 0
            )
            .map(produto => {

                const item = {
                    ...produto,
                    tipo: produto.tipo === "combo" ? "combo" : "individual",
                    batata: produto.batata || "",
                    bebida: produto.bebida || ""
                };

                item.chave = criarChave(item);

                return item;

            });

    } catch (erro) {

        console.error("Erro ao carregar carrinho:", erro);
        return [];

    }

}


function salvarCarrinho() {
    localStorage.setItem("carrinho", JSON.stringify(carrinho));
}


/* ========================================
   4. CONFIGURAR EVENTOS
======================================== */

document.addEventListener("DOMContentLoaded", function () {

    // Seletores individual / combo
    document.querySelectorAll(".tipo-pedido").forEach(seletor => {

        seletor.addEventListener("change", function () {

            if (this.value === "combo") {
                abrirModalCombo(this);
            }

        });

    });


    // Botões de adicionar produto
    document.querySelectorAll(".botao-adicionar").forEach(botao => {

        botao.addEventListener("click", function () {

            const cartao = this.closest(".cardapio-item");

            const seletor = cartao.querySelector(".tipo-pedido");

            // Evita adicionar combo sem passar pela personalização
            if (seletor && seletor.value === "combo") {
                abrirModalCombo(seletor);
                return;
            }

            const produto = {
                id: Number(this.dataset.id),
                nome: this.dataset.nome,
                preco: Number(this.dataset.preco),
                tipo: "individual",
                batata: "",
                bebida: ""
            };

            adicionarCarrinho(produto);

        });

    });


    // Eventos da janela modal
    const batataModal = document.getElementById("modal-batata");
    const bebidaModal = document.getElementById("modal-bebida");

    if (batataModal) {
        batataModal.addEventListener("change", atualizarPrecoModal);
    }

    if (bebidaModal) {
        bebidaModal.addEventListener("change", atualizarPrecoModal);
    }


    document.getElementById("confirmar-modal-combo")
        ?.addEventListener("click", confirmarCombo);

    document.getElementById("cancelar-modal-combo")
        ?.addEventListener("click", fecharModalCombo);

    document.getElementById("fechar-modal-combo")
        ?.addEventListener("click", fecharModalCombo);


    const modal = document.getElementById("modal-combo");

    if (modal) {

        modal.addEventListener("click", function (evento) {

            if (evento.target === modal) {
                fecharModalCombo();
            }

        });

    }


    // Tecla ESC fecha a janela
    document.addEventListener("keydown", function (evento) {

        if (evento.key === "Escape") {
            fecharModalCombo();
        }

    });


    // Limpar carrinho
    document.getElementById("limpar-carrinho")
        ?.addEventListener("click", limparCarrinho);


    // Finalizar pedido
    document.getElementById("finalizar-pedido")
        ?.addEventListener("click", finalizarPedido);


    mostrarCarrinho();

});


/* ========================================
   5. ABRIR JANELA DO COMBO
======================================== */

function abrirModalCombo(seletor) {

    const cartao = seletor.closest(".cardapio-item");
    const botao = cartao.querySelector(".botao-adicionar");

    const modal = document.getElementById("modal-combo");

    if (!modal || !botao) return;

    comboSelecionado = {
        id: Number(botao.dataset.id),
        nome: botao.dataset.nome,
        preco: Number(botao.dataset.preco),
        precoCombo: Number(botao.dataset.precoCombo),
        seletor: seletor
    };

    const nomeProduto = document.getElementById("modal-nome-produto");

    if (nomeProduto) {
        nomeProduto.textContent = comboSelecionado.nome;
    }

    // Valores iniciais
    document.getElementById("modal-batata").value = "Batata média";
    document.getElementById("modal-bebida").value = "Coca-Cola";

    atualizarPrecoModal();

    modal.hidden = false;

    document.body.style.overflow = "hidden";

}


/* ========================================
   6. FECHAR JANELA DO COMBO
======================================== */

function fecharModalCombo() {

    const modal = document.getElementById("modal-combo");

    if (!modal || modal.hidden) return;

    modal.hidden = true;

    document.body.style.overflow = "";

    // Cancela a seleção de combo
    if (comboSelecionado && comboSelecionado.seletor) {

        comboSelecionado.seletor.value = "individual";

    }

    comboSelecionado = null;

}


/* ========================================
   7. CALCULAR PREÇO DO COMBO
======================================== */

function calcularPrecoCombo(precoBase, batata, bebida) {

    const precoBatata = PRECO_BATATAS[batata];
    const precoBebida = PRECO_BEBIDAS[bebida];

    if (
        !Number.isFinite(precoBase) ||
        precoBatata === undefined ||
        precoBebida === undefined
    ) {
        return 0;
    }

    // O preço base inclui batata média e Coca-Cola.
    return precoBase + (precoBatata - 12) + (precoBebida - 8);

}


/* ========================================
   8. ATUALIZAR PREÇO DA JANELA
======================================== */

function atualizarPrecoModal() {

    if (!comboSelecionado) return;

    const batata = document.getElementById("modal-batata").value;
    const bebida = document.getElementById("modal-bebida").value;

    const preco = calcularPrecoCombo(
        comboSelecionado.precoCombo,
        batata,
        bebida
    );

    const elementoPreco = document.getElementById("modal-preco-combo");

    if (elementoPreco) {
        elementoPreco.textContent = formatarDinheiro(preco);
    }

}


/* ========================================
   9. CONFIRMAR COMBO
======================================== */

function confirmarCombo() {

    if (!comboSelecionado) return;

    const batata = document.getElementById("modal-batata").value;
    const bebida = document.getElementById("modal-bebida").value;

    const preco = calcularPrecoCombo(
        comboSelecionado.precoCombo,
        batata,
        bebida
    );

    const produto = {
        id: comboSelecionado.id,
        nome: comboSelecionado.nome,
        preco: preco,
        quantidade: 1,
        tipo: "combo",
        batata: batata,
        bebida: bebida
    };

    adicionarCarrinho(produto);

    fecharModalCombo();

}


/* ========================================
   10. ADICIONAR PRODUTOS AO CARRINHO
======================================== */

function adicionarCarrinho(
    produto
) {

    if (
        !Number.isInteger(produto.id) ||
        !produto.nome ||
        !Number.isFinite(produto.preco) ||
        produto.preco < 0
    ) {
        return;
    }

    const novoProduto = {
        ...produto,
        quantidade: 1
    };

    novoProduto.chave = criarChave(novoProduto);

    const produtoExistente = carrinho.find(
        item => item.chave === novoProduto.chave
    );

    if (produtoExistente) {

        produtoExistente.quantidade++;

    } else {

        carrinho.push(novoProduto);

    }

    salvarCarrinho();
    mostrarCarrinho();

}


/* ========================================
   11. MOSTRAR PRODUTOS NO CARRINHO
======================================== */

function mostrarCarrinho() {

    const container = document.getElementById("carrinho-itens");

    if (!container) return;

    container.innerHTML = "";

    if (carrinho.length === 0) {

        const mensagem = document.createElement("p");

        mensagem.textContent = "Seu carrinho está vazio!";

        container.appendChild(mensagem);

    } else {

        carrinho.forEach(produto => {

            const item = document.createElement("div");
            item.className = "item-carrinho";

            const nome = document.createElement("h3");

            nome.textContent = produto.tipo === "combo"
                ? "Combo " + produto.nome
                : produto.nome;

            const preco = document.createElement("p");

            preco.textContent =
                "Preço unitário: " + formatarDinheiro(produto.preco);

            item.appendChild(nome);

            // Detalhes do combo
            if (produto.tipo === "combo") {

                const detalhes = document.createElement("p");

                detalhes.textContent =
                    produto.batata + " + " + produto.bebida;

                item.appendChild(detalhes);

            }

            const quantidade = document.createElement("p");

            quantidade.className = "quantidade-produto";
            quantidade.textContent = "Quantidade: " + produto.quantidade;

            const subtotal = document.createElement("p");

            subtotal.className = "subtotal-produto";
            subtotal.textContent =
                "Subtotal: " +
                formatarDinheiro(produto.preco * produto.quantidade);

            const controles = document.createElement("div");

            controles.className = "controles-carrinho";

            const botaoDiminuir = document.createElement("button");

            botaoDiminuir.textContent = "−";

            botaoDiminuir.setAttribute(
                "aria-label",
                "Diminuir quantidade"
            );

            botaoDiminuir.addEventListener("click", () => {
                alterarQuantidade(produto.chave, -1);
            });

            const botaoAumentar = document.createElement("button");

            botaoAumentar.textContent = "+";

            botaoAumentar.setAttribute(
                "aria-label",
                "Aumentar quantidade"
            );

            botaoAumentar.addEventListener("click", () => {
                alterarQuantidade(produto.chave, 1);
            });

            const botaoRemover = document.createElement("button");

            botaoRemover.textContent = "Remover";
            botaoRemover.className = "botao-remover";

            botaoRemover.addEventListener("click", () => {
                removerProduto(produto.chave);
            });

            controles.appendChild(botaoDiminuir);
            controles.appendChild(botaoAumentar);
            controles.appendChild(botaoRemover);

            item.appendChild(preco);
            item.appendChild(quantidade);
            item.appendChild(subtotal);
            item.appendChild(controles);

            container.appendChild(item);

        });

    }

    atualizarTotal();

}


/* ========================================
   12. ALTERAR QUANTIDADE
======================================== */

function alterarQuantidade(chave, valor) {

    const produto = carrinho.find(
        item => item.chave === chave
    );

    if (!produto) return;

    produto.quantidade += valor;

    if (produto.quantidade <= 0) {

        removerProduto(chave);

        return;

    }

    salvarCarrinho();
    mostrarCarrinho();

}


/* ========================================
   13. REMOVER PRODUTO
======================================== */

function removerProduto(chave) {

    carrinho = carrinho.filter(
        produto => produto.chave !== chave
    );

    salvarCarrinho();
    mostrarCarrinho();

}


/* ========================================
   14. LIMPAR CARRINHO
======================================== */

function limparCarrinho() {

    carrinho = [];

    salvarCarrinho();
    mostrarCarrinho();

}


/* ========================================
   15. CALCULAR TOTAL
======================================== */

function atualizarTotal() {

    const elementoTotal = document.getElementById("carrinho-total");

    if (!elementoTotal) return;

    const total = carrinho.reduce((soma, produto) => {

        return soma + produto.preco * produto.quantidade;

    }, 0);

    elementoTotal.textContent = formatarDinheiro(total);

}


/* ========================================
   16. FORMATAR DINHEIRO
======================================== */

function formatarDinheiro(valor) {

    return valor.toLocaleString("pt-BR", {
        style: "currency",
        currency: "BRL"
    });

}


/* ========================================
   17. FINALIZAR PEDIDO
======================================== */

async function finalizarPedido() {

    if (finalizandoPedido) return;

    if (carrinho.length === 0) {

        alert("Seu carrinho está vazio!");

        return;

    }

    const botaoFinalizar = document.getElementById("finalizar-pedido");

    finalizandoPedido = true;

    if (botaoFinalizar) {

        botaoFinalizar.disabled = true;
        botaoFinalizar.textContent = "Finalizando...";

    }

    try {

        const resposta = await fetch("/finalizar-pedido", {

            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                itens: carrinho
            })

        });

        const resultado = await resposta.json();

        if (!resposta.ok) {

            throw new Error(
                resultado.erro || "Erro ao finalizar pedido."
            );

        }

        carrinho = [];

        salvarCarrinho();

        window.location.href = "/pedidos/" + resultado.pedido_id;

    } catch (erro) {

        alert(erro.message || "Não foi possível finalizar o pedido.");

        console.error(erro);

        finalizandoPedido = false;

        if (botaoFinalizar) {

            botaoFinalizar.disabled = false;
            botaoFinalizar.textContent = "Finalizar pedido";

        }

    }

}


