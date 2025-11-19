#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Learning Loop - Agente Proativo Claude LLM

Este sistema implementa o ciclo de aprendizado contínuo e feedback
para evolução constante do agente proativo.

Classe principal: LearningLoop
"""

from pathlib import Path
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
import logging
import hashlib

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
_logger = logging.getLogger(__name__)


class LearningLoop:
    """
    Sistema principal de aprendizado contínuo.

    Implementa:
    - Coleta de feedback do usuário
    - Análise de eficácia das sugestões
    - Ajuste automático de parâmetros
    - Evolução dos modelos de decisão
    - Métricas de melhoria contínua
    """

    def __init__(self, project_root: Path):
        """
        Inicializa o sistema de aprendizado.

        Args:
            project_root: Caminho para a raiz do projeto
        """
        self.project_root = project_root
        self.memory_path = project_root / ".claude" / "memory"
        self.learning_db_path = self.memory_path / "learning_db.json"
        self.metrics_path = self.memory_path / "learning_metrics.json"

        # Carregar dados de aprendizado
        self.feedback_history = self._load_feedback_history()
        self.modelo_aprendizado = self._load_modelo_aprendizado()
        self.metrics_atuais = self._load_metrics()

        # Parâmetros ajustáveis
        self.parametros_atuais = {
            'threshold_proatividade': 0.6,
            'max_sugestoes': 5,
            'peso_confianca_padroes': 0.7,
            'peso_experiencia_usuario': 0.8,
            'minimo_confianca_sugestao': 0.5,
            'sensibilidade_anomalias': 0.7,
            'fator_aprendizado': 0.1  # Quão rápido o modelo aprende
        }

        # Estado atual de aprendizado
        self.sessoes_ativas = {}
        self.sugestoes_pendentes = {}

    def registrar_interacao_completa(self, sessao_id: str, interacao: Dict[str, Any]) -> Dict[str, Any]:
        """
        Registra uma interação completa para aprendizado.

        Args:
            sessao_id: ID único da sessão
            interacao: Dados completos da interação

        Returns:
            Resultado do processamento e aprendizado
        """

        _logger.info(f"📚 Processando interação completa para sessão {sessao_id}")

        # 1. Extrair eventos de aprendizado
        eventos_aprendizado = self._extrair_eventos_aprendizado(interacao)

        # 2. Analisar eficácia das ações anteriores
        eficacia_analise = self._analisar_eficacia_acoes(interacao)

        # 3. Coletar feedback implícito e explícito
        feedback = self._coletar_feedback(interacao)

        # 4. Atualizar modelo de aprendizado
        atualizacoes_modelo = self._atualizar_modelo_aprendizado(eventos_aprendizado, feedback)

        # 5. Ajustar parâmetros dinamicamente
        ajustes_parametros = self._ajustar_parametros_dinamicamente(eficacia_analise, feedback)

        # 6. Calcular métricas de melhoria
        metricas_atualizadas = self._calcular_metricas_melhoria()

        # 7. Gerar insights de aprendizado
        insights_aprendizado = self._gerar_insights_aprendizado(eventos_aprendizado, feedback)

        resultado = {
            'sessao_id': sessao_id,
            'timestamp': datetime.now().isoformat(),
            'eventos_aprendizado': len(eventos_aprendizado),
            'eficacia_geral': eficacia_analise.get('score_geral', 0.0),
            'feedback_coletado': feedback,
            'atualizacoes_modelo': atualizacoes_modelo,
            'ajustes_parametros': ajustes_parametros,
            'metricas_atualizadas': metricas_atualizadas,
            'insights_gerados': insights_aprendizado,
            'status': 'aprendizado_concluido'
        }

        # Salvar estado atualizado
        self._salvar_estado_aprendizado()

        _logger.info(f"✅ Aprendizado concluído - Score geral: {resultado['eficacia_geral']:.2f}")

        return resultado

    def _extrair_eventos_aprendizado(self, interacao: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extrai eventos relevantes para aprendizado da interação.

        Args:
            interacao: Dados completos da interação

        Returns:
            Lista de eventos de aprendizado
        """

        eventos = []

        # 1. Eventos de solicitação original
        if 'request_original' in interacao:
            eventos.append({
                'tipo': 'solicitacao',
                'dados': interacao['request_original'],
                'timestamp': interacao.get('timestamp_inicio', datetime.now().isoformat()),
                'contexto': interacao.get('contexto_analise', {})
            })

        # 2. Eventos de análise e refinamento
        if 'analise_contextual' in interacao:
            analise = interacao['analise_contextual']
            eventos.append({
                'tipo': 'analise_contextual',
                'dados': {
                    'entidades_detectadas': len(analise.get('entidades', {})),
                    'ambiguidades': len(analise.get('ambiguidades', {}).get('ambiguidades', [])),
                    'solucoes_similares': len(analise.get('solucoes_existentes', [])),
                    'confidence_score': analise.get('confidence_score', 0.0)
                },
                'timestamp': interacao.get('timestamp_analise', datetime.now().isoformat()),
                'contexto': {}
            })

        if 'refinamento' in interacao:
            refinamento = interacao['refinamento']
            eventos.append({
                'tipo': 'refinamento',
                'dados': {
                    'ambiguidades_resolvidas': len(refinamento.get('ambiguidades', [])),
                    'especificacoes_adicionadas': len(refinamento.get('especificacoes', [])),
                    'alternativas_sugeridas': len(refinamento.get('alternativas', [])),
                    'nivel_refinamento': refinamento.get('nivel_refinamento', 'medio')
                },
                'timestamp': interacao.get('timestamp_refinamento', datetime.now().isoformat()),
                'contexto': {}
            })

        # 3. Eventos de sugestões geradas
        if 'sugestoes' in interacao:
            sugestoes = interacao['sugestoes']
            eventos.append({
                'tipo': 'sugestoes_geradas',
                'dados': {
                    'total_sugestoes': len(sugestoes),
                    'tipos_sugestoes': list(set(s.get('tipo') for s in sugestoes if s.get('tipo'))),
                    'sugestoes_aceitas': len([s for s in sugestoes if s.get('aceita', False)]),
                    'sugestoes_rejeitadas': len([s for s in sugestoes if s.get('rejeitada', False)])
                },
                'timestamp': interacao.get('timestamp_sugestoes', datetime.now().isoformat()),
                'contexto': {}
            })

        # 4. Eventos de execução e resultado
        if 'resultado_execucao' in interacao:
            resultado = interacao['resultado_execucao']
            eventos.append({
                'tipo': 'execucao',
                'dados': {
                    'sucesso': resultado.get('sucesso', False),
                    'duracao': resultado.get('duracao', 0),
                    'erros': resultado.get('erros', []),
                    'warnings': resultado.get('warnings', []),
                    'output_size': len(str(resultado.get('output', '')))
                },
                'timestamp': interacao.get('timestamp_execucao', datetime.now().isoformat()),
                'contexto': {}
            })

        # 5. Eventos de feedback do usuário
        if 'feedback_usuario' in interacao:
            feedback = interacao['feedback_usuario']
            eventos.append({
                'tipo': 'feedback_usuario',
                'dados': {
                    'satisfacao': feedback.get('satisfacao', 0),
                    'utilidade': feedback.get('utilidade', 0),
                    'comentarios': feedback.get('comentarios', ''),
                    'sugestoes_usuario': feedback.get('sugestoes', [])
                },
                'timestamp': feedback.get('timestamp', datetime.now().isoformat()),
                'contexto': {}
            })

        return eventos

    def _analisar_eficacia_acoes(self, interacao: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa a eficácia das ações tomadas pelo agente.

        Args:
            interacao: Dados completos da interação

        Returns:
            Análise de eficácia com métricas
        """

        eficacia = {
            'analise_contextual': 0.0,
            'refinamento': 0.0,
            'sugestoes': 0.0,
            'execucao': 0.0,
            'score_geral': 0.0
        }

        # 1. Eficácia da análise contextual
        analise = interacao.get('analise_contextual', {})
        if analise:
            # Fatores positivos
            if analise.get('confidence_score', 0) > 0.7:
                eficacia['analise_contextual'] += 0.3
            if len(analise.get('solucoes_existentes', [])) > 0:
                eficacia['analise_contextual'] += 0.2
            if len(analise.get('entidades', {})) > 2:
                eficacia['analise_contextual'] += 0.2

        # 2. Eficácia do refinamento
        refinamento = interacao.get('refinamento', {})
        if refinamento:
            if refinamento.get('nivel_refinamento') == 'alto':
                eficacia['refinamento'] += 0.4
            elif refinamento.get('nivel_refinamento') == 'medio':
                eficacia['refinamento'] += 0.2

            if len(refinamento.get('ambiguidades', [])) > 0:
                eficacia['refinamento'] += 0.3

        # 3. Eficácia das sugestões
        sugestoes = interacao.get('sugestoes', [])
        if sugestoes:
            total_sugestoes = len(sugestoes)
            sugestoes_aceitas = len([s for s in sugestoes if s.get('aceita', False)])

            if total_sugestoes > 0:
                taxa_aceitacao = sugestoes_aceitas / total_sugestoes
                eficacia['sugestoes'] = min(1.0, taxa_aceitacao + 0.2)

            # Bônus por sugestões de alta prioridade
            sugestoes_alta_prioridade = len([s for s in sugestoes if s.get('prioridade') in ['alta', 'critica']])
            if sugestoes_alta_prioridade > 0:
                eficacia['sugestoes'] += 0.1

        # 4. Eficácia da execução
        resultado = interacao.get('resultado_execucao', {})
        if resultado:
            if resultado.get('sucesso', False):
                eficacia['execucao'] += 0.5

            # Tempo de execução
            duracao = resultado.get('duracao', 0)
            if duracao > 0 and duracao < 60:  # Menos de 1 minuto
                eficacia['execucao'] += 0.3

            # Sem erros
            if not resultado.get('erros', []):
                eficacia['execucao'] += 0.2

        # 5. Calcular score geral
        pesos = {
            'analise_contextual': 0.2,
            'refinamento': 0.2,
            'sugestoes': 0.3,
            'execucao': 0.3
        }

        eficacia['score_geral'] = sum(
            eficacia[componente] * pesos[componente]
            for componente in pesos
        )

        # 6. Adicionar ajustes baseados no feedback do usuário
        feedback = interacao.get('feedback_usuario', {})
        if feedback:
            satisfacao = feedback.get('satisfacao', 0)
            # Ajustar score geral baseado na satisfação do usuário
            eficacia['score_geral'] = (eficacia['score_geral'] * 0.7) + (satisfacao * 0.3)

        return eficacia

    def _coletar_feedback(self, interacao: Dict[str, Any]) -> Dict[str, Any]:
        """
        Coleta feedback implícito e explícito do usuário.

        Args:
            interacao: Dados completos da interação

        Returns:
            Feedback coletado e processado
        """

        feedback = {
            'explicito': {},
            'implicito': {},
            'comportamental': {},
            'sentimento': 'neutro',
            'score_geral': 0.0
        }

        # 1. Feedback explícito (se fornecido)
        if 'feedback_usuario' in interacao:
            feedback_explicito = interacao['feedback_usuario']
            feedback['explicito'] = {
                'satisfacao': feedback_explicito.get('satisfacao', 0),
                'utilidade': feedback_explicito.get('utilidade', 0),
                'clareza': feedback_explicito.get('clareza', 0),
                'comentarios': feedback_explicito.get('comentarios', ''),
                'sugestoes': feedback_explicito.get('sugestoes', [])
            }

        # 2. Feedback implícito (baseado no comportamento)
        resultado = interacao.get('resultado_execucao', {})

        # Se usuário executou comando sugerido
        comandos_sugeridos = [s.get('comando') for s in interacao.get('sugestoes', []) if s.get('comando')]
        comando_executado = resultado.get('comando_executado', '')

        if comando_executado in comandos_sugeridos:
            feedback['implicito']['aceitou_sugestao'] = True
            feedback['implicito']['confianca_sugestao'] += 0.3
        else:
            feedback['implicito']['aceitou_sugestao'] = False

        # Se usuário repetiu padrão similar
        interacoes_anteriores = self._get_interacoes_similares(interacao)
        if len(interacoes_anteriores) > 2:
            feedback['implicito']['padrao_repetido'] = True
            feedback['implicito']['consistencia'] = 0.8
        else:
            feedback['implicito']['padrao_repetido'] = False

        # 3. Feedback comportamental
        duracao_sessao = interacao.get('duracao_total', 0)
        if duracao_sessao > 0:
            # Sessão longa pode indicar engajamento ou dificuldade
            if duracao_sessao > 300:  # 5 minutos
                feedback['comportamental']['engajamento_alto'] = True
            else:
                feedback['comportamental']['resolucao_rapida'] = True

        # Número de perguntas feitas pelo usuário
        num_perguntas = len([e for e in interacao.get('eventos', []) if e.get('tipo') == 'pergunta'])
        if num_perguntas > 3:
            feedback['comportamental']['necessidade_clareza'] = True

        # 4. Análise de sentimento (baseado em comentários)
        comentarios = feedback['explicito'].get('comentarios', '')
        if comentarios:
            feedback['sentimento'] = self._analisar_sentimento(comentarios)

        # 5. Calcular score geral de feedback
        pesos_feedback = {
            'satisfacao': 0.4,
            'utilidade': 0.3,
            'confianca_sugestao': 0.2,
            'consistencia': 0.1
        }

        valores = {
            'satisfacao': feedback['explicito'].get('satisfacao', 0),
            'utilidade': feedback['explicito'].get('utilidade', 0),
            'confianca_sugestao': feedback['implicito'].get('confianca_sugestao', 0.5),
            'consistencia': feedback['implicito'].get('consistencia', 0.5)
        }

        feedback['score_geral'] = sum(
            pesos_feedback[componente] * valores[componente]
            for componente in pesos_feedback
        )

        return feedback

    def _atualizar_modelo_aprendizado(self, eventos: List[Dict], feedback: Dict) -> Dict[str, Any]:
        """
        Atualiza o modelo de aprendizado baseado nos eventos e feedback.

        Args:
            eventos: Lista de eventos de aprendizado
            feedback: Feedback coletado

        Returns:
            Atualizações realizadas no modelo
        """

        atualizacoes = {
            'padroes_atualizados': [],
            'parametros_ajustados': {},
            'novas_regras': [],
            'melhorias_modelo': []
        }

        # 1. Aprender com feedback positivo
        if feedback['score_geral'] > 0.7:
            # Identificar o que funcionou bem
            for evento in eventos:
                if evento['tipo'] == 'sugestoes_geradas' and evento['dados'].get('sugestoes_aceitas', 0) > 0:
                    # Aprender que este tipo de sugestão é útil
                    atualizacoes['padroes_atualizados'].append({
                        'tipo': 'sugestao_efetiva',
                        'contexto': evento['contexto'],
                        'confianca_incremento': 0.1
                    })

        # 2. Aprender com feedback negativo
        elif feedback['score_geral'] < 0.4:
            # Identificar o que não funcionou
            for evento in eventos:
                if evento['tipo'] == 'analise_contextual' and evento['dados'].get('confidence_score', 0) < 0.5:
                    # Reduzir confiança neste tipo de análise
                    atualizacoes['padroes_atualizados'].append({
                        'tipo': 'analise_inefetiva',
                        'contexto': evento['contexto'],
                        'confianca_decremento': 0.1
                    })

        # 3. Ajustar parâmetros baseados no feedback
        ajustes = self._calcular_ajustes_parametros(feedback)
        if ajustes:
            atualizacoes['parametros_ajustados'] = ajustes
            for parametro, novo_valor in ajustes.items():
                if parametro in self.parametros_atuais:
                    self.parametros_atuais[parametro] = novo_valor

        # 4. Gerar novas regras baseadas em padrões observados
        novas_regras = self._gerar_regras_aprendizado(eventos, feedback)
        if novas_regras:
            atualizacoes['novas_regras'] = novas_regras

        # 5. Registrar melhorias no modelo
        if feedback['score_geral'] > self.metrics_atuais.get('score_medio_feedback', 0.5):
            atualizacoes['melhorias_modelo'].append({
                'tipo': 'melhoria_geral',
                'score_anterior': self.metrics_atuais.get('score_medio_feedback', 0.5),
                'score_atual': feedback['score_geral'],
                'melhoria': feedback['score_geral'] - self.metrics_atuais.get('score_medio_feedback', 0.5)
            })

        return atualizacoes

    def _ajustar_parametros_dinamicamente(self, eficacia: Dict, feedback: Dict) -> Dict[str, Any]:
        """
        Ajusta parâmetros do sistema dinamicamente.

        Args:
            eficacia: Análise de eficácia das ações
            feedback: Feedback coletado

        Returns:
            Ajustes realizados nos parâmetros
        """

        ajustes = {}

        # 1. Ajustar threshold de proatividade
        score_geral = eficacia.get('score_geral', 0.5)
        if score_geral > 0.8:
            # Aumentar proatividade se tudo está funcionando bem
            novo_threshold = max(0.3, self.parametros_atuais['threshold_proatividade'] - 0.05)
            ajustes['threshold_proatividade'] = novo_threshold
        elif score_geral < 0.4:
            # Reduzir proatividade se não está funcionando bem
            novo_threshold = min(0.8, self.parametros_atuais['threshold_proatividade'] + 0.05)
            ajustes['threshold_proatividade'] = novo_threshold

        # 2. Ajustar número máximo de sugestões
        if feedback.get('implicito', {}).get('aceitou_sugestao', False):
            # Se aceitou sugestão, pode aumentar um pouco
            novo_max = min(7, self.parametros_atuais['max_sugestoes'] + 1)
            ajustes['max_sugestoes'] = novo_max
        elif feedback.get('score_geral', 0) < 0.5:
            # Se não gostou, reduzir número de sugestões
            novo_max = max(3, self.parametros_atuais['max_sugestoes'] - 1)
            ajustes['max_sugestoes'] = novo_max

        # 3. Ajustar peso de confiança de padrões
        if feedback.get('implicito', {}).get('padrao_repetido', False):
            # Se usuário segue padrões, aumentar peso
            novo_peso = min(0.9, self.parametros_atuais['peso_confianca_padroes'] + 0.05)
            ajustes['peso_confianca_padroes'] = novo_peso

        # 4. Ajustar sensibilidade a anomalias
        if feedback.get('comportamental', {}).get('necessidade_clareza', False):
            # Se usuário precisa de mais clareza, aumentar sensibilidade
            nova_sensibilidade = min(0.9, self.parametros_atuais['sensibilidade_anomalias'] + 0.1)
            ajustes['sensibilidade_anomalias'] = nova_sensibilidade

        return ajustes

    def _calcular_metricas_melhoria(self) -> Dict[str, Any]:
        """
        Calcula métricas de melhoria contínua.

        Returns:
            Métricas atualizadas do sistema
        """

        # 1. Métricas de eficiência
        metricas = {
            'eficiencia_geral': self._calcular_eficiencia_geral(),
            'taxa_aprendizado': self._calcular_taxa_aprendizado(),
            'qualidade_sugestoes': self._calcular_qualidade_sugestoes(),
            'satisfacao_usuario': self._calcular_satisfacao_media(),
            'adaptabilidade': self._calcular_adaptabilidade()
        }

        # 2. Métricas comparativas (vs período anterior)
        periodo_anterior = datetime.now() - timedelta(days=7)
        metricas_anteriores = self._get_metricas_periodo(periodo_anterior)

        for key in metricas:
            if key in metricas_anteriores:
                variacao = metricas[key] - metricas_anteriores[key]
                metricas[f'{key}_variacao'] = variacao
                metricas[f'{key}_tendencia'] = 'melhorando' if variacao > 0 else 'piorando'

        # 3. Score geral de melhoria
        metricas['score_geral_melhoria'] = sum(metricas.values()) / len(metricas)

        # 4. Salvar métricas atuais
        self.metrics_atuais = metricas
        self._salvar_metrics()

        return metricas

    def _gerar_insights_aprendizado(self, eventos: List[Dict], feedback: Dict) -> List[str]:
        """
        Gera insights baseados no aprendizado da sessão.

        Args:
            eventos: Eventos de aprendizado
            feedback: Feedback coletado

        Returns:
            Lista de insights gerados
        """

        insights = []

        # 1. Insights sobre padrões de uso
        eventos_tipo = [e['tipo'] for e in eventos]
        contador_tipos = Counter(eventos_tipo)
        tipo_mais_frequente = contador_tipos.most_common(1)[0] if contador_tipos else None

        if tipo_mais_frequente:
            insights.append(
                f"Tipo de evento mais frequente: '{tipo_mais_frequente}' "
                f"({contador_tipos[tipo_mais_frequente]} ocorrências)"
            )

        # 2. Insights sobre eficácia
        if feedback['score_geral'] > 0.8:
            insights.append("Alta eficácia detectada - padrões atuais estão funcionando bem")
        elif feedback['score_geral'] < 0.4:
            insights.append("Baixa eficácia detectada - necessário ajuste nos padrões")

        # 3. Insights sobre comportamento do usuário
        if feedback['implicito'].get('padrao_repetido'):
            insights.append("Usuário demonstra comportamento consistente - bom para personalização")

        if feedback['comportamental'].get('engajamento_alto'):
            insights.append("Alto engajamento do usuário detectado")

        # 4. Insights sobre oportunidades de melhoria
        if feedback['explicito'].get('sugestoes'):
            insights.append(f"Usuário forneceu sugestões: {len(feedback['explicito']['sugestoes'])}")

        # 5. Insights sobre evolução do sistema
        score_atual = feedback['score_geral']
        score_medio_historico = self.metrics_atuais.get('satisfacao_usuario', 0.5)

        if score_atual > score_medio_historico + 0.2:
            insights.append("Melhoria significativa detectada em relação ao histórico")
        elif score_atual < score_medio_historico - 0.2:
            insights.append("Performance abaixo da média histórica - atenção necessária")

        return insights

    # Métodos auxiliares

    def _load_feedback_history(self) -> List[Dict]:
        """Carrega histórico de feedback."""
        try:
            if self.learning_db_path.exists():
                content = self.learning_db_path.read_text(encoding='utf-8')
                dados = json.loads(content)
                return dados.get('feedback_history', [])
        except Exception as e:
            _logger.warning(f"Erro ao carregar feedback: {e}")
        return []

    def _load_modelo_aprendizado(self) -> Dict[str, Any]:
        """Carrega modelo de aprendizado."""
        try:
            if self.learning_db_path.exists():
                content = self.learning_db_path.read_text(encoding='utf-8')
                return json.loads(content)
        except Exception as e:
            _logger.warning(f"Erro ao carregar modelo: {e}")
        return {}

    def _load_metrics(self) -> Dict[str, Any]:
        """Carrega métricas atuais."""
        try:
            if self.metrics_path.exists():
                content = self.metrics_path.read_text(encoding='utf-8')
                return json.loads(content)
        except Exception as e:
            _logger.warning(f"Erro ao carregar métricas: {e}")
        return {}

    def _analisar_sentimento(self, texto: str) -> str:
        """Análise simples de sentimento."""
        positivas = ['bom', 'ótimo', 'excelente', 'ajudou', 'funcionou', 'perfeito', 'gostei']
        negativas = ['ruim', 'péssimo', 'não funcionou', 'erro', 'problema', 'dificuldade', 'confuso']

        texto_lower = texto.lower()

        positivas_count = sum(1 for palavra in positivas if palavra in texto_lower)
        negativas_count = sum(1 for palavra in negativas if palavra in texto_lower)

        if positivas_count > negativas_count:
            return 'positivo'
        elif negativas_count > positivas_count:
            return 'negativo'
        else:
            return 'neutro'

    def _get_interacoes_similares(self, interacao: Dict) -> List[Dict]:
        """Busca interações similares no histórico."""
        # Implementação simplificada
        return []

    def _calcular_ajustes_parametros(self, feedback: Dict) -> Dict[str, float]:
        """Calcula ajustes necessários nos parâmetros."""
        # Implementação simplificada
        return {}

    def _gerar_regras_aprendizado(self, eventos: List[Dict], feedback: Dict) -> List[Dict]:
        """Gera novas regras baseadas no aprendizado."""
        # Implementação simplificada
        return []

    def _calcular_eficiencia_geral(self) -> float:
        """Calcula eficiência geral do sistema."""
        return self.metrics_atuais.get('eficiencia_geral', 0.7)

    def _calcular_taxa_aprendizado(self) -> float:
        """Calcula taxa de aprendizado."""
        return self.metrics_atuais.get('taxa_aprendizado', 0.5)

    def _calcular_qualidade_sugestoes(self) -> float:
        """Calcula qualidade das sugestões."""
        return self.metrics_atuais.get('qualidade_sugestoes', 0.6)

    def _calcular_satisfacao_media(self) -> float:
        """Calcula satisfação média do usuário."""
        return self.metrics_atuais.get('satisfacao_usuario', 0.7)

    def _calcular_adaptabilidade(self) -> float:
        """Calcula adaptabilidade do sistema."""
        return self.metrics_atuais.get('adaptabilidade', 0.6)

    def _get_metricas_periodo(self, data: datetime) -> Dict[str, float]:
        """Obtém métricas de um período específico."""
        # Implementação simplificada
        return {}

    def _salvar_estado_aprendizado(self):
        """Salva o estado atual de aprendizado."""
        try:
            # Salvar modelo
            modelo_data = {
                'modelo_aprendizado': self.modelo_aprendizado,
                'parametros_atuais': self.parametros_atuais,
                'feedback_history': self.feedback_history,
                'ultima_atualizacao': datetime.now().isoformat()
            }
            self.learning_db_path.write_text(json.dumps(modelo_data, indent=2), encoding='utf-8')

            # Salvar métricas
            self._salvar_metrics()
        except Exception as e:
            _logger.error(f"Erro ao salvar estado: {e}")

    def _salvar_metrics(self):
        """Salva métricas atuais."""
        try:
            self.metrics_path.write_text(json.dumps(self.metrics_atuais, indent=2), encoding='utf-8')
        except Exception as e:
            _logger.error(f"Erro ao salvar métricas: {e}")


def main():
    """Função principal para testes."""
    project_root = Path(__file__).parent.parent.parent.parent

    learning_loop = LearningLoop(project_root)

    # Simular interação completa
    interacao_teste = {
        'request_original': 'configurar odoo servidor testing',
        'analise_contextual': {
            'entidades': {'acoes': ['configurar'], 'recursos': ['odoo']},
            'confidence_score': 0.8
        },
        'refinamento': {
            'nivel_refinamento': 'alto',
            'ambiguidades': [],
            'especificacoes': []
        },
        'sugestoes': [
            {'tipo': 'best_practice', 'aceita': True},
            {'tipo': 'seguranca', 'aceita': False}
        ],
        'resultado_execucao': {
            'sucesso': True,
            'duracao': 45,
            'erros': []
        },
        'feedback_usuario': {
            'satisfacao': 0.9,
            'utilidade': 0.8,
            'comentarios': 'Muito bom, ajudou bastante!'
        }
    }

    resultado = learning_loop.registrar_interacao_completa('sessao_test', interacao_teste)

    print("📚 Learning Loop - Resultado:")
    print(json.dumps(resultado, indent=2, ensure_ascii=False, default=str))


if __name__ == "__main__":
    main()