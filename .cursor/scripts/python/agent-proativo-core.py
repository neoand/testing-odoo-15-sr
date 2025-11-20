#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Análise Contextual - Agente Proativo Claude LLM

Este motor implementa a análise profunda de contexto para antecipar
necessidades e refinar solicitações do usuário.

Classe principal: ContextAnalysisEngine
"""

from pathlib import Path
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_logger = logging.getLogger(__name__)


class ContextAnalysisEngine:
    """
    Motor principal para análise contextual de solicitações do usuário.

    Implementa:
    - Extração de entidades da solicitação
    - Análise de contexto recente
    - Identificação de padrões do usuário
    - Detecção de intenções reais vs superficiais
    """

    def __init__(self, project_root: Path):
        """
        Inicializa o motor de análise contextual.

        Args:
            project_root: Caminho para a raiz do projeto
        """
        self.project_root = project_root
        self.memory_path = project_root / ".claude" / "memory"

        # Carregar conhecimento do projeto
        self.errors_solved = self._load_errors_solved()
        self.patterns = self._load_patterns()
        self.commands_history = self._load_commands_history()

        # Cache para análises recentes
        self._analysis_cache = {}

    def analisar_contexto_completo(self, request: str, contexto_recente: List[Dict] = None) -> Dict[str, Any]:
        """
        Analisa contexto completo da solicitação do usuário.

        Args:
            request: Solicitação do usuário
            contexto_recente: Histórico de interações recentes

        Returns:
            Dicionário com análise completa do contexto
        """

        _logger.info(f"🔍 Analisando contexto para request: '{request[:50]}...'")

        # 1. Extrair entidades da solicitação
        entidades = self._extrair_entidades(request)

        # 2. Verificar se já existe solução documentada
        solucoes_existentes = self._buscar_solucoes_similares(entidades, request)

        # 3. Analisar contexto recente da sessão
        contexto_session = self._analisar_sessao_recente(contexto_recente or [])

        # 4. Identificar padrões e preferências do usuário
        padroes_usuario = self._identificar_padroes_usuario(contexto_session, request)

        # 5. Detectar intenções múltiplas
        intencoes = self._detectar_intencoes_multiples(request, entidades)

        # 6. Avaliar nível de ambiguidade
        nivel_ambiguidade = self._avaliar_ambiguidade(request, entidades)

        # 7. Identificar oportunidades de melhoria
        oportunidades = self._identificar_oportunidades_melhoria(request, entidades, contexto_session)

        # 8. Criar análise básica primeiro
        timestamp = datetime.now().isoformat()
        analise = {
            'request_original': request,
            'entidades': entidades,
            'solucoes_existentes': solucoes_existentes,
            'contexto_session': contexto_session,
            'padroes_usuario': padroes_usuario,
            'intencoes': intencoes,
            'ambiguidade': nivel_ambiguidade,
            'oportunidades': oportunidades,
            'timestamp': timestamp
        }

        # 9. Adicionar campos que dependem da análise
        analise['proatividade_necessaria'] = self._avaliar_necessidade_proatividade(request, analise)
        analise['confidence_score'] = self._calcular_confidence_score(request, analise)

        # Cache da análise
        self._cache_analysis(request, analise)

        _logger.info(f"✅ Análise concluída - Score: {analise['confidence_score']:.2f}, Proatividade: {analise['proatividade_necessaria']}")

        return analise

    def _extrair_entidades(self, request: str) -> Dict[str, List[str]]:
        """
        Extrai entidades da solicitação do usuário.

        Args:
            request: Solicitação do usuário

        Returns:
            Dicionário com entidades encontradas
        """

        entidades = {
            'acoes': [],
            'recursos': [],
            'tecnologias': [],
            'servidores': [],
            'modulos': [],
            'arquivos': [],
            'comandos': [],
            'prioridades': [],
            'contextos': []
        }

        # Padrões para extração de entidades
        padroes = {
            'acoes': [
                r'\b(instalar|configurar|reiniciar|parar|criar|deletar|atualizar|verificar|testar|debugar|implementar|melhorar|otimizar|resolver)\b',
                r'\b(restart|stop|start|create|delete|update|check|test|debug|implement|improve|optimize|fix|solve)\b'
            ],
            'recursos': [
                r'\b(odoo|postgres|nginx|apache|redis|docker|kubernetes|banco|database|api|servidor|módulo)\b',
                r'\b(sms|crm|whatsapp|email|chatbot|contact.?center)\b'
            ],
            'tecnologias': [
                r'\b(python|javascript|html|css|xml|sql|json|yaml|yml|git|linux|ubuntu|gcp|aws)\b',
                r'\b(react|vue|angular|node|django|flask|fastapi)\b'
            ],
            'servidores': [
                r'\b(testing|produção|prod|staging|dev|development)\b',
                r'\b(odoo-sr-tensting|odoo-rc|pangolin)\b'
            ],
            'modulos': [
                r'\b(chatroom_sms_advanced|crm|sale|contacts|helpdesk|hr_attendance|whatsapp.?connector)\b',
                r'\b(sms_base|sms_comunicacao|l10n_br_base|social)\b'
            ],
            'arquivos': [
                r'\b\w+\.\w+(?:\.\w+)?\b',  # arquivo.ext ou arquivo.ext.ext
            ],
            'comandos': [
                r'\b(git|curl|wget|sudo|systemctl|psql|pip|npm|docker|kubectl)\b'
            ],
            'prioridades': [
                r'\b(urgente|crítico|importante|prioridade|alta|média|baixa|imediato)\b',
                r'\b(urgent|critical|important|priority|high|medium|low|immediate)\b'
            ],
            'contextos': [
                r'\b(erro|bug|problema|issue|melhoria|feature|novo|atualização)\b',
                r'\b(error|problem|issue|improvement|feature|new|update)\b'
            ]
        }

        # Extrair entidades usando regex
        for tipo, regex_list in padroes.items():
            for regex in regex_list:
                matches = re.findall(regex, request, re.IGNORECASE)
                entidades[tipo].extend([match.lower() for match in matches if match.lower() not in entidades[tipo]])

        # Extrair entidades específicas de arquivos/paths
        paths = re.findall(r'\b[\w/\\.-]+\.(py|js|xml|md|sql|json|yaml|yml|conf|sh|log)\b', request, re.IGNORECASE)
        entidades['arquivos'].extend([p.lower() for p in paths if p.lower() not in entidades['arquivos']])

        return entidades

    def _buscar_solucoes_similares(self, entidades: Dict[str, List[str]], request: str) -> List[Dict[str, Any]]:
        """
        Busca soluções similares documentadas.

        Args:
            entidades: Entidades extraídas da solicitação
            request: Solicitação original

        Returns:
            Lista de soluções similares encontradas
        """

        solucoes = []

        # 1. Buscar em errors solved
        for error in self.errors_solved.get('errors', []):
            if self._similaridade_request_error(request, error):
                solucoes.append({
                    'tipo': 'erro_resolvido',
                    'titulo': error.get('title', ''),
                    'contexto': error.get('context', ''),
                    'sintoma': error.get('symptom', ''),
                    'solucao': error.get('solution', ''),
                    'tags': error.get('tags', []),
                    'similaridade': self._calcular_similaridade(request, error.get('title', '') + ' ' + error.get('context', ''))
                })

        # 2. Buscar em commands history
        for cmd in self.commands_history.get('commands', []):
            if self._similaridade_request_comando(request, cmd):
                solucoes.append({
                    'tipo': 'comando_conhecido',
                    'comando': cmd.get('command', ''),
                    'regra_aprendida': cmd.get('rule', ''),
                    'contexto': cmd.get('context', ''),
                    'trigger': cmd.get('trigger', ''),
                    'similaridade': self._calcular_similaridade(request, cmd.get('command', '') + ' ' + cmd.get('context', ''))
                })

        # 3. Buscar em patterns
        for pattern in self.patterns.get('patterns', []):
            if self._similaridade_request_pattern(request, pattern):
                solucoes.append({
                    'tipo': 'pattern_conhecido',
                    'nome': pattern.get('name', ''),
                    'descricao': pattern.get('description', ''),
                    'categoria': pattern.get('category', ''),
                    'codigo': pattern.get('code', ''),
                    'similaridade': self._calcular_similaridade(request, pattern.get('name', '') + ' ' + pattern.get('description', ''))
                })

        # Ordenar por similaridade
        solucoes.sort(key=lambda x: x['similaridade'], reverse=True)

        return solucoes[:5]  # Top 5 soluções mais similares

    def _analisar_sessao_recente(self, contexto_recente: List[Dict]) -> Dict[str, Any]:
        """
        Analisa contexto recente da sessão.

        Args:
            contexto_recente: Lista de interações recentes

        Returns:
            Análise da sessão recente
        """

        if not contexto_recente:
            return {
                'temas_recentes': [],
                'comandos_recentes': [],
                'erros_recentes': [],
                'sucessos_recentes': [],
                'ultimo_comando': None,
                'ultima_intencao': None,
                'sequencia_logica': True,
                'nivel_experiencia': 'desconhecido'
            }

        # Extrair informações das interações recentes
        temas = []
        comandos = []
        erros = []
        sucessos = []

        for interacao in contexto_recente[-10:]:  # Últimas 10 interações
            if 'tema' in interacao:
                temas.extend(interacao['tema'])
            if 'comando' in interacao:
                comandos.append(interacao['comando'])
            if 'erro' in interacao:
                erros.append(interacao['erro'])
            if 'sucesso' in interacao:
                sucessos.append(interacao['sucesso'])

        # Analisar sequência lógica
        sequencia_logica = self._analisar_sequencia_logica(contexto_recente)

        # Detectar nível de experiência
        nivel_experiencia = self._detectar_nivel_experiencia(contexto_recente)

        return {
            'temas_recentes': list(set(temas)),
            'comandos_recentes': comandos[-5:],  # Últimos 5 comandos
            'erros_recentes': erros[-3:],  # Últimos 3 erros
            'sucessos_recentes': sucessos[-5:],  # Últimos 5 sucessos
            'ultimo_comando': contexto_recente[-1].get('comando') if contexto_recente else None,
            'ultima_intencao': contexto_recente[-1].get('intencao') if contexto_recente else None,
            'sequencia_logica': sequencia_logica,
            'nivel_experiencia': nivel_experiencia,
            'total_interacoes': len(contexto_recente)
        }

    def _identificar_padroes_usuario(self, contexto_session: Dict, request: str) -> List[Dict[str, Any]]:
        """
        Identifica padrões de comportamento do usuário.

        Args:
            contexto_session: Análise da sessão recente
            request: Solicitação atual

        Returns:
            Lista de padrões identificados
        """

        padroes = []

        # Padrão 1: Tipo de solicitação preferida
        if contexto_session['comandos_recentes']:
            acoes_freq = [cmd.split()[0] if cmd else '' for cmd in contexto_session['comandos_recentes'] if cmd and cmd.split()]
            if acoes_freq:
                acao_mais_freq = max(set(acoes_freq), key=acoes_freq.count)
                padroes.append({
                    'tipo': 'preferencia_acao',
                    'descricao': f'Usuário frequentemente usa: {acao_mais_freq}',
                    'frequencia': acoes_freq.count(acao_mais_freq) / len(acoes_freq),
                    'aplicavel': acao_mais_freq in request.lower()
                })

        # Padrão 2: Nível de detalhe preferido
        nivel_detalhe = self._analisar_nivel_detalhe(contexto_session)
        if nivel_detalhe:
            padroes.append({
                'tipo': 'nivel_detalhe',
                'descricao': f'Usuário prefere instruções {nivel_detalhe}',
                'nivel': nivel_detalhe,
                'aplicavel': self._requer_detalhe(request, nivel_detalhe)
            })

        # Padrão 3: estilo_comunicacao
        estilo = self._analisar_estilo_comunicacao(request, contexto_session)
        if estilo:
            padroes.append({
                'tipo': 'estilo_comunicacao',
                'descricao': f'Usuário comunica-se de forma {estilo}',
                'estilo': estilo,
                'aplicavel': True  # Sempre aplicável
            })

        # Padrão 4: Frequência de erros
        if contexto_session['erros_recentes']:
            taxa_erros = len(contexto_session['erros_recentes']) / max(len(contexto_session['comandos_recentes']), 1)
            if taxa_erros > 0.3:  # 30%+ de erro
                padroes.append({
                    'tipo': 'alta_taxa_erro',
                    'descricao': 'Usuário tem encontrando muitos erros recentemente',
                    'taxa_erro': taxa_erros,
                    'aplicavel': True,
                    'sugestao': 'Oferecer ajuda adicional e verificação'
                })

        # Padrão 5: Preferência por automação
        preferencia_automacao = self._detectar_preferencia_automacao(contexto_session)
        if preferencia_automacao:
            padroes.append({
                'tipo': 'preferencia_automacao',
                'descricao': 'Usuário prefere soluções automatizadas',
                'nivel': preferencia_automacao,
                'aplicavel': 'automat' in request.lower() or 'script' in request.lower()
            })

        return padroes

    def _detectar_intencoes_multiples(self, request: str, entidades: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Detecta múltiplas intenções na solicitação do usuário.

        Args:
            request: Solicitação do usuário
            entidades: Entidades extraídas

        Returns:
            Lista de intenções detectadas
        """

        intencoes = []

        # Mapeamento de intenções baseado em entidades
        mapa_intencoes = {
            'configurar': 'configuracao',
            'instalar': 'instalacao',
            'reiniciar': 'restart',
            'resolver': 'resolucao_problema',
            'criar': 'criacao',
            'melhorar': 'melhoria',
            'implementar': 'implementacao',
            'verificar': 'verificacao',
            'testar': 'teste',
            'debugar': 'debug'
        }

        # Detectar intenções baseado em palavras-chave
        for acao in entidades['acoes']:
            if acao in mapa_intencoes:
                intencoes.append({
                    'tipo': mapa_intencoes[acao],
                    'acao': acao,
                    'alvo': self._identificar_alvo_intencao(acao, entidades),
                    'prioridade': self._calcular_prioridade_intencao(acao, entidades),
                    'confianca': 0.8
                })

        # Detectar intenção implícita de aprendizado
        if any(palavra in request.lower() for palavra in ['como', 'why', 'por que', 'explicar', 'entender']):
            intencoes.append({
                'tipo': 'aprendizado',
                'acao': 'aprender',
                'alvo': self._extrair_topico_aprendizado(request),
                'prioridade': 'media',
                'confianca': 0.7
            })

        # Detectar intenção de otimização
        if any(palavra in request.lower() for palavra in ['lento', 'performance', 'otimizar', 'melhorar']):
            intencoes.append({
                'tipo': 'otimizacao',
                'acao': 'otimizar',
                'alvo': self._identificar_alvo_otimizacao(entidades),
                'prioridade': 'alta',
                'confianca': 0.8
            })

        # Ordenar por prioridade e confiança
        intencoes.sort(key=lambda x: (x['prioridade'] != 'baixa', x['confianca']), reverse=True)

        return intencoes

    def _avaliar_ambiguidade(self, request: str, entidades: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Avalia o nível de ambiguidade da solicitação.

        Args:
            request: Solicitação do usuário
            entidades: Entidades extraídas

        Returns:
            Avaliação de ambiguidade
        """

        ambiguidades = []

        # Verificar 1: Múltiplos recursos sem especificação
        if len(entidades['recursos']) > 1 and not any(p in request.lower() for p in ['e', 'and', 'com', 'with']):
            ambiguidades.append({
                'tipo': 'multiplas_acoes_sem_conector',
                'descricao': f"Múltiplos recursos detectados ({', '.join(entidades['recursos'][:3])}) sem conector claro",
                'nivel': 'medio'
            })

        # Verificar 2: Verbos genéricos
        verbos_genericos = ['fazer', 'ajustar', 'mexer', 'ver', 'arrumar']
        if any(verbo in request.lower() for verbo in verbos_genericos):
            ambiguidades.append({
                'tipo': 'verbo_generico',
                'descricao': 'Verbo genérico detectado - necessidade de especificação',
                'nivel': 'alto'
            })

        # Verificar 3: Falta de contexto
        if len(request.split()) < 4 and len(entidades['acoes']) == 0:
            ambiguidades.append({
                'tipo': 'pouco_contexto',
                'descricao': 'Solicitação muito curta - precisa de mais contexto',
                'nivel': 'alto'
            })

        # Verificar 4: Referências ambíguas
        referencias_ambiguas = ['isso', 'aquilo', 'coisa', 'algo', 'o negócio']
        if any(ref in request.lower() for ref in referencias_ambiguas):
            ambiguidades.append({
                'tipo': 'referencia_ambigua',
                'descricao': 'Referência ambígua detectada - precisa de especificação',
                'nivel': 'alto'
            })

        # Verificar 5: Múltiplas intenções sem prioridade
        if len([e for e in entidades.get('acoes', []) if e in ['configurar', 'implementar', 'criar', 'resolver']]) > 1:
            ambiguidades.append({
                'tipo': 'multiplas_intencoes',
                'descricao': 'Múltiplas intenções detectadas sem clara prioridade',
                'nivel': 'medio'
            })

        # Calcular nível geral de ambiguidade
        nivel_geral = 'baixo'
        if ambiguidades:
            niveis_numericos = {'baixo': 1, 'medio': 2, 'alto': 3}
            media_nivel = sum(niveis_numericos[a['nivel']] for a in ambiguidades) / len(ambiguidades)

            if media_nivel >= 2.5:
                nivel_geral = 'alto'
            elif media_nivel >= 1.5:
                nivel_geral = 'medio'

        return {
            'nivel_geral': nivel_geral,
            'ambiguidades': ambiguidades,
            'total_ambiguidades': len(ambiguidades),
            'precisa_esclarecimento': nivel_geral in ['medio', 'alto']
        }

    def _identificar_oportunidades_melhoria(self, request: str, entidades: Dict[str, List[str]], contexto_session: Dict) -> List[Dict[str, Any]]:
        """
        Identifica oportunidades de melhoria na solicitação.

        Args:
            request: Solicitação do usuário
            entidades: Entidades extraídas
            contexto_session: Contexto da sessão

        Returns:
            Lista de oportunidades de melhoria
        """

        oportunidades = []

        # Oportunidade 1: Sugerir comando específico se for genérico
        if any(verbo in request.lower() for verbo in ['verificar', 'checar', 'check']):
            if 'servidor' in request.lower() or 'odoo' in request.lower():
                oportunidades.append({
                    'tipo': 'especificacao_comando',
                    'sugestao': 'Sugira verificar status específico (logs, portas, processos)',
                    'exemplo': 'Verificar status do Odoo, verificar logs de erros, verificar portas em uso',
                    'impacto': 'alto'
                })

        # Oportunidade 2: Sugerir automação se for tarefa repetitiva
        if contexto_session['comandos_recentes']:
            comandos_similares = [cmd for cmd in contexto_session['comandos_recentes']
                                if any(ent in cmd.lower() for ent in entidades['acoes'])]
            if len(comandos_similares) > 2:
                oportunidades.append({
                    'tipo': 'automacao_tarefa',
                    'sugestao': 'Tarefa repetitiva detectada - sugira criar script',
                    'exemplo': 'Criar script para automatizar esta verificação',
                    'impacto': 'medio'
                })

        # Oportunidade 3: Sugerir verificação de segurança
        if any(palavra in request.lower() for palavra in ['acesso', 'permissao', 'senha', 'security']):
            oportunidades.append({
                'tipo': 'verificacao_seguranca',
                'sugestao': 'Inclua verificação de segurança na solução',
                'exemplo': 'Verificar permissões, validar inputs, usar HTTPS',
                'impacto': 'critico'
            })

        # Oportunidade 4: Sugerir monitoramento
        if 'producao' in request.lower() or 'prod' in request.lower():
            oportunidades.append({
                'tipo': 'monitoramento',
                'sugestao': 'Adicione monitoramento/logs à solução',
                'exemplo': 'Configurar logs, métricas, alertas',
                'impacto': 'alto'
            })

        # Oportunidade 5: Sugerir otimização de performance
        if any(palavra in request.lower() for palavra in ['lento', 'demora', 'pesado', 'slow']):
            oportunidades.append({
                'tipo': 'otimizacao_performance',
                'sugestao': 'Inclua análise de performance na solução',
                'exemplo': 'Identificar bottleneck, otimizar queries, cache',
                'impacto': 'alto'
            })

        return oportunidades

    def _avaliar_necessidade_proatividade(self, request: str, analise: Dict[str, Any]) -> bool:
        """
        Avalia se o caso requer atuação proativa.

        Args:
            request: Solicitação do usuário
            analise: Análise completa do contexto

        Returns:
            True se requer atuação proativa
        """

        # Critérios para ativação proativa
        criterios = [
            # Alto nível de ambiguidade
            analise['ambiguidade']['nivel_geral'] in ['medio', 'alto'],

            # Múltiplas intenções
            len(analise['intencoes']) > 1,

            # Oportunidades de melhoria críticas
            any(opp['impacto'] == 'critico' for opp in analise['oportunidades']),

            # Padrões de usuário que sugerem necessidade
            any(p['tipo'] == 'alta_taxa_erro' for p in analise['padroes_usuario']),

            # Soluções similares existentes
            len(analise['solucoes_existentes']) > 0,

            # Request vago ou genérico
            len(request.split()) < 5,

            # Indicadores de aprendizado
            any(intencao['tipo'] == 'aprendizado' for intencao in analise['intencoes'])
        ]

        # Requer proatividade se algum critério for atendido
        return any(criterios)

    def _calcular_confidence_score(self, request: str, analise: Dict[str, Any]) -> float:
        """
        Calcula score de confiança da análise.

        Args:
            request: Solicitação original
            analise: Análise completa

        Returns:
            Score de confiança (0.0 a 1.0)
        """

        score = 0.5  # Base score

        # Fatores positivos
        if len(analise['entidades']['acoes']) > 0:
            score += 0.1  # Tem ações claras

        if len(analise['solucoes_existentes']) > 0:
            score += 0.2  # Tem soluções similares

        if analise['ambiguidade']['nivel_geral'] == 'baixo':
            score += 0.1  # Baixa ambiguidade

        if len(analise['intencoes']) > 0:
            score += 0.1  # Intenções detectadas

        # Fatores negativos
        if analise['ambiguidade']['nivel_geral'] == 'alto':
            score -= 0.2  # Alta ambiguidade

        if len(request.split()) < 4:
            score -= 0.1  # Request muito curto

        # Limitar entre 0.0 e 1.0
        return max(0.0, min(1.0, score))

    # Métodos auxiliares

    def _load_errors_solved(self) -> Dict[str, Any]:
        """Carrega erros resolvidos do arquivo de memória."""
        try:
            errors_file = self.memory_path / "errors" / "ERRORS-SOLVED.md"
            if errors_file.exists():
                # Parse simplificado - em implementação real usaria markdown parser
                content = errors_file.read_text(encoding='utf-8')
                # Aqui teríamos parsing completo do markdown
                return {'errors': []}  # Placeholder
        except Exception as e:
            _logger.warning(f"Erro ao carregar ERRORS-SOLVED.md: {e}")
        return {'errors': []}

    def _load_patterns(self) -> Dict[str, Any]:
        """Carrega padrões do arquivo de memória."""
        try:
            patterns_file = self.memory_path / "patterns" / "PATTERNS.md"
            if patterns_file.exists():
                content = patterns_file.read_text(encoding='utf-8')
                return {'patterns': []}  # Placeholder
        except Exception as e:
            _logger.warning(f"Erro ao carregar PATTERNS.md: {e}")
        return {'patterns': []}

    def _load_commands_history(self) -> Dict[str, Any]:
        """Carrega histórico de comandos."""
        try:
            commands_file = self.memory_path / "commands" / "COMMAND-HISTORY.md"
            if commands_file.exists():
                content = commands_file.read_text(encoding='utf-8')
                return {'commands': []}  # Placeholder
        except Exception as e:
            _logger.warning(f"Erro ao carregar COMMAND-HISTORY.md: {e}")
        return {'commands': []}

    def _similaridade_request_error(self, request: str, error: Dict) -> bool:
        """Verifica similaridade entre request e erro."""
        # Implementação simplificada
        return False

    def _similaridade_request_comando(self, request: str, comando: Dict) -> bool:
        """Verifica similaridade entre request e comando."""
        # Implementação simplificada
        return False

    def _similaridade_request_pattern(self, request: str, pattern: Dict) -> bool:
        """Verifica similaridade entre request e pattern."""
        # Implementação simplificada
        return False

    def _calcular_similaridade(self, text1: str, text2: str) -> float:
        """Calcula similaridade entre dois textos."""
        # Implementação simplificada
        return 0.0

    def _analisar_sequencia_logica(self, contexto: List[Dict]) -> bool:
        """Analisa se a sequência de comandos é lógica."""
        return True

    def _detectar_nivel_experiencia(self, contexto: List[Dict]) -> str:
        """Detecta nível de experiência do usuário."""
        return 'intermediario'

    def _analisar_nivel_detalhe(self, contexto: Dict) -> Optional[str]:
        """Analisa nível de detalhe preferido pelo usuário."""
        return None

    def _requer_detalhe(self, request: str, nivel: str) -> bool:
        """Verifica se request requer detalhe."""
        return False

    def _analisar_estilo_comunicacao(self, request: str, contexto: Dict) -> Optional[str]:
        """Analisa estilo de comunicação do usuário."""
        return None

    def _detectar_preferencia_automacao(self, contexto: Dict) -> Optional[str]:
        """Detecta preferência por automação."""
        return None

    def _identificar_alvo_intencao(self, acao: str, entidades: Dict) -> str:
        """Identifica alvo da intenção."""
        return 'desconhecido'

    def _calcular_prioridade_intencao(self, acao: str, entidades: Dict) -> str:
        """Calcula prioridade da intenção."""
        return 'media'

    def _extrair_topico_aprendizado(self, request: str) -> str:
        """Extrai tópico de aprendizado do request."""
        return 'geral'

    def _identificar_alvo_otimizacao(self, entidades: Dict) -> str:
        """Identifica alvo de otimização."""
        return 'desconhecido'

    def _cache_analysis(self, request: str, analise: Dict):
        """Cache da análise para uso futuro."""
        cache_key = hash(request)
        self._analysis_cache[cache_key] = {
            'analise': analise,
            'timestamp': datetime.now()
        }


def main():
    """Função principal para testes."""
    project_root = Path(__file__).parent.parent.parent.parent

    engine = ContextAnalysisEngine(project_root)

    # Teste básico
    request = "preciso configurar o odoo no servidor testing"
    analise = engine.analisar_contexto_completo(request)

    print("🔍 Análise Contextual Completa:")
    print(json.dumps(analise, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()