#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Refinamento Automático - Agente Proativo Claude LLM

Este motor implementa o refinamento inteligente de solicitações do usuário,
detectando intenções reais, removendo ambiguidades e sugerindo melhorias.

Classe principal: RefinementEngine
"""

from pathlib import Path
import json
import re
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_logger = logging.getLogger(__name__)


class RefinementEngine:
    """
    Motor principal para refinamento automático de solicitações.

    Implementa:
    - Detecção de ambiguidades
    - Sugestão de especificações faltantes
    - Oferta de alternativas melhores
    - Antecipação de necessidades adicionais
    - Geração de solicitação refinada
    """

    def __init__(self, project_root: Path):
        """
        Inicializa o motor de refinamento.

        Args:
            project_root: Caminho para a raiz do projeto
        """
        self.project_root = project_root
        self.memory_path = project_root / ".claude" / "memory"

        # Carregar templates de refinamento
        self.templates = self._load_refinement_templates()

        # Cache para refinamentos recentes
        self._refinement_cache = {}

        # Mapeamento de intenções para perguntas de refinamento
        self.mapeamento_refinamento = {
            'configurar': {
                'perguntas': [
                    'O que exatamente você quer configurar?',
                    'Qual é o estado atual da configuração?',
                    'Existe algum requisito específico?'
                ],
                'especificacoes': ['componente', 'estado_atual', 'requisitos'],
                'alternativas': ['instalar', 'verificar_status', 'atualizar']
            },
            'reiniciar': {
                'perguntas': [
                    'Qual serviço você quer reiniciar?',
                    'Você já tentou outras soluções?',
                    'Existe risco em reiniciar agora?'
                ],
                'especificacoes': ['servico', 'motivo', 'risco'],
                'alternativas': ['reload', 'restart_graceful', 'verificar_status']
            },
            'resolver': {
                'perguntas': [
                    'Qual é o erro exato que está ocorrendo?',
                    'Quando o problema começou?',
                    'O que você já tentou fazer?'
                ],
                'especificacoes': ['erro', 'contexto', 'tentativas_anteriores'],
                'alternativas': ['debug', 'investigar_logs', 'procurar_solucoes_similares']
            },
            'criar': {
                'perguntas': [
                    'O que você quer criar?',
                    'Quais são os requisitos?',
                    'Existe algum modelo ou exemplo a seguir?'
                ],
                'especificacoes': ['tipo_objeto', 'requisitos', 'referencia'],
                'alternativas': ['usar_template', 'basear_existente', 'prototipo_simples']
            }
        }

        # Padrões para detectar verbos genéricos
        self.verbos_genericos = {
            'fazer': ['criar', 'implementar', 'configurar', 'executar'],
            'ajustar': ['configurar', 'modificar', 'otimizar', 'calibrar'],
            'mexer': ['configurar', 'modificar', 'ajustar', 'otimizar'],
            'ver': ['verificar', 'consultar', 'analisar', 'exibir'],
            'arrumar': ['resolver', 'corrigir', 'consertar', 'reparar']
        }

    def refinar_solicitacao(self, request_original: str, analise_contextual: Dict[str, Any]) -> Dict[str, Any]:
        """
        Refina solicitação do usuário para ser mais específica e acionável.

        Args:
            request_original: Solicitação original do usuário
            analise_contextual: Análise completa do contexto

        Returns:
            Dicionário com refinamento completo da solicitação
        """

        _logger.info(f"🔧 Refinando solicitação: '{request_original[:50]}...'")

        # 1. Detectar ambiguidades na solicitação
        ambiguidades = self._detectar_ambiguidades(request_original, analise_contextual)

        # 2. Sugerir especificações que faltam
        especificacoes = self._sugerir_especificacoes_faltantes(request_original, analise_contextual)

        # 3. Oferecer alternativas melhores
        alternativas = self._sugerir_alternativas_melhores(request_original, analise_contextual)

        # 4. Antecipar necessidades adicionais
        necessidades_adicionais = self._antecipar_necessidades_adicionais(request_original, analise_contextual)

        # 5. Construir versão refinada do request
        request_refinado = self._construir_request_refinado(
            request_original, ambiguidades, especificacoes, alternativas, necessidades_adicionais
        )

        # 6. Gerar plano de ação refinado
        plano_acao = self._gerar_plano_acao_refinado(request_refinado, analise_contextual)

        # 7. Calcular métricas de refinamento
        metricas = self._calcular_metricas_refinamento(request_original, request_refinado, analise_contextual)

        refinamento = {
            'request_original': request_original,
            'request_refinado': request_refinado,
            'ambiguidades': ambiguidades,
            'especificacoes': especificacoes,
            'alternativas': alternativas,
            'necessidades_adicionais': necessidades_adicionais,
            'plano_acao': plano_acao,
            'metricas': metricas,
            'timestamp': datetime.now().isoformat(),
            'confianca_refinamento': metricas.get('confianca', 0.0),
            'nivel_refinamento': metricas.get('nivel', 'medio')
        }

        # Cache do refinamento
        self._cache_refinamento(request_original, refinamento)

        _logger.info(f"✅ Refinamento concluído - Nível: {refinamento['nivel_refinamento']}, Confiança: {refinamento['confianca_refinamento']:.2f}")

        return refinamento

    def _detectar_ambiguidades(self, request: str, analise: Dict) -> List[Dict[str, Any]]:
        """
        Detecta ambiguidades na solicitação do usuário.

        Args:
            request: Solicitação original
            analise: Análise contextual completa

        Returns:
            Lista de ambiguidades detectadas
        """

        ambiguidades = []

        # 1. Verbos genéricos sem contexto
        for generico, especificos in self.verbos_genericos.items():
            if generico in request.lower():
                ambiguidades.append({
                    'tipo': 'verbo_generico',
                    'termo': generico,
                    'possibilidades': especificos,
                    'pergunta_sugestao': f'Quando você diz "{generico}", você quer dizer {", ".join(especificos[:3])}?',
                    'impacto': 'alto',
                    'prioridade': 1
                })

        # 2. Múltiplos alvos sem especificação
        entidades = analise.get('entidades', {})
        if len(entidades.get('recursos', [])) > 1:
            ambiguidades.append({
                'tipo': 'multiplos_alvos',
                'alvos': entidades.get('recursos', [])[:3],
                'pergunta_sugestao': f'Qual destes recursos você quer focar: {", ".join(entidades.get("recursos", [])[:3])}?',
                'impacto': 'medio',
                'prioridade': 2
            })

        # 3. Falta de especificações críticas
        if 'configurar' in request.lower():
            if not any(palavra in request.lower() for palavra in ['banco', 'database', 'db']):
                if 'odoo' in request.lower():
                    ambiguidades.append({
                        'tipo': 'especificacao_faltante',
                        'campo': 'database_config',
                        'pergunta_sugestao': 'Qual banco de dados você quer configurar?',
                        'impacto': 'alto',
                        'prioridade': 1
                    })

        # 4. Referências vagas
        referencias_vagas = ['isso', 'aquilo', 'coisa', 'o negócio']
        for referencia in referencias_vagas:
            if referencia in request.lower():
                ambiguidades.append({
                    'tipo': 'referencia_vaga',
                    'termo': referencia,
                    'pergunta_sugestao': f'Ao dizer "{referencia}", o que exatamente você se refere?',
                    'impacto': 'alto',
                    'prioridade': 1
                })

        # 5. Contexto faltante
        if len(request.split()) < 5:
            ambiguidades.append({
                'tipo': 'pouco_contexto',
                'pergunta_sugestao': 'Poderia dar mais detalhes sobre o que você precisa?',
                'impacto': 'medio',
                'prioridade': 2
            })

        # Ordenar por prioridade
        ambiguidades.sort(key=lambda x: x['prioridade'])
        return ambiguidades

    def _sugerir_especificacoes_faltantes(self, request: str, analise: Dict) -> List[Dict[str, Any]]:
        """
        Sugere especificações que estão faltando na solicitação.

        Args:
            request: Solicitação original
            analise: Análise contextual

        Returns:
            Lista de especificações sugeridas
        """

        especificacoes = []

        # 1. Para configurações - ambiente
        if 'configurar' in request.lower():
            if not any(amb in request.lower() for amb in ['testing', 'producao', 'dev', 'homologacao']):
                especificacoes.append({
                    'campo': 'ambiente',
                    'tipo': 'selecao',
                    'opcoes': ['testing', 'produção', 'development'],
                    'padrao': 'testing',
                    'pergunta': 'Em qual ambiente você quer fazer esta configuração?',
                    'importancia': 'alta'
                })

        # 2. Para restart - serviço específico
        if 'reiniciar' in request.lower():
            if not any(svc in request.lower() for svc in ['odoo', 'nginx', 'postgres', 'postgresql']):
                especificacoes.append({
                    'campo': 'servico',
                    'tipo': 'selecao',
                    'opcoes': ['Odoo', 'Nginx', 'PostgreSQL', 'Todos'],
                    'padrao': 'Odoo',
                    'pergunta': 'Qual serviço você quer reiniciar?',
                    'importancia': 'critica'
                })

        # 3. Para problemas - logs/erros
        if any(palavra in request.lower() for palavra in ['erro', 'problema', 'bug', 'não funciona']):
            if 'log' not in request.lower():
                especificacoes.append({
                    'campo': 'fonte_erro',
                    'tipo': 'texto',
                    'pergunta': 'Você pode mostrar o erro ou mensagem de log?',
                    'importancia': 'alta'
                })

        # 4. Para instalação - versão/source
        if 'instalar' in request.lower():
            especificacoes.append({
                'campo': 'fonte_instalacao',
                'tipo': 'selecao',
                'opcoes': ['Repositório Oficial', 'GitHub', 'PPA', 'Source'],
                'padrao': 'Repositório Oficial',
                'pergunta': 'De onde você quer instalar?',
                'importancia': 'media'
            })

        # 5. Baseado no contexto recente
        contexto_session = analise.get('contexto_session', {})
        if contexto_session.get('erros_recentes'):
            especificacoes.append({
                'campo': 'relacao_erro_anterior',
                'tipo': 'confirmacao',
                'pergunta': 'Isso está relacionado ao erro que encontramos anteriormente?',
                'importancia': 'media'
            })

        return especificacoes

    def _sugerir_alternativas_melhores(self, request: str, analise: Dict) -> List[Dict[str, Any]]:
        """
        Oferece alternativas melhores para a solicitação.

        Args:
            request: Solicitação original
            analise: Análise contextual

        Returns:
            Lista de alternativas sugeridas
        """

        alternativas = []

        # 1. Para verbos genéricos - alternativas específicas
        for generico, especificos in self.verbos_genericos.items():
            if generico in request.lower():
                for especifico in especificos[:3]:  # Top 3 alternativas
                    alternativas.append({
                        'tipo': 'substituicao_verbo',
                        'original': generico,
                        'sugestao': especifico,
                        'request_modificado': request.lower().replace(generico, especifico),
                        'justificativa': f'"{especifico}" é mais específico que "{generico}"',
                        'impacto': 'alto'
                    })

        # 2. Se há soluções similares conhecidas
        solucoes_existentes = analise.get('solucoes_existentes', [])
        if solucoes_existentes:
            for solucao in solucoes_existentes[:2]:  # Top 2 soluções
                alternativas.append({
                    'tipo': 'solucao_conhecida',
                    'titulo': solucao.get('titulo', 'Solução Similar'),
                    'descricao': solucao.get('descricao', 'Já resolvemos algo similar'),
                    'similaridade': solucao.get('similaridade', 0),
                    'justificativa': f'Solução {solucao.get("similaridade", 0):.0%} similar',
                    'impacto': 'medio'
                })

        # 3. Para tarefas manuais - sugestão de automação
        if any(palavra in request.lower() for palavra in ['manualmente', 'a mão', 'passo a passo']):
            alternativas.append({
                'tipo': 'automacao',
                'sugestao': 'Criar script/automação',
                'justificativa': 'Esta tarefa pode ser automatizada para economizar tempo futuro',
                'impacto': 'medio'
            })

        # 4. Para acesso direto - sugestão de verificação
        if any(palavra in request.lower() for palavra in ['acessar', 'entrar', 'conectar']):
            alternativas.append({
                'tipo': 'verificacao_previa',
                'sugestao': 'Verificar status antes de acessar',
                'justificativa': 'Evitar tentativas de acesso a serviços offline',
                'impacto': 'baixo'
            })

        # 5. Baseado em padrões do usuário
        padroes_usuario = analise.get('padroes_usuario', [])
        for padrao in padroes_usuario:
            if padrao.get('tipo') == 'preferencia_automacao' and padrao.get('aplicavel'):
                alternativas.append({
                    'tipo': 'padrao_usuario',
                    'sugestao': 'Usar automação baseada em seu padrão',
                    'justificativa': 'Você geralmente prefere soluções automatizadas',
                    'impacto': 'medio'
                })

        return alternativas

    def _antecipar_necessidades_adicionais(self, request: str, analise: Dict) -> List[Dict[str, Any]]:
        """
        Antecipa necessidades adicionais não mencionadas pelo usuário.

        Args:
            request: Solicitação original
            analise: Análise contextual

        Returns:
            Lista de necessidades adicionais antecipadas
        """

        necessidades = []

        # 1. Para alterações em produção - backup
        if 'producao' in request.lower():
            necessidades.append({
                'tipo': 'seguranca',
                'necessidade': 'backup',
                'descricao': 'Fazer backup antes de alterações em produção',
                'prioridade': 'critica',
                'pergunta': 'Você fez backup antes de fazer alterações em produção?',
                'impacto': 'alto'
            })

        # 2. Para configurações - restart
        if 'configurar' in request.lower():
            necessidades.append({
                'tipo': 'operacional',
                'necessidade': 'restart',
                'descricao': 'Provavelmente precisará reiniciar o serviço após configuração',
                'prioridade': 'media',
                'pergunta': 'Você sabe que precisará reiniciar o serviço?',
                'impacto': 'medio'
            })

        # 3. Para debugging - logs
        if 'debug' in request.lower() or 'investigar' in request.lower():
            necessidades.append({
                'tipo': 'informacao',
                'necessidade': 'logs',
                'descricao': 'Precisará acessar logs para investigação',
                'prioridade': 'alta',
                'pergunta': 'Você tem acesso aos logs do sistema?',
                'impacto': 'medio'
            })

        # 4. Para instalações - dependências
        if 'instalar' in request.lower():
            necessidades.append({
                'tipo': 'dependencias',
                'necessidade': 'dependencias',
                'descricao': 'Verificar dependências necessárias antes da instalação',
                'prioridade': 'media',
                'pergunta': 'Você verificou todas as dependências necessárias?',
                'impacto': 'medio'
            })

        # 5. Para acesso remoto - conectividade
        if any(palavra in request.lower() for palavra in ['ssh', 'remoto', 'servidor']):
            necessidades.append({
                'tipo': 'conectividade',
                'necessidade': 'verificar_conexao',
                'descricao': 'Verificar conectividade com o servidor antes de prosseguir',
                'prioridade': 'alta',
                'pergunta': 'Você testou a conexão com o servidor?',
                'impacto': 'alto'
            })

        # 6. Baseado em erros recentes
        contexto_session = analise.get('contexto_session', {})
        if contexto_session.get('erros_recentes'):
            necessidades.append({
                'tipo': 'prevencao',
                'necessidade': 'verificacao_erros',
                'descricao': 'Verificar se o erro anterior pode afetar esta operação',
                'prioridade': 'media',
                'impacto': 'medio'
            })

        return necessidades

    def _construir_request_refinado(self, request_original: str, ambiguidades: List,
                                   especificacoes: List, alternativas: List, necessidades: List) -> str:
        """
        Constrói uma versão refinada da solicitação.

        Args:
            request_original: Solicitação original
            ambiguidades: Ambiguidades detectadas
            especificacoes: Especificações sugeridas
            alternativas: Alternativas melhores
            necessidades: Necessidades adicionais

        Returns:
            Solicitação refinada
        """

        request_refinado = request_original

        # 1. Substituir verbos genéricos se houver alternativas
        if ambiguidades:
            for ambiguidade in ambiguidades:
                if ambiguidade['tipo'] == 'verbo_generico' and alternativas:
                    # Usar primeira alternativa de maior impacto
                    alt_relevante = next((alt for alt in alternativas
                                        if alt['tipo'] == 'substituicao_verbo' and
                                        alt['original'] == ambiguidade['termo']), None)
                    if alt_relevante:
                        request_refinado = request_refinado.replace(
                            ambiguidade['termo'], alt_relevante['sugestao']
                        )

        # 2. Adicionar especificações críticas
        if especificacoes:
            especificacoes_criticas = [esp for esp in especificacoes if esp.get('importancia') == 'critica']
            for esp in especificacoes_criticas:
                if esp['tipo'] == 'selecao' and esp.get('padrao'):
                    # Adicionar especificação padrão
                    if esp['campo'] == 'servico' and 'reiniciar' in request_refinado.lower():
                        request_refinado += f" ({esp['padrao']})"
                    elif esp['campo'] == 'ambiente' and 'configurar' in request_refinado.lower():
                        request_refinado += f" no ambiente {esp['padrao']}"

        # 3. Adicionar contexto de prevenção se necessário
        if necessidades:
            necessidades_criticas = [nec for nec in necessidades if nec.get('prioridade') == 'critica']
            if necessidades_criticas:
                request_refinado += " (com verificação de segurança)"

        # 4. Formatar para clareza
        request_refinado = self._formatar_request_para_clareza(request_refinado)

        return request_refinado

    def _formatar_request_para_clareza(self, request: str) -> str:
        """
        Formata o request para melhor clareza.

        Args:
            request: Request a ser formatado

        Returns:
            Request formatado
        """

        # Capitalizar primeira letra
        request = request.strip()
        if request:
            request = request[0].upper() + request[1:]

        # Remover espaços múltiplos
        request = re.sub(r'\s+', ' ', request)

        # Adicionar ponto final se não tiver
        if request and not request.endswith('.'):
            request += '.'

        return request

    def _gerar_plano_acao_refinado(self, request_refinado: str, analise: Dict) -> List[Dict[str, Any]]:
        """
        Gera um plano de ação baseado no request refinado.

        Args:
            request_refinado: Solicitação refinada
            analise: Análise contextual completa

        Returns:
            Plano de ação estruturado
        """

        plano = []

        # 1. Passos de verificação (sempre incluídos)
        if any(palavra in request_refinado.lower() for palavra in ['servidor', 'remoto', 'acessar']):
            plano.append({
                'etapa': 'verificacao',
                'descricao': 'Verificar conectividade com o servidor',
                'comando': 'ping ou curl',
                'prioridade': 1,
                'tipo': 'preparacao'
            })

        # 2. Passos de segurança (se crítico)
        if 'producao' in request_refinado.lower():
            plano.append({
                'etapa': 'backup',
                'descricao': 'Fazer backup do estado atual',
                'comando': 'backup automatizado ou manual',
                'prioridade': 1,
                'tipo': 'seguranca'
            })

        # 3. Passo principal (baseado na ação principal)
        intencoes = analise.get('intencoes', [])
        if intencoes:
            intencao_principal = intencoes[0]
            plano.append({
                'etapa': 'execucao_principal',
                'descricao': f"Executar {intencao_principal.get('acao', 'ação principal')}",
                'alvo': intencao_principal.get('alvo', 'alvo especificado'),
                'prioridade': 2,
                'tipo': 'execucao'
            })

        # 4. Passos de verificação pós-execução
        if 'configurar' in request_refinado.lower() or 'instalar' in request_refinado.lower():
            plano.append({
                'etapa': 'verificacao_pos',
                'descricao': 'Verificar se a configuração foi aplicada corretamente',
                'comando': 'status check ou teste funcional',
                'prioridade': 3,
                'tipo': 'validacao'
            })

        # 5. Passos de documentação (se relevante)
        if any(palavra in request_refinado.lower() for palavra in ['implementar', 'criar', 'configurar']):
            plano.append({
                'etapa': 'documentacao',
                'descricao': 'Documentar as alterações realizadas',
                'comando': 'atualizar arquivos de configuração ou README',
                'priority': 4,
                'tipo': 'documentacao'
            })

        return plano

    def _calcular_metricas_refinamento(self, request_original: str, request_refinado: str,
                                     analise: Dict) -> Dict[str, Any]:
        """
        Calcula métricas do refinamento realizado.

        Args:
            request_original: Solicitação original
            request_refinado: Solicitação refinada
            analise: Análise contextual

        Returns:
            Métricas do refinamento
        """

        # 1. Nível de refinamento baseado em mudanças
        mudancas_significativas = 0
        if len(request_refinado) > len(request_original) * 1.2:
            mudancas_significativas += 1
        if any(amb['impacto'] == 'alto' for amb in analise.get('ambiguidades', [])):
            mudancas_significativas += 1

        nivel = 'baixo'
        if mudancas_significativas >= 2:
            nivel = 'alto'
        elif mudancas_significativas >= 1:
            nivel = 'medio'

        # 2. Confiança no refinamento
        confianca = 0.7  # Base
        if len(analise.get('solucoes_existentes', [])) > 0:
            confianca += 0.1  # Tem soluções similares
        if len(analise.get('ambiguidades', [])) > 0:
            confianca -= 0.1  # Ambiguidades reduzem confiança
        if nivel == 'alto':
            confianca += 0.2  # Refinamento significativo

        confianca = max(0.0, min(1.0, confianca))

        # 3. Especificidade do request
        especificidade = self._calcular_especificidade(request_refinado)

        # 4. Cobertura de necessidades
        cobertura_necessidades = self._calcular_cobertura_necessidades(analise)

        return {
            'nivel': nivel,
            'confianca': confianca,
            'especificidade': especificidade,
            'cobertura_necessidades': cobertura_necessidades,
            'melhorias_aplicadas': len(analise.get('ambiguidades', [])) + len(analise.get('especificacoes', [])),
            'reducao_ambiguidade': max(0, len(analise.get('ambiguidades', [])) - 1)
        }

    def _calcular_especificidade(self, request: str) -> float:
        """
        Calcula quão específico é o request.

        Args:
            request: Request a ser analisado

        Returns:
            Score de especificidade (0.0 a 1.0)
        """

        score = 0.3  # Base

        # Palavras específicas aumentam score
        palavras_especificas = [
            'configurar', 'reiniciar', 'instalar', 'resolver', 'criar',
            'banco', 'database', 'servidor', 'odoo', 'nginx', 'postgres',
            'produção', 'testing', 'development'
        ]

        for palavra in palavras_especificas:
            if palavra in request.lower():
                score += 0.1

        # Números e paths específicos aumentam score
        if re.search(r'\d+', request):
            score += 0.1
        if re.search(r'[\w/\\.-]+\.(py|js|xml|conf|log)', request):
            score += 0.15

        # Limitar entre 0.0 e 1.0
        return max(0.0, min(1.0, score))

    def _calcular_cobertura_necessidades(self, analise: Dict) -> float:
        """
        Calcula cobertura de necessidades antecipadas.

        Args:
            analise: Análise contextual

        Returns:
            Score de cobertura (0.0 a 1.0)
        """

        necessidades_identificadas = len(analise.get('necessidades_adicionais', []))
        if necessidades_identificadas == 0:
            return 1.0  # Todas cobertas (não tem necessidades)

        # Em implementação real, verificaríamos quantas foram tratadas
        return 0.7  # Placeholder

    # Métodos auxiliares

    def _load_refinement_templates(self) -> Dict[str, Any]:
        """Carrega templates de refinamento."""
        # Em implementação real, carregaríamos de arquivos
        return {}

    def _cache_refinamento(self, request: str, refinamento: Dict):
        """Cache do refinamento para uso futuro."""
        cache_key = hash(request)
        self._refinement_cache[cache_key] = {
            'refinamento': refinamento,
            'timestamp': datetime.now()
        }


def main():
    """Função principal para testes."""
    project_root = Path(__file__).parent.parent.parent.parent

    engine = RefinementEngine(project_root)

    # Teste básico
    request_original = "fazer o odoo funcionar no servidor"
    analise_mock = {
        'entidades': {'acoes': ['fazer'], 'recursos': ['odoo', 'servidor']},
        'ambiguidades': [{'tipo': 'verbo_generico', 'termo': 'fazer'}],
        'solucoes_existentes': [],
        'necessidades_adicionais': []
    }

    refinamento = engine.refinar_solicitacao(request_original, analise_mock)

    print("🔧 Refinamento Completo:")
    print(json.dumps(refinamento, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()