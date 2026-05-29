"""CLI do agente especialista.

Fluxo:
1. carrega o `.env`;
2. escolhe o provedor (Groq auditado se houver chave; senão, modo offline);
3. instancia o agente geral (responde Tecnologia e Direito Digital/LGPD);
4. loop de conversa com alguns comandos especiais;
5. ao sair, imprime um resumo usando os dunders do agente/conversa.
"""

from __future__ import annotations

import json
import os

from dotenv import load_dotenv

from agentes import AgenteBase, AgenteGeral
from provedores import ErroDoProvedor, ProvedorFake, ProvedorGroqAuditado


def escolher_provedor():
    """Decide entre o Groq (online, auditado) e o provedor offline."""
    load_dotenv()
    if os.environ.get("GROQ_API_KEY"):
        try:
            provedor = ProvedorGroqAuditado()
            print("Provedor: Groq (online, com trilha de auditoria).\n")
            return provedor
        except ErroDoProvedor as erro:
            print(f"Aviso: {erro}")
    print("Provedor: modo offline (ProvedorFake) — sem internet.\n")
    return ProvedorFake()


def salvar_historico(agente: AgenteBase, caminho: str = "historico.json") -> None:
    """Serializa o histórico em JSON (metadados + conteúdo de cada mensagem)."""
    dados = [
        {
            "papel": m.papel,
            "conteudo": m.conteudo,
            "criada_em": m.criada_em.isoformat(),
        }
        for m in agente._historico
    ]
    with open(caminho, "w", encoding="utf-8") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
    print(f"Histórico salvo em {caminho} ({len(dados)} mensagens).")


def mostrar_mro(agente: AgenteBase) -> None:
    """Demonstra a ordem de resolução de métodos (MRO)."""
    print("\nMRO do agente:")
    for classe in type(agente).__mro__:
        print(f"  - {classe.__name__}")
    print("MRO do provedor:")
    for classe in type(agente._provedor).__mro__:
        print(f"  - {classe.__name__}")
    print()


def mostrar_auditoria(agente: AgenteBase) -> None:
    """Imprime a trilha de auditoria, se o provedor for auditado."""
    registros = getattr(agente._provedor, "registros", None)
    if not registros:
        print("Sem trilha de auditoria (provedor offline ou nenhuma chamada ainda).\n")
        return
    print("\nTrilha de auditoria:")
    for linha in registros:
        print(f"  - {linha}")
    print()


def imprimir_resumo(agente: AgenteBase) -> None:
    """Resumo final usando os dunders."""
    print("\n--- Resumo da sessão ---")
    print(str(agente))
    print(f"{len(agente)} mensagens trocadas:")
    print(agente._historico)


def main() -> None:
    provedor = escolher_provedor()
    agente = AgenteGeral(provedor)
    print(f"\n{agente}. Digite sua pergunta (ou 'sair' para encerrar).")
    print("Comandos: sair | salvar | mro | auditoria\n")

    while True:
        try:
            entrada = input("você> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not entrada:
            continue

        comando = entrada.lower()
        if comando == "sair":
            break
        if comando == "salvar":
            salvar_historico(agente)
            continue
        if comando == "mro":
            mostrar_mro(agente)
            continue
        if comando == "auditoria":
            mostrar_auditoria(agente)
            continue

        try:
            resposta = agente.responder(entrada)
        except ErroDoProvedor as erro:
            print(f"[erro] {erro}\n")
            continue
        print(f"{agente.nome}> {resposta}\n")

    imprimir_resumo(agente)


if __name__ == "__main__":
    main()