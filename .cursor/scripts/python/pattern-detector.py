#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Detector de Padrões de Usuário - Agente Proativo Claude LLM

Este motor implementa detecção de padrões comportamentais do usuário
para personalização e melhoria contínua da experiência.

Classe principal: PatternDetector
"""

from pathlib import Path
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional, Set
from collections import defaultdict, Counter
import hashlib
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_logger = logging.getLogger(__name__)


class PatternDetector:
    """
    Motor principal para detecção de padrões de usuário.

    Implementa:
    - Detecção de padrões de comando
    - Análise de sequências de trabalho
    - Identificação de preferências
    - Detecção de anomalias
    - Aprendizado contínuo
    """

    def __init__(self, project_root: Path):
        """
        Inicializa o detector de padrões.

        Args:
            project_root: Caminho para a raiz do projeto
        """
        self.project_root = project_root
        self.patterns_db_path = project_root / ".claude" / "memory" / "patterns_db.json"
        self.sessions_db_path = project_root / ".claude" / "memory" / "sessions.json"

        # Carregar padrões existentes
        self.padroes_conhecidos = self._carregar_padroes_conhecidos()
        self.sessoes_anteriores = self._carregar_sessoes_anteriores()

        # Cache para análises recentes
        self._analysis_cache = {}

        # Configurações de detecção
        self.minimo_ocorrencias = 3  # Mínimo para considerar padrão
        self.janela_tempo_padrao = timedelta(days=7)  # Janela para análise
        self.threshold_similaridade = 0.8  # Similaridade para agrupar

    def analisar_padroes_sessao(self, sessao_atual: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analisa padrões em uma sessão atual e atualiza conhecimento.

        Args:
            sessao_atual: Lista de interações da sessão atual

        Returns:
            Análise completa de padrões detectados
        """

        _logger.info(f"🔍 Analisando padrões em sessão com {len(sessao_atual)} interações")

        # 1. Extrair eventos estruturados da sessão
        eventos = self._extrair_eventos(sessao_atual)

        # 2. Detectar padrões de comando
        padroes_comando = self._detectar_padroes_comando(eventos)

        # 3. Detectar padrões de sequência
        padroes_sequencia = self._detectar_padroes_sequencia(eventos)

        # 4. Detectar padrões temporais
        padroes_temporais = self._detectar_padroes_temporais(eventos)

        # 5. Detectar padrões de contexto
        padroes_contexto = self._detectar_padroes_contexto(eventos)

        # 6. Detectar anomalias
        anomalias = self._detectar_anomalias(eventos)

        # 7. Comparar com padrões históricos
        padroes_consolidados = self._consolidar_padroes_historicos(
            padroes_comando, padroes_sequencia, padroes_temporais, padroes_contexto
        )

        # 8. Atualizar banco de padrões
        self._atualizar_padroes_conhecidos(padroes_consolidados)

        # 9. Salvar sessão atual
        self._salvar_sessao_atual(sessao_atual, eventos)

        analise = {
            'sessao_id': self._gerar_session_id(sessao_atual),
            'timestamp_analise': datetime.now().isoformat(),
            'total_eventos': len(eventos),
            'padroes_comando': padroes_comando,
            'padroes_sequencia': padroes_sequencia,
            'padroes_temporais': padroes_temporais,
            'padroes_contexto': padroes_contexto,
            'anomalias': anomalias,
            'padroes_consolidados': padroes_consolidados,
            'insights': self._gerar_insights(padroes_consolidados, anomalias),
            'recomendacoes': self._gerar_recomendacoes(padroes_consolidados)
        }

        _logger.info(f"✅ Análise concluída - {len(padroes_consolidados)} padrões detectados")

        return analise

    def _extrair_eventos(self, sessao: List[Dict]) -> List[Dict[str, Any]]:
        """
        Extrai eventos estruturados da sessão bruta.

        Args:
            sessao: Lista bruta de interações

        Returns:
            Lista de eventos estruturados
        """

        eventos = []
        timestamp_base = datetime.now()

        for i, interacao in enumerate(sessao):
            # Determinar tipo de evento
            tipo_evento = self._classificar_tipo_evento(interacao)

            # Extrair comando principal se houver
            comando = self._extrair_comando_principal(interacao)

            # Extrair entidades
            entidades = self._extrair_entidades_rapido(interacao)

            # Determinar resultado
            resultado = interacao.get('resultado', 'desconhecido')

            evento = {
                'id': f"evt_{i+1}",
                'timestamp': timestamp_base + timedelta(minutes=i),
                'tipo': tipo_evento,
                'comando': comando,
                'entidades': entidades,
                'resultado': resultado,
                'duracao_estimada': interacao.get('duracao', 0),
                'contexto': interacao.get('contexto', {}),
                'raw_data': interacao
            }

            eventos.append(evento)

        return eventos

    def _detectar_padroes_comando(self, eventos: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detecta padrões em comandos executados.

        Args:
            eventos: Lista de eventos da sessão

        Returns:
            Lista de padrões de comando detectados
        """

        padroes = []

        # 1. Frequência de comandos
        comandos = [evt['comando'] for evt in eventos if evt.get('comando')]
        if comandos:
            contador_comandos = Counter(comandos)

            for comando, frequencia in contador_comandos.items():
                if frequencia >= 2:  # Padrão de repetição
                    padroes.append({
                        'tipo': 'frequencia_comando',
                        'comando': comando,
                        'frequencia': frequencia,
                        'percentual': frequencia / len(comandos) * 100,
                        'descricao': f"Comando '{comando}' executado {frequencia} vezes",
                        'confianca': min(1.0, frequencia / 5.0)
                    })

        # 2. Padrões de parâmetros
        parametros_por_comando = defaultdict(list)
        for evt in eventos:
            if evt.get('comando') and evt.get('entidades'):
                parametros_por_comando[evt['comando']].extend(evt['entidades'].values())

        for comando, params in parametros_por_comando.items():
            if len(params) >= self.minimo_ocorrencias:
                params_flat = [item for sublist in params for item in (sublist if isinstance(sublist, list) else [sublist])]
                if params_flat:
                    params_comuns = Counter(params_flat)
                    param_freq, _ = params_comuns.most_common(1)[0]
                    if param_freq >= 2:
                        padroes.append({
                            'tipo': 'parametro_frequente',
                            'comando': comando,
                            'parametro': params_comuns.most_common(1)[0][0],
                            'frequencia': param_freq,
                            'descricao': f"Parâmetro '{params_comuns.most_common(1)[0][0]}' frequentemente usado com '{comando}'",
                            'confianca': min(1.0, param_freq / 3.0)
                        })

        # 3. Padrões de prefixo/sufixo
        prefixos = [cmd.split()[0] if cmd.split() else cmd for cmd in comandos]
        if prefixos:
            contador_prefixos = Counter(prefixos)
            for prefixo, freq in contador_prefixos.items():
                if freq >= 2 and len(prefixo) > 2:  # Evitar palavras muito curtas
                    padroes.append({
                        'tipo': 'prefixo_comando',
                        'prefixo': prefixo,
                        'frequencia': freq,
                        'descricao': f"Prefixo '{prefixo}' frequentemente usado",
                        'confianca': min(1.0, freq / 4.0)
                    })

        return padroes

    def _detectar_padroes_sequencia(self, eventos: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detecta padrões de sequência de comandos.

        Args:
            eventos: Lista de eventos da sessão

        Returns:
            Lista de padrões de sequência detectados
        """

        padroes = []

        if len(eventos) < 3:
            return padroes

        # 1. Sequências de 2 comandos
        sequencias_2 = []
        for i in range(len(eventos) - 1):
            cmd_atual = eventos[i].get('comando')
            cmd_proximo = eventos[i + 1].get('comando')
            if cmd_atual and cmd_proximo:
                sequencias_2.append((cmd_atual, cmd_proximo))

        # Contar sequências repetidas
        contador_sequencias = Counter(sequencias_2)
        for (cmd1, cmd2), freq in contador_sequencias.items():
            if freq >= 2:
                padroes.append({
                    'tipo': 'sequencia_comandos',
                    'sequencia': [cmd1, cmd2],
                    'frequencia': freq,
                    'descricao': f"Sequência '{cmd1}' → '{cmd2}' executada {freq} vezes",
                    'confianca': min(1.0, freq / 3.0)
                })

        # 2. Padrões de início/fim
        comando_inicio = eventos[0].get('comando')
        comando_fim = eventos[-1].get('comando')

        if comando_inicio:
            # Verificar se este é um padrão de início
            historico_inicios = [s.get('comando_inicio') for s in self.sessoes_anteriores[-5:] if s.get('comando_inicio')]
            if historico_inicios.count(comando_inicio) >= 2:
                padroes.append({
                    'tipo': 'padrao_inicio',
                    'comando': comando_inicio,
                    'frequencia': historico_inicios.count(comando_inicio) + 1,
                    'descricao': f"Usuário frequentemente inicia sessões com '{comando_inicio}'",
                    'confianca': 0.8
                })

        return padroes

    def _detectar_padroes_temporais(self, eventos: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detecta padrões temporais.

        Args:
            eventos: Lista de eventos da sessão

        Returns:
            Lista de padrões temporais detectados
        """

        padroes = []

        if len(eventos) < 2:
            return padroes

        # 1. Duração média por tipo de comando
        duracoes_por_tipo = defaultdict(list)
        for evt in eventos:
            tipo = evt.get('tipo', 'desconhecido')
            duracao = evt.get('duracao_estimada', 0)
            if duracao > 0:
                duracoes_por_tipo[tipo].append(duracao)

        for tipo, duracoes in duracoes_por_tipo.items():
            if len(duracoes) >= 2:
                media_duracao = sum(duracoes) / len(duracoes)
                padroes.append({
                    'tipo': 'duracao_media',
                    'categoria': tipo,
                    'duracao_media': media_duracao,
                    'amostras': len(duracoes),
                    'descricao': f"Comandos do tipo '{tipo}' levam em média {media_duracao:.1f}s",
                    'confianca': min(1.0, len(duracoes) / 4.0)
                })

        # 2. Ritmo de trabalho (tempo entre comandos)
        tempos_entre = []
        for i in range(1, len(eventos)):
            delta = eventos[i]['timestamp'] - eventos[i-1]['timestamp']
            tempos_entre.append(delta.total_seconds())

        if len(tempos_entre) >= 3:
            media_tempo = sum(tempos_entre) / len(tempos_entre)
            padroes.append({
                'tipo': 'ritmo_trabalho',
                'tempo_medio_entre_comandos': media_tempo,
                'descricao': f"Usuário executa comando a cada {media_tempo:.0f}s em média",
                'confianca': 0.7
            })

        return padroes

    def _detectar_padroes_contexto(self, eventos: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detecta padrões de contexto.

        Args:
            eventos: Lista de eventos da sessão

        Returns:
            Lista de padrões de contexto detectados
        """

        padroes = []

        # 1. Contextos mais frequentes
        contextos = []
        for evt in eventos:
            contexto = evt.get('contexto', {})
            if contexto:
                contextos.extend(contexto.keys())

        if contextos:
            contador_contextos = Counter(contextos)
            for ctx, freq in contador_contextos.items():
                if freq >= 2:
                    padroes.append({
                        'tipo': 'contexto_frequente',
                        'contexto': ctx,
                        'frequencia': freq,
                        'percentual': freq / len(contextos) * 100,
                        'descricao': f"Contexto '{ctx}' presente em {freq}% dos eventos",
                        'confianca': min(1.0, freq / 4.0)
                    })

        # 2. Padrões de resultado por contexto
        resultados_por_contexto = defaultdict(list)
        for evt in eventos:
            for ctx in evt.get('contexto', {}).keys():
                resultados_por_contexto[ctx].append(evt.get('resultado', 'desconhecido'))

        for ctx, resultados in resultados_por_contexto.items():
            if len(resultados) >= 3:
                contador_resultados = Counter(resultados)
                resultado_freq, resultado_comum = contador_resultados.most_common(1)[0]
                if resultado_freq >= 2:
                    padroes.append({
                        'tipo': 'resultado_contexto',
                        'contexto': ctx,
                        'resultado_comum': resultado_comum,
                        'frequencia': resultado_freq,
                        'descricao': f"No contexto '{ctx}', resultado '{resultado_comum}' é mais comum",
                        'confianca': 0.6
                    })

        return padroes

    def _detectar_anomalias(self, eventos: List[Dict]) -> List[Dict[str, Any]]:
        """
        Detecta anomalias e comportamentos incomuns.

        Args:
            eventos: Lista de eventos da sessão

        Returns:
            Lista de anomalias detectadas
        """

        anomalias = []

        # 1. Comandos com duração anormal
        duracoes = [evt.get('duracao_estimada', 0) for evt in eventos]
        if len(duracoes) >= 5:
            media_duracao = sum(duracoes) / len(duracoes)
            desvio_padrao = (sum((d - media_duracao) ** 2 for d in duracoes) / len(duracoes)) ** 0.5

            for i, evt in enumerate(eventos):
                duracao = evt.get('duracao_estimada', 0)
                if duracao > 0:
                    z_score = abs(duracao - media_duracao) / (desvio_padrao + 1e-6)
                    if z_score > 2:  # 2 desvios padrão
                        anomalias.append({
                            'tipo': 'duracao_anormal',
                            'evento_id': evt['id'],
                            'duracao': duracao,
                            'media_esperada': media_duracao,
                            'z_score': z_score,
                            'descricao': f"Comando levou {duracao:.1f}s (esperado: {media_duracao:.1f}s)",
                            'severidade': 'alta' if z_score > 3 else 'media'
                        })

        # 2. Sequências incomuns
        if len(eventos) >= 3:
            for i in range(len(eventos) - 2):
                sequencia_atual = (
                    eventos[i].get('comando'),
                    eventos[i + 1].get('comando'),
                    eventos[i + 2].get('comando')
                )
                if all(sequencia_atual):  # Todos não nulos
                    # Verificar se esta sequência é incomum
                    frequencia_esperada = self._calcular_frequencia_esperada_sequencia(sequencia_atual)
                    if frequencia_esperada < 0.1:  # Menos de 10% de chance
                        anomalias.append({
                            'tipo': 'sequencia_incomum',
                            'sequencia': list(sequencia_atual),
                            'frequencia_esperada': frequencia_esperada,
                            'descricao': f"Sequência incomum: {sequencia_atual}",
                            'severidade': 'baixa'
                        })

        return anomalias

    def _consolidar_padroes_historicos(self, *lista_padroes) -> List[Dict[str, Any]]:
        """
        Consolida padrões detectados com padrões históricos.

        Args:
            *lista_padroes: Listas de diferentes tipos de padrões

        Returns:
            Lista consolidada de padrões
        """

        todos_padroes = []
        for lista in lista_padroes:
            todos_padroes.extend(lista)

        # Consolidar padrões similares
        padroes_consolidados = []
        vistos = set()

        for padrao in todos_padroes:
            chave_unic = self._gerar_chave_unica_padrao(padrao)

            if chave_unic not in vistos:
                # Verificar se existe padrão similar no histórico
                padrao_historico = self._encontrar_padrao_similar_historico(padrao)

                if padrao_historico:
                    # Atualizar padrão histórico com dados novos
                    padrao_consolidado = self._mesclar_padroes(padrao_historico, padrao)
                    padrao_consolidado['primeira_deteccao'] = padrao_historico.get('primeira_deteccao', datetime.now().isoformat())
                    padrao_consolidado['vezes_deteccao'] = padrao_historico.get('vezes_deteccao', 1) + 1
                else:
                    # Novo padrão
                    padrao_consolidado = padrao.copy()
                    padrao_consolidado['primeira_deteccao'] = datetime.now().isoformat()
                    padrao_consolidado['vezes_deteccao'] = 1

                padrao_consolidado['ultima_deteccao'] = datetime.now().isoformat()
                padroes_consolidados.append(padrao_consolidado)
                vistos.add(chave_unic)

        # Ordenar por confiança e frequência
        padroes_consolidados.sort(
            key=lambda x: (x.get('vezes_deteccao', 1), x.get('confianca', 0)),
            reverse=True
        )

        return padroes_consolidados

    def _gerar_insights(self, padroes: List[Dict], anomalias: List[Dict]) -> List[str]:
        """
        Gera insights baseados nos padrões detectados.

        Args:
            padroes: Lista de padrões consolidados
            anomalias: Lista de anomalias detectadas

        Returns:
            Lista de insights gerados
        """

        insights = []

        # 1. Insights de produtividade
        padroes_frequencia = [p for p in padroes if p.get('tipo') == 'frequencia_comando']
        if padroes_frequencia:
            mais_frequente = max(padroes_frequencia, key=lambda x: x.get('frequencia', 0))
            insights.append(
                f"Usuário executa '{mais_frequente['comando']}' com alta frequência "
                f"({mais_frequente['frequencia']} vezes) - pode ser um candidato para automação"
            )

        # 2. Insights de eficiência
        padroes_duracao = [p for p in padroes if p.get('tipo') == 'duracao_media']
        if padroes_duracao:
            mais_lento = max(padroes_duracao, key=lambda x: x.get('duracao_media', 0))
            insights.append(
                f"Operações do tipo '{mais_lento['categoria']}' levam mais tempo "
                f"({mais_lento['duracao_media']:.1f}s) - pode haver oportunidade de otimização"
            )

        # 3. Insights de anomalias
        if anomalias:
            anomalias_altas = [a for a in anomalias if a.get('severidade') == 'alta']
            if anomalias_altas:
                insights.append(
                    f"Detectadas {len(anomalias_altas)} anomalias de alta severidade - "
                    "pode indicar necessidade de investigação"
                )

        # 4. Insights de aprendizado
        if len(padroes) >= 5:
            insights.append(
                f"Usuário demonstra padrões consistentes ({len(padroes)} padrões detectados) - "
                "boa oportunidade para personalização da experiência"
            )

        return insights

    def _gerar_recomendacoes(self, padroes: List[Dict]) -> List[Dict[str, Any]]:
        """
        Gera recomendações baseadas nos padrões detectados.

        Args:
            padroes: Lista de padrões consolidados

        Returns:
            Lista de recomendações geradas
        """

        recomendacoes = []

        # 1. Recomendações de automação
        padroes_automacao = [
            p for p in padroes
            if p.get('frequencia', 0) >= 3 and p.get('tipo') in ['frequencia_comando', 'sequencia_comandos']
        ]

        for padrao in padroes_automacao:
            recomendacoes.append({
                'tipo': 'automacao',
                'prioridade': 'media',
                'descricao': f"Automatizar {padrao.get('comando', 'comandos frequentes')}",
                'acao': 'Criar script para automatizar esta operação',
                'ganho_estimado': padrao.get('frequencia', 0) * 30,  # 30s economizados por execução
                'complexidade': 'baixa'
            })

        # 2. Recomendações de otimização
        padroes_lentos = [
            p for p in padroes
            if p.get('tipo') == 'duracao_media' and p.get('duracao_media', 0) > 30
        ]

        for padrao in padroes_lentos:
            recomendacoes.append({
                'tipo': 'otimizacao',
                'prioridade': 'alta',
                'descricao': f"Otimizar operações do tipo '{padrao.get('categoria')}'",
                'acao': 'Investigar causas da lentidão e implementar otimizações',
                'ganho_estimado': (padrao.get('duracao_media', 0) - 10) * padrao.get('vezes_deteccao', 1),
                'complexidade': 'media'
            })

        # 3. Recomendações de aprendizado
        padroes_contexto = [p for p in padroes if p.get('tipo') == 'contexto_frequente']
        if padroes_contexto:
            recomendacoes.append({
                'tipo': 'aprendizado',
                'prioridade': 'baixa',
                'descricao': "Criar atalhos para contextos frequentes",
                'acao': 'Desenvolver comandos personalizados para contextos mais usados',
                'ganho_estimado': 15 * len(padroes_contexto),  # 15s por contexto
                'complexidade': 'baixa'
            })

        return recomendacoes

    # Métodos auxiliares

    def _carregar_padroes_conhecidos(self) -> Dict[str, Any]:
        """Carrega padrões conhecidos do arquivo."""
        try:
            if self.patterns_db_path.exists():
                content = self.patterns_db_path.read_text(encoding='utf-8')
                return json.loads(content)
        except Exception as e:
            _logger.warning(f"Erro ao carregar padrões: {e}")
        return {'padroes': []}

    def _carregar_sessoes_anteriores(self) -> List[Dict[str, Any]]:
        """Carrega sessões anteriores."""
        try:
            if self.sessions_db_path.exists():
                content = self.sessions_db_path.read_text(encoding='utf-8')
                return json.loads(content)
        except Exception as e:
            _logger.warning(f"Erro ao carregar sessões: {e}")
        return []

    def _classificar_tipo_evento(self, interacao: Dict) -> str:
        """Classifica o tipo de evento."""
        if 'comando' in interacao:
            return 'comando'
        elif 'erro' in interacao:
            return 'erro'
        elif 'sucesso' in interacao:
            return 'sucesso'
        elif 'pergunta' in interacao:
            return 'pergunta'
        else:
            return 'outro'

    def _extrair_comando_principal(self, interacao: Dict) -> Optional[str]:
        """Extrai o comando principal da interação."""
        return interacao.get('comando', interacao.get('acao', None))

    def _extrair_entidades_rapido(self, interacao: Dict) -> Dict[str, List[str]]:
        """Extrai entidades de forma rápida."""
        entidades = {
            'acoes': [],
            'recursos': [],
            'contextos': []
        }

        texto = str(interacao).lower()

        # Palavras-chave simples
        if any(palavra in texto for palavra in ['reiniciar', 'restart', 'start']):
            entidades['acoes'].append('reiniciar')
        if any(palavra in texto for palavra in ['odoo', 'postgres', 'nginx']):
            entidades['recursos'].append(palavra if palavra in texto else 'desconhecido')
        if any(palavra in texto for palavra in ['producao', 'testing', 'dev']):
            entidades['contextos'].append(palavra if palavra in texto else 'desconhecido')

        return entidades

    def _gerar_session_id(self, sessao: List[Dict]) -> str:
        """Gera ID único para a sessão."""
        content = json.dumps(sessao, sort_keys=True)
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def _atualizar_padroes_conhecidos(self, novos_padroes: List[Dict]):
        """Atualiza o banco de padrões conhecidos."""
        try:
            dados_atuais = self._carregar_padroes_conhecidos()
            dados_atuais['padroes'].extend(novos_padroes)
            dados_atuais['ultima_atualizacao'] = datetime.now().isoformat()

            self.patterns_db_path.write_text(json.dumps(dados_atuais, indent=2), encoding='utf-8')
        except Exception as e:
            _logger.error(f"Erro ao salvar padrões: {e}")

    def _salvar_sessao_atual(self, sessao: List[Dict], eventos: List[Dict]):
        """Salva a sessão atual para análise futura."""
        try:
            sessao_data = {
                'timestamp': datetime.now().isoformat(),
                'session_id': self._gerar_session_id(sessao),
                'eventos': eventos,
                'comando_inicio': eventos[0].get('comando') if eventos else None,
                'comando_fim': eventos[-1].get('comando') if eventos else None
            }

            sessoes = self._carregar_sessoes_anteriores()
            sessoes.append(sessao_data)

            # Manter apenas últimas 50 sessões
            if len(sessoes) > 50:
                sessoes = sessoes[-50:]

            self.sessions_db_path.write_text(json.dumps(sessoes, indent=2), encoding='utf-8')
        except Exception as e:
            _logger.error(f"Erro ao salvar sessão: {e}")

    def _gerar_chave_unica_padrao(self, padrao: Dict) -> str:
        """Gera chave única para identificar padrão."""
        chave_parts = [padrao.get('tipo', 'desconhecido')]
        if 'comando' in padrao:
            chave_parts.append(padrao['comando'])
        if 'sequencia' in padrao:
            chave_parts.append('_'.join(padrao['sequencia']))
        return '|'.join(chave_parts)

    def _encontrar_padrao_similar_historico(self, padrao: Dict) -> Optional[Dict]:
        """Encontra padrão similar no histórico."""
        chave_busca = self._gerar_chave_unica_padrao(padrao)

        for historico in self.padroes_conhecidos.get('padroes', []):
            if self._gerar_chave_unica_padrao(historico) == chave_busca:
                return historico
        return None

    def _mesclar_padroes(self, padrao_antigo: Dict, padrao_novo: Dict) -> Dict:
        """Mescla dois padrões similares."""
        mesclado = padrao_antigo.copy()

        # Atualizar confiança (média ponderada)
        conf_antiga = padrao_antigo.get('confianca', 0.5)
        conf_nova = padrao_novo.get('confianca', 0.5)
        mesclado['confianca'] = (conf_antiga * 0.7 + conf_nova * 0.3)

        # Atualizar frequência
        freq_antiga = padrao_antigo.get('frequencia', 1)
        freq_nova = padrao_novo.get('frequencia', 1)
        mesclado['frequencia'] = freq_antiga + freq_nova

        return mesclado

    def _calcular_frequencia_esperada_sequencia(self, sequencia: Tuple) -> float:
        """Calcula frequência esperada de uma sequência."""
        # Implementação simplificada
        return 0.05  # 5% de chance padrão


def main():
    """Função principal para testes."""
    project_root = Path(__file__).parent.parent.parent.parent

    detector = PatternDetector(project_root)

    # Simular sessão de teste
    sessao_teste = [
        {'comando': 'verificar status odoo', 'resultado': 'sucesso', 'duracao': 5},
        {'comando': 'verificar status odoo', 'resultado': 'sucesso', 'duracao': 4},
        {'comando': 'reiniciar odoo', 'resultado': 'sucesso', 'duracao': 15},
        {'comando': 'verificar status odoo', 'resultado': 'sucesso', 'duracao': 6},
        {'comando': 'configurar nginx', 'resultado': 'erro', 'duracao': 45}
    ]

    analise = detector.analisar_padroes_sessao(sessao_teste)

    print("🔍 Análise de Padrões:")
    print(json.dumps(analise, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()