"""
Script de calibração do LIMIAR_PONTOS_MINIMO.

Como usar:
1. Coloque este arquivo na MESMA pasta do app.py e do ia.db.
2. Rode: python calibrar.py
   (vai demorar uns segundos pra carregar o modelo de IA, mesmo sem usá-lo,
   porque importar app.py executa esse carregamento também.)
3. Olhe a coluna de pontos: deve haver um "vão" entre as perguntas que
   DEVERIAM ser respondidas e as que DEVERIAM ser recusadas. O limiar
   fica nesse vão.

Edite PERGUNTAS_TESTE abaixo para incluir as perguntas que quiser testar
(as 5 do relatório já estão aqui como ponto de partida).
"""

from app import buscar_trechos_pdf, conectar, USUARIO_LOCAL_ID


# Cada item: (pergunta, o que deveria acontecer)
PERGUNTAS_TESTE = [
    (
        "Sou funcionário da produção e percebi que meu equipamento de "
        "proteção individual está danificado. Qual é a responsabilidade "
        "da empresa nessa situação?",
        "RESPONDER  (está na NR-06, item 6.5.1g)"
    ),
    (
        "Quais são minhas responsabilidades como trabalhador em relação "
        "ao uso, à conservação e à comunicação de problemas com o EPI?",
        "RESPONDER  (está na NR-06, item 6.6.1)"
    ),
    (
        "Como posso verificar se o EPI está regular em relação ao "
        "Certificado de Aprovação e quais informações devem estar "
        "identificadas no equipamento?",
        "RESPONDER  (está na NR-06, itens 6.9.2.1 e 6.9.3)"
    ),
    (
        "Qual é o procedimento interno para solicitar a substituição de "
        "luvas, quem autoriza a troca e quanto tempo o processo costuma "
        "levar?",
        "RECUSAR    (procedimento interno, não está na NR-06)"
    ),
    (
        "Quantos respiradores PFF2 há atualmente no estoque da empresa e "
        "qual é a marca dos equipamentos comprados?",
        "RECUSAR    (estoque/marca, não está na NR-06)"
    ),
    (
        "O que é EPI?",
        "RESPONDER  (definição básica, está no objetivo/glossário)"
    )
]


def main():
    conexao = conectar()

    documentos = conexao.execute(
        """
        SELECT id, nome, texto
        FROM documentos
        WHERE usuario_id = ?
        """,
        (USUARIO_LOCAL_ID,)
    ).fetchall()

    conexao.close()

    if not documentos:
        print(
            "Nenhum documento encontrado para o usuário local. "
            "Confirme se o ia.db usado é o mesmo onde o PDF da NR-06 "
            "foi enviado."
        )
        return

    print(f"{len(documentos)} documento(s) carregado(s).\n")

    resultados = []

    for pergunta, esperado in PERGUNTAS_TESTE:
        trechos = buscar_trechos_pdf(pergunta, documentos)
        melhor_pontuacao = trechos[0]["pontos"] if trechos else 0
        resultados.append((melhor_pontuacao, esperado, pergunta))

    resultados.sort(reverse=True)

    print(f"{'PONTOS':>7}  {'ESPERADO':<45}  PERGUNTA")
    print("-" * 110)

    for pontos, esperado, pergunta in resultados:
        print(f"{pontos:>7}  {esperado:<45}  {pergunta[:55]}")

    print(
        "\nProcure o maior valor entre as linhas RECUSAR e o menor valor "
        "entre as linhas RESPONDER. Se houver um vão limpo entre eles, "
        "coloque LIMIAR_PONTOS_MINIMO em algum ponto nesse vão.\n"
        "Se uma linha RECUSAR pontuar MAIS alto que uma linha RESPONDER, "
        "o limiar sozinho não resolve — nesse caso, ajuste os pesos em "
        "buscar_trechos_pdf (ex.: aumentar o peso por palavra encontrada) "
        "antes de fixar o número."
    )


if __name__ == "__main__":
    main()
