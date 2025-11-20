#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agente Proativo Claude LLM - Sistema Principal de Integração

Este arquivo integra todos os motores do agente proativo em uma
interface unificada e fácil de usar.

Classe principal: AgenteProativo
"""

from pathlib import Path
import json
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Importar todos os motores
from agent_proativo_core import ContextAnalysisEngine
from refinement_engine import RefinementEngine
from suggestions_engine import SuggestionsEngine
from pattern_detector import PatternDetector
from learning_loop import LearningLoop


class AgenteProativo:
    """
    Sistema principal do Agente Proativo Claude LLM.

    Integra todos os motores em uma interface unificada:
    - Análise contextual profunda
    - Refinamento automático de solicitações
    - Sugestões proativas inteligentes
    - Detecção de padrões de usuário
    - Aprendizado contínuo e feedback loop
    """

    def __init__(self, project_root: Path):
        """
        Inicializa o agente proativo completo.

        Args:
            project_root: Caminho para a raiz do projeto
        """
        self.project_root = project_root

        # Inicializar todos os motores
        print("🤖 Inicializando Agente Proativo...")
        self.context_engine = ContextAnalysisEngine(project_root)
        self.refinement_engine = RefinementEngine(project_root)
        self.suggestions_engine = SuggestionsEngine(project_root)
        self.pattern_detector = PatternDetector(project_root)
        self.learning_loop = LearningLoop(project_root)

        # Estado da sessão atual
        self.sessao_atual = []
        self.sessao_id = None

        print(f"✅ Agente Proativo inicializado em: {project_root}")

    def processar_solicitacao_completa(self, request: str, contexto_usuario: Dict = None) -> Dict[str, Any]:
        """
        Processa uma solicitação completa usando todos os motores do agente.

        Args:
            request: Solicitação do usuário
            contexto_usuario: Contexto adicional fornecido pelo usuário

        Returns:
            Resposta completa do agente proativo
        """

        print(f"\n🎯 Processando solicitação: '{request[:50]}...'")
        inicio_processamento = datetime.now()

        # 1. Iniciar ou recuperar sessão
        if not self.sessao_id:
            self.sessao_id = self._gerar_sessao_id()
            print(f"📋 Iniciando nova sessão: {self.sessao_id}")

        # 2. Análise Contextual Completa
        print("\n1️⃣ Realizando análise contextual...")
        analise_contextual = self.context_engine.analisar_contexto_completo(
            request, self.sessao_atual
        )

        # 3. Refinamento Automático
        print("2️⃣ Refinando solicitação...")
        refinamento = self.refinement_engine.refinar_solicitacao(
            request, analise_contextual
        )

        # 4. Geração de Sugestões Proativas
        print("3️⃣ Gerando sugestões proativas...")
        sugestoes = self.suggestions_engine.gerar_sugestoes_proativas(
            analise_contextual, refinamento
        )

        # 5. Detecção de Padrões (em background)
        print("4️⃣ Analisando padrões de comportamento...")
        analise_padroes = self.pattern_detector.analisar_padroes_sessao(self.sessao_atual)

        # 6. Construir Resposta Integrada
        resposta = self._construir_resposta_integrada(
            request, analise_contextual, refinamento, sugestoes, analise_padroes
        )

        # 7. Registrar evento na sessão
        self._registrar_evento_sessao(request, resposta, analise_contextual, refinamento, sugestoes)

        # 8. Calcular métricas de processamento
        duracao = (datetime.now() - inicio_processamento).total_seconds()
        resposta['metricas_processamento'] = {
            'duracao_total': duracao,
            'timestamp_inicio': inicio_processamento.isoformat(),
            'timestamp_fim': datetime.now().isoformat(),
            'sessao_id': self.sessao_id
        }

        print(f"✅ Processamento concluído em {duracao:.2f}s")
        return resposta

    def finalizar_sessao(self, feedback_usuario: Dict = None) -> Dict[str, Any]:
        """
        Finaliza a sessão atual e processa aprendizado.

        Args:
            feedback_usuario: Feedback explícito do usuário (opcional)

        Returns:
            Resumo da sessão e resultados do aprendizado
        """

        if not self.sessao_id:
            return {"erro": "Nenhuma sessão ativa para finalizar"}

        print(f"\n🏁 Finalizando sessão: {self.sessao_id}")

        # 1. Preparar dados completos da sessão
        dados_sessao = {
            'sessao_id': self.sessao_id,
            'timestamp_inicio': self.sessao_atual[0]['timestamp'] if self.sessao_atual else datetime.now().isoformat(),
            'timestamp_fim': datetime.now().isoformat(),
            'total_interacoes': len(self.sessao_atual),
            'eventos': self.sessao_atual,
            'feedback_usuario': feedback_usuario,
            'duracao_total': self._calcular_duracao_sessao()
        }

        # 2. Processar aprendizado completo
        print("📚 Processando aprendizado da sessão...")
        resultado_aprendizado = self.learning_loop.registrar_interacao_completa(
            self.sessao_id, dados_sessao
        )

        # 3. Gerar relatório final
        relatorio = self._gerar_relatorio_final(dados_sessao, resultado_aprendizado)

        # 4. Limpar estado da sessão
        self._limpar_sessao()

        print("✅ Sessão finalizada e aprendizado processado")
        return relatorio

    def _construir_resposta_integrada(self, request: str, analise: Dict, refinamento: Dict,
                                   sugestoes: List, padroes: Dict) -> Dict[str, Any]:
        """
        Constrói resposta integrada formatada para o usuário.

        Args:
            request: Solicitação original
            analise: Análise contextual completa
            refinamento: Refinamento realizado
            sugestoes: Sugestões geradas
            padroes: Análise de padrões

        Returns:
            Resposta integrada e formatada
        """

        resposta = {
            'status': 'sucesso',
            'solicitacao_original': request,
            'sessao_id': self.sessao_id,
            'secoes': []
        }

        # 1. Seção de Entendimento
        secao_entendimento = {
            'titulo': '📋 Entendido sua solicitação',
            'conteudo': f"Vou {self._formatar_acao_principal(analise)}",
            'detalhes': self._gerar_detalhes_entendimento(analise, refinamento)
        }
        resposta['secoes'].append(secao_entendimento)

        # 2. Seção de Análise Contextual
        if analise.get('solucoes_existentes') or analise.get('ambiguidade', {}).get('total_ambiguidades', 0) > 0:
            secao_contexto = {
                'titulo': '🔍 Análise Contextual',
                'conteudo': self._formatar_analise_contextual(analise),
                'detalhes': []
            }

            if analise.get('solucoes_existentes'):
                secao_contexto['detalhes'].append(f"✅ Encontrei {len(analise['solucoes_existentes'])} soluções similares")

            if analise.get('ambiguidade', {}).get('total_ambiguidades', 0) > 0:
                secao_contexto['detalhes'].append(f"⚠️ Detectei {analise['ambiguidade']['total_ambiguidades']} pontos que precisam clarificação")

            resposta['secoes'].append(secao_contexto)

        # 3. Seção de Refinamento
        if refinamento.get('nivel_refinamento') in ['medio', 'alto']:
            secao_refinamento = {
                'titulo': '🔧 Solicitação Refinada',
                'conteudo': refinamento.get('request_refinado', request),
                'melhorias': []
            }

            if refinamento.get('ambiguidades'):
                secao_refinamento['melhorias'].append(f"Resolvi {len(refinamento['ambiguidades'])} ambiguidades")

            if refinamento.get('especificacoes'):
                secao_refinamento['melhorias'].append(f"Adicionei {len(refinamento['especificacoes'])} especificações")

            resposta['secoes'].append(secao_refinamento)

        # 4. Seção de Sugestões Proativas
        if sugestoes:
            secao_sugestoes = {
                'titulo': '💡 Sugestões Proativas',
                'sugestoes': []
            }

            for i, sugestao in enumerate(sugestoes[:3], 1):  # Top 3 sugestões
                secao_sugestoes['sugestoes'].append({
                    'numero': i,
                    'mensagem': sugestao.get('mensagem', ''),
                    'acoes': [acao.get('descricao', '') for acao in sugestao.get('acoes', [])[:2]],
                    'prioridade': sugestao.get('prioridade', 'media')
                })

            resposta['secoes'].append(secao_sugestoes)

        # 5. Seção de Plano de Ação
        if refinamento.get('plano_acao'):
            secao_plano = {
                'titulo': '🎯 Plano de Ação',
                'passos': []
            }

            for i, passo in enumerate(refinamento['plano_acao'], 1):
                secao_plano['passos'].append({
                    'numero': i,
                    'descricao': passo.get('descricao', ''),
                    'prioridade': passo.get('prioridade', 'media')
                })

            resposta['secoes'].append(secao_plano)

        # 6. Seção de Padrões Detectados
        if padroes.get('padroes_consolidados'):
            secao_padroes = {
                'titulo': '🎨 Padrões Detectados',
                'padroes': []
            }

            for padrao in padroes['padroes_consolidados'][:2]:  # Top 2 padrões
                secao_padroes['padroes'].append({
                    'tipo': padrao.get('tipo', ''),
                    'descricao': padrao.get('descricao', ''),
                    'confianca': padrao.get('confianca', 0)
                })

            resposta['secoes'].append(secao_padroes)

        # 7. Seção de Próximos Passos
        resposta['secoes'].append({
            'titulo': '➡️ Próximos Passos',
            'opcoes': [
                "Posso começar a executar o plano de ação agora",
                "Você prefere ajustar algo antes de começar?",
                "Quer mais detalhes sobre alguma sugestão específica?",
                "Posso finalizar a sessão e registrar o aprendizado"
            ]
        })

        return resposta

    def _gerar_sessao_id(self) -> str:
        """Gera ID único para a sessão."""
        import hashlib
        import time
        timestamp = str(time.time())
        return hashlib.md5(timestamp.encode()).hexdigest()[:12]

    def _registrar_evento_sessao(self, request: str, resposta: Dict, analise: Dict, refinamento: Dict, sugestoes: List):
        """Registra evento na sessão atual."""
        evento = {
            'timestamp': datetime.now().isoformat(),
            'request': request,
            'resumo_resposta': {
                'sugestoes_geradas': len(sugestoes),
                'nivel_refinamento': refinamento.get('nivel_refinamento'),
                'ambiguidades_resolvidas': len(refinamento.get('ambiguidades', [])),
                'solucoes_encontradas': len(analise.get('solucoes_existentes', []))
            },
            'analise_contextual': analise,
            'refinamento': refinamento,
            'sugestoes': sugestoes
        }

        self.sessao_atual.append(evento)

    def _formatar_acao_principal(self, analise: Dict) -> str:
        """Formata a ação principal baseada na análise."""
        entidades = analise.get('entidades', {})
        acoes = entidades.get('acoes', [])
        recursos = entidades.get('recursos', [])

        if acoes and recursos:
            return f"{acoes[0]} {recursos[0]}"
        elif acoes:
            return f"{acoes[0]} o que você solicitou"
        else:
            return "ajudar com sua solicitação"

    def _gerar_detalhes_entendimento(self, analise: Dict, refinamento: Dict) -> List[str]:
        """Gera detalhes do entendimento."""
        detalhes = []

        # Entidades detectadas
        entidades = analise.get('entidades', {})
        if any(entidades.values()):
            detalhes.append("Identifiquei os seguintes elementos:")
            for tipo, itens in entidades.items():
                if itens:
                    detalhes.append(f"  • {tipo.title()}: {', '.join(itens[:3])}")

        # Nível de confiança
        confianca = analise.get('confidence_score', 0)
        if confianca > 0.8:
            detalhes.append(f"✅ Alta confiança na análise ({confianca:.0%})")
        elif confianca > 0.5:
            detalhes.append(f"⚠️ Confiança média na análise ({confianca:.0%})")
        else:
            detalhes.append(f"❌ Baixa confiança - posso precisar de mais informações")

        # Se há refinamento
        if refinamento.get('nivel_refinamento') == 'alto':
            detalhes.append("🔧 Refinamento significativo foi aplicado para clareza")

        return detalhes

    def _formatar_analise_contextual(self, analise: Dict) -> str:
        """Formata a análise contextual de forma legível."""
        partes = []

        if analise.get('solucoes_existentes'):
            partes.append(f"Encontrei {len(analise['solucoes_existentes'])} soluções similares já documentadas")

        if analise.get('ambiguidade', {}).get('nivel_geral') == 'alto':
            partes.append("Sua solicitação tem várias ambiguidades que precisam ser esclarecidas")
        elif analise.get('ambiguidade', {}).get('nivel_geral') == 'medio':
            partes.append("Sua solicitação tem algumas pontos que podem ser mais específicos")

        if analise.get('proatividade_necessaria'):
            partes.append("Identifiquei oportunidades de melhorias proativas")

        return ". ".join(partes) if partes else "Análise contextual concluída com sucesso"

    def _calcular_duracao_sessao(self) -> float:
        """Calcula duração total da sessão em segundos."""
        if not self.sessao_atual:
            return 0.0

        inicio = datetime.fromisoformat(self.sessao_atual[0]['timestamp'])
        fim = datetime.now()
        return (fim - inicio).total_seconds()

    def _gerar_relatorio_final(self, dados_sessao: Dict, resultado_aprendizado: Dict) -> Dict[str, Any]:
        """Gera relatório final da sessão."""
        return {
            'sessao_id': dados_sessao['sessao_id'],
            'resumo': {
                'total_interacoes': dados_sessao['total_interacoes'],
                'duracao_total': dados_sessao['duracao_total'],
                'eficacia_geral': resultado_aprendizado.get('eficacia_geral', 0),
                'score_feedback': resultado_aprendizado.get('feedback_coletado', {}).get('score_geral', 0)
            },
            'aprendizado': resultado_aprendizado.get('insights_gerados', []),
            'metricas': resultado_aprendizado.get('metricas_atualizadas', {}),
            'status': 'sessao_finalizada'
        }

    def _limpar_sessao(self):
        """Limpa o estado da sessão atual."""
        self.sessao_atual = []
        self.sessao_id = None

    def exibir_resposta_formatada(self, resposta: Dict):
        """Exibe resposta de forma formatada e amigável."""
        print("\n" + "="*60)
        print(f"🤖 Agente Proativo - Sessão {resposta['sessao_id']}")
        print("="*60)

        for secao in resposta['secoes']:
            print(f"\n{secao['titulo']}")
            print("-" * len(secao['titulo']))
            print(secao['conteudo'])

            if 'detalhes' in secao and secao['detalhes']:
                for detalhe in secao['detalhes']:
                    print(f"  {detalhe}")

            if 'melhorias' in secao and secao['melhorias']:
                print("\n🔧 Melhorias aplicadas:")
                for melhoria in secao['melhorias']:
                    print(f"  • {melhoria}")

            if 'sugestoes' in secao:
                for sugestao in secao['sugestoes']:
                    print(f"\n{sugestao['numero']}. {sugestao['mensagem']}")
                    for acao in sugestao['acoes']:
                        if acao:
                            print(f"   → {acao}")

            if 'passos' in secao:
                for passo in secao['passos']:
                    prioridade_icon = "🔴" if passo['prioridade'] == 'alta' else "🟡" if passo['prioridade'] == 'media' else "🟢"
                    print(f"  {passo['numero']}. {prioridade_icon} {passo['descricao']}")

            if 'padroes' in secao:
                for padrao in secao['padroes']:
                    confianca_icon = "✅" if padrao['confianca'] > 0.7 else "⚠️" if padrao['confianca'] > 0.4 else "❌"
                    print(f"  • {confianca_icon} {padrao['descricao']} ({padrao['tipo']})")

            if 'opcoes' in secao:
                for i, opcao in enumerate(secao['opcoes'], 1):
                    print(f"  {i}. {opcao}")

        print("\n" + "="*60)
        print(f"⏱️ Processado em {resposta['metricas_processamento']['duracao_total']:.2f}s")
        print("="*60)


def main():
    """Função principal para demonstração do agente proativo."""
    project_root = Path(__file__).parent.parent.parent.parent

    # Inicializar agente
    agente = AgenteProativo(project_root)

    print("🚀 Agente Proativo Claude LLM - Demonstração")
    print("="*50)

    # Exemplos de solicitações para teste
    solicitacoes_teste = [
        "fazer o odoo funcionar direito no servidor",
        "preciso configurar odoo mas não sei bem como",
        "tem erro no odoo de produção que preciso resolver urgente",
        "queria criar um módulo customizado para sms"
    ]

    for i, request in enumerate(solicitacoes_teste, 1):
        print(f"\n\n📝 Teste {i}: {request}")
        print("-" * (len(request) + 10))

        # Processar solicitação
        resposta = agente.processar_solicitacao_completa(request)

        # Exibir resposta formatada
        agente.exibir_resposta_formatada(resposta)

        # Pausar entre testes
        if i < len(solicitacoes_teste):
            input("\nPressione Enter para continuar com o próximo teste...")

    # Finalizar sessão
    print("\n\n🏁 Finalizando demonstração...")
    feedback_final = {
        'satisfacao': 0.9,
        'utilidade': 0.8,
        'comentarios': 'Demonstração muito útil e clara!'
    }

    relatorio_final = agente.finalizar_sessao(feedback_final)

    print("\n📊 Relatório Final da Sessão:")
    print(json.dumps(relatorio_final, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()