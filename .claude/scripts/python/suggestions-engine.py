#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Motor de Sugestões Proativas - Agente Proativo Claude LLM

Este motor implementa sugestões inteligentes e proativas baseadas em
contexto, padrões e best practices.

Classe principal: SuggestionsEngine
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


class SuggestionsEngine:
    """
    Motor principal para geração de sugestões proativas.

    Implementa:
    - Sugestões baseadas em contexto recente
    - Identificação de padrões de usuário
    - Recomendações de best practices
    - Alertas de prevenção de riscos
    - Sugestões de otimização
    """

    def __init__(self, project_root: Path):
        """
        Inicializa o motor de sugestões.

        Args:
            project_root: Caminho para a raiz do projeto
        """
        self.project_root = project_root
        self.memory_path = project_root / ".claude" / "memory"

        # Carregar conhecimento base
        self.best_practices = self._load_best_practices()
        self.risk_patterns = self._load_risk_patterns()
        self.optimization_patterns = self._load_optimization_patterns()

        # Cache para sugestões recentes
        self._suggestions_cache = {}

        # Pesos para diferentes tipos de sugestões
        self.pesos_sugestoes = {
            'continuidade': 0.3,
            'padrao_reconhecido': 0.4,
            'best_practice': 0.5,
            'prevencao': 0.7,
            'otimizacao': 0.3,
            'automacao': 0.4,
            'seguranca': 0.8,
            'performance': 0.5
        }

    def gerar_sugestoes_proativas(self, analise_contextual: Dict[str, Any],
                                 refinamento: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """
        Gera sugestões proativas baseadas na análise contextual.

        Args:
            analise_contextual: Análise completa do contexto
            refinamento: Refinamento da solicitação (opcional)

        Returns:
            Lista de sugestões proativas ordenadas por prioridade
        """

        _logger.info("💡 Gerando sugestões proativas...")

        sugestoes = []

        # 1. Sugestões baseadas em contexto recente
        sugestoes_contextuais = self._gerar_sugestoes_contexto_recente(analise_contextual)
        sugestoes.extend(sugestoes_contextuais)

        # 2. Sugestões baseadas em padrões de usuário
        sugestoes_padroes = self._gerar_sugestoes_padroes_usuario(analise_contextual)
        sugestoes.extend(sugestoes_padroes)

        # 3. Sugestões de best practices
        sugestoes_best_practices = self._gerar_sugestoes_best_practices(analise_contextual)
        sugestoes.extend(sugestoes_best_practices)

        # 4. Sugestões de prevenção de riscos
        sugestoes_prevencao = self._gerar_sugestoes_prevencao(analise_contextual)
        sugestoes.extend(sugestoes_prevencao)

        # 5. Sugestões de otimização
        sugestoes_otimizacao = self._gerar_sugestoes_otimizacao(analise_contextual)
        sugestoes.extend(sugestoes_otimizacao)

        # 6. Sugestões baseadas em refinamento
        if refinamento:
            sugestoes_refinamento = self._gerar_sugestoes_refinamento(refinamento, analise_contextual)
            sugestoes.extend(sugestoes_refinamento)

        # 7. Deduplicar e ordenar sugestões
        sugestoes_finais = self._deduplicar_e_ordenar(sugestoes)

        # 8. Limitar número de sugestões
        sugestoes_limitadas = sugestoes_finais[:5]  # Top 5 sugestões

        _logger.info(f"✅ Geradas {len(sugestoes_limitadas)} sugestões proativas")

        return sugestoes_limitadas

    def _gerar_sugestoes_contexto_recente(self, analise: Dict) -> List[Dict[str, Any]]:
        """
        Gera sugestões baseadas no contexto recente da sessão.

        Args:
            analise: Análise contextual completa

        Returns:
            Lista de sugestões contextuais
        """

        sugestoes = []
        contexto_session = analise.get('contexto_session', {})

        # 1. Continuidade de tarefas
        if contexto_session.get('ultimo_comando') and contexto_session.get('ultima_intencao'):
            ultimo_comando = contexto_session['ultimo_comando']
            ultima_intencao = contexto_session['ultima_intencao']

            sugestoes.append({
                'tipo': 'continuidade',
                'mensagem': f"Baseado no seu último comando sobre {ultima_intencao}, você pode querer continuar com:",
                'acoes': self._gerar_acoes_continuacao(ultima_intencao, ultimo_comando),
                'peso': self.pesos_sugestoes['continuidade'],
                'prioridade': 'media',
                'categoria': 'continuidade'
            })

        # 2. Padrão de erros recentes
        erros_recentes = contexto_session.get('erros_recentes', [])
        if len(erros_recentes) >= 2:
            sugestoes.append({
                'tipo': 'padrao_erro',
                'mensagem': f"⚠️ Você encontrou {len(erros_recentes)} erros similares recentemente. Sugestão:",
                'acoes': [
                    {
                        'acao': 'investigar_causa_raiz',
                        'descricao': 'Investigar a causa raiz dos erros recorrentes',
                        'comando': 'analisar logs e padrões'
                    },
                    {
                        'acao': 'criar_script_prevencao',
                        'descricao': 'Criar script para prevenir estes erros',
                        'comando': 'automatizar verificação'
                    }
                ],
                'peso': self.pesos_sugestoes['prevencao'],
                'prioridade': 'alta',
                'categoria': 'prevencao'
            })

        # 3. Sucessos recentes - replicar
        sucessos_recentes = contexto_session.get('sucessos_recentes', [])
        if sucessos_recentes:
            sucesso_relevante = sucessos_recentes[0]  # Mais recente
            if 'padrao' in sucesso_relevante:
                sugestoes.append({
                    'tipo': 'replicar_sucesso',
                    'mensagem': f"✅ Você teve sucesso recente com: {sucesso_relevante.get('descricao', 'operações similares')}",
                    'acoes': [
                        {
                            'acao': 'aplicar_mesmo_padrao',
                            'descricao': 'Aplicar o mesmo padrão que funcionou antes',
                            'padrao': sucesso_relevante.get('padrao', '')
                        }
                    ],
                    'peso': self.pesos_sugestoes['best_practice'],
                    'prioridade': 'media',
                    'categoria': 'best_practice'
                })

        return sugestoes

    def _gerar_sugestoes_padroes_usuario(self, analise: Dict) -> List[Dict[str, Any]]:
        """
        Gera sugestões baseadas em padrões reconhecidos do usuário.

        Args:
            analise: Análise contextual completa

        Returns:
            Lista de sugestões baseadas em padrões
        """

        sugestoes = []
        padroes_usuario = analise.get('padroes_usuario', [])

        for padrao in padroes_usuario:
            if not padrao.get('aplicavel', False):
                continue

            # Padrão de preferência por automação
            if padrao.get('tipo') == 'preferencia_automacao':
                sugestoes.append({
                    'tipo': 'padrao_reconhecido',
                    'mensagem': f"Notei que você prefere soluções automatizadas. Posso criar um script para:",
                    'acoes': [
                        {
                            'acao': 'criar_automacao',
                            'descricao': 'Automatizar esta tarefa baseada no seu padrão',
                            'nivel': padrao.get('nivel', 'basico')
                        }
                    ],
                    'peso': self.pesos_sugestoes['automacao'],
                    'prioridade': 'media',
                    'categoria': 'automacao'
                })

            # Padrão de alta taxa de erro
            elif padrao.get('tipo') == 'alta_taxa_erro':
                sugestoes.append({
                    'tipo': 'padrao_reconhecido',
                    'mensagem': f"⚠️ Sua taxa de erro está em {padrao.get('taxa_erro', 0):.0%}. Sugiro ajuda adicional:",
                    'acoes': [
                        {
                            'acao': 'verificacao_dupla',
                            'descricao': 'Fazer verificação dupla antes de executar comandos'
                        },
                        {
                            'acao': 'explicacao_detalhada',
                            'descricao': 'Oferecer explicações mais detalhadas dos comandos'
                        }
                    ],
                    'peso': self.pesos_sugestoes['prevencao'],
                    'prioridade': 'alta',
                    'categoria': 'ajuda'
                })

            # Padrão de estilo de comunicação
            elif padrao.get('tipo') == 'estilo_comunicacao':
                estilo = padrao.get('estilo', '')
                sugestoes.append({
                    'tipo': 'padrao_reconhecido',
                    'mensagem': f"Vou adaptar minha comunicação ao seu estilo {estilo}:",
                    'acoes': [
                        {
                            'acao': 'adaptar_comunicacao',
                            'descricao': f'Manter comunicação {estilo} e direta'
                        }
                    ],
                    'peso': 0.2,
                    'prioridade': 'baixa',
                    'categoria': 'comunicacao'
                })

        return sugestoes

    def _gerar_sugestoes_best_practices(self, analise: Dict) -> List[Dict[str, Any]]:
        """
        Gera sugestões baseadas em best practices conhecidas.

        Args:
            analise: Análise contextual completa

        Returns:
            Lista de sugestões de best practices
        """

        sugestoes = []
        entidades = analise.get('entidades', {})

        # 1. Best practices para Odoo
        if 'odoo' in entidades.get('recursos', []):
            if 'producao' in entidades.get('contextos', []):
                sugestoes.append({
                    'tipo': 'best_practice',
                    'mensagem': '📋 Recomendações para Odoo em produção:',
                    'acoes': [
                        {
                            'acao': 'backup_antes_mudancas',
                            'descricao': 'Sempre fazer backup antes de mudanças em produção'
                        },
                        {
                            'acao': 'modo_manutencao',
                            'descricao': 'Colocar em modo manutenção durante upgrades'
                        },
                        {
                            'acao': 'monitoramento_ativo',
                            'descricao': 'Configurar monitoramento e alertas'
                        }
                    ],
                    'peso': self.pesos_sugestoes['best_practice'],
                    'prioridade': 'alta',
                    'categoria': 'producao'
                })

            if 'configurar' in entidades.get('acoes', []):
                sugestoes.append({
                    'tipo': 'best_practice',
                    'mensagem': '⚙️ Boas práticas para configuração Odoo:',
                    'acoes': [
                        {
                            'acao': 'testar_ambiente_dev',
                            'descricao': 'Testar configurações em ambiente de desenvolvimento primeiro'
                        },
                        {
                            'acao': 'documentar_mudancas',
                            'descricao': 'Documentar todas as alterações de configuração'
                        },
                        {
                            'acao': 'validar_comandos',
                            'descricao': 'Validar sintaxe dos arquivos de configuração'
                        }
                    ],
                    'peso': self.pesos_sugestoes['best_practice'],
                    'prioridade': 'media',
                    'categoria': 'configuracao'
                })

        # 2. Best practices para segurança
        if any(palavra in entidades.get('recursos', []) for palavra in ['banco', 'database', 'postgres']):
            sugestoes.append({
                'tipo': 'best_practice',
                'mensagem': '🔒 Boas práticas de segurança para banco de dados:',
                'acoes': [
                    {
                        'acao': 'backup_regular',
                        'descricao': 'Configurar backups regulares automatizados'
                    },
                    {
                        'acao': 'limitar_acessos',
                        'descricao': 'Usar usuários específicos com permissões mínimas'
                    },
                    {
                        'acao': 'encrypt_dados_sensiveis',
                        'descricao': 'Criptografar dados sensíveis se aplicável'
                    }
                ],
                'peso': self.pesos_sugestoes['seguranca'],
                'prioridade': 'alta',
                'categoria': 'seguranca'
            })

        # 3. Best practices para desenvolvimento
        if 'criar' in entidades.get('acoes', []) or 'implementar' in entidades.get('acoes', []):
            sugestoes.append({
                'tipo': 'best_practice',
                'mensagem': '👨‍💻 Boas práticas de desenvolvimento:',
                'acoes': [
                    {
                        'acao': 'versionamento_git',
                        'descricao': 'Usar Git para versionamento de todo código'
                    },
                    {
                        'acao': 'testes_unitarios',
                        'descricao': 'Escrever testes para funcionalidades críticas'
                    },
                    {
                        'acao': 'code_review',
                        'descricao': 'Fazer code review antes de aplicar mudanças'
                    }
                ],
                'peso': self.pesos_sugestoes['best_practice'],
                'prioridade': 'media',
                'categoria': 'desenvolvimento'
            })

        return sugestoes

    def _gerar_sugestoes_prevencao(self, analise: Dict) -> List[Dict[str, Any]]:
        """
        Gera sugestões de prevenção de riscos.

        Args:
            analise: Análise contextual completa

        Returns:
            Lista de sugestões de prevenção
        """

        sugestoes = []
        entidades = analise.get('entidades', {})

        # 1. Prevenção para produção
        if 'producao' in entidades.get('contextos', []):
            sugestoes.append({
                'tipo': 'prevencao',
                'mensagem': '⚠️ Alerta: Detectada operação em ambiente de produção',
                'acoes': [
                    {
                        'acao': 'verificar_backup',
                        'descricao': 'Verificar se backup atual existe',
                        'comando': 'listar backups mais recentes'
                    },
                    {
                        'acao': 'testar_homologacao',
                        'descricao': 'Testar em homologação antes',
                        'comando': 'executar mesmos passos em ambiente de teste'
                    },
                    {
                        'acao': 'preparar_rollback',
                        'descricao': 'Preparar plano de rollback',
                        'comando': 'documentar passos para reversão'
                    }
                ],
                'peso': self.pesos_sugestoes['prevencao'],
                'prioridade': 'critica',
                'categoria': 'risco'
            })

        # 2. Prevenção para comandos destrutivos
        acoes_destrutivas = ['deletar', 'remover', 'drop', 'truncate', 'unlink']
        if any(acao in entidades.get('acoes', []) for acao in acoes_destrutivas):
            sugestoes.append({
                'tipo': 'prevencao',
                'mensagem': '🚨 Alerta: Detectada ação destrutiva',
                'acoes': [
                    {
                        'acao': 'confirmar_alvo',
                        'descricao': 'Confirmar alvo exato da ação',
                        'comando': 'verificar se alvo está correto'
                    },
                    {
                        'acao': 'backup_antes',
                        'descricao': 'Fazer backup imediatamente antes',
                        'comando': 'criar backup do alvo'
                    },
                    {
                        'acao': 'modo_dry_run',
                        'descricao': 'Executar em modo de simulação primeiro',
                        'comando': '--dry-run ou --what-if'
                    }
                ],
                'peso': self.pesos_sugestoes['prevencao'],
                'prioridade': 'alta',
                'categoria': 'risco'
            })

        # 3. Prevenção para alterações de configuração
        if 'configurar' in entidades.get('acoes', []) and any(rec in entidades.get('recursos', []) for rec in ['nginx', 'apache', 'firewall']):
            sugestoes.append({
                'tipo': 'prevencao',
                'mensagem': '⚙️ Alerta: Alteração de configuração de rede/servidor',
                'acoes': [
                    {
                        'acao': 'backup_config',
                        'descricao': 'Fazer backup da configuração atual',
                        'comando': 'copiar arquivos de config para backup'
                    },
                    {
                        'acao': 'testar_conectividade',
                        'descricao': 'Verificar conectividade após mudança',
                        'comando': 'testar acesso aos serviços'
                    },
                    {
                        'acao': 'janela_manutencao',
                        'descricao': 'Considerar janela de manutenção',
                        'comando': 'avisar usuários sobre indisponibilidade'
                    }
                ],
                'peso': self.pesos_sugestoes['prevencao'],
                'prioridade': 'media',
                'categoria': 'infraestrutura'
            })

        return sugestoes

    def _gerar_sugestoes_otimizacao(self, analise: Dict) -> List[Dict[str, Any]]:
        """
        Gera sugestões de otimização.

        Args:
            analise: Análise contextual completa

        Returns:
            Lista de sugestões de otimização
        """

        sugestoes = []
        entidades = analise.get('entidades', {})

        # 1. Otimização para performance
        if any(palavra in ' '.join(entidades.get('acoes', [])).lower() for palavra in ['lento', 'demora', 'pesado']):
            sugestoes.append({
                'tipo': 'otimizacao',
                'mensagem': '🚀 Sugestões de otimização de performance:',
                'acoes': [
                    {
                        'acao': 'identificar_bottleneck',
                        'descricao': 'Identificar gargalo de performance',
                        'comando': 'analisar uso de CPU, memória, I/O'
                    },
                    {
                        'acao': 'otimizar_queries',
                        'descricao': 'Otimizar queries lentas de banco',
                        'comando': 'analisar slow queries e adicionar índices'
                    },
                    {
                        'acao': 'habilitar_cache',
                        'descricao': 'Configurar cache para respostas frequentes',
                        'comando': 'Redis ou cache nativo do Odoo'
                    }
                ],
                'peso': self.pesos_sugestoes['performance'],
                'prioridade': 'alta',
                'categoria': 'performance'
            })

        # 2. Otimização para processos repetitivos
        contexto_session = analise.get('contexto_session', {})
        comandos_recentes = contexto_session.get('comandos_recentes', [])
        if len(comandos_recentes) >= 3:
            # Verificar se há padrão repetitivo
            comandos_unicos = set(comandos_recentes)
            if len(comandos_unicos) < len(comandos_recentes):  # Há repetição
                sugestoes.append({
                    'tipo': 'otimizacao',
                    'mensagem': '⚡ Detectei padrão repetitivo. Sugestão:',
                    'acoes': [
                        {
                            'acao': 'criar_script',
                            'descricao': 'Criar script para automatizar tarefas repetitivas',
                            'comando': 'combinar comandos repetidos em um script'
                        },
                        {
                            'acao': 'criar_alias',
                            'descricao': 'Criar aliases para comandos frequentes',
                            'comando': 'adicionar ao .bashrc ou .zshrc'
                        }
                    ],
                    'peso': self.pesos_sugestoes['automacao'],
                    'prioridade': 'media',
                    'categoria': 'automacao'
                })

        # 3. Otimização para recursos
        if any(rec in entidades.get('recursos', []) for rec in ['odoo', 'postgres']):
            sugestoes.append({
                'tipo': 'otimizacao',
                'mensagem': '💡 Sugestões de otimização de recursos:',
                'acoes': [
                    {
                        'acao': 'monitorar_recursos',
                        'descricao': 'Configurar monitoramento de recursos',
                        'comando': 'htop, iotop, nethog'
                    },
                    {
                        'acao': 'otimizar_workers',
                        'descricao': 'Ajustar número de workers Odoo',
                        'comando': 'baseado em CPUs disponíveis'
                    },
                    {
                        'acao': 'limpeza_logs',
                        'descricao': 'Implementar rotação e limpeza de logs',
                        'comando': 'logrotate ou cleanup automático'
                    }
                ],
                'peso': self.pesos_sugestoes['performance'],
                'prioridade': 'media',
                'categoria': 'recursos'
            })

        return sugestoes

    def _gerar_sugestoes_refinamento(self, refinamento: Dict, analise: Dict) -> List[Dict[str, Any]]:
        """
        Gera sugestões baseadas no refinamento da solicitação.

        Args:
            refinamento: Refinamento completo
            analise: Análise contextual

        Returns:
            Lista de sugestões baseadas no refinamento
        """

        sugestoes = []

        # 1. Se houve muitas ambiguidades resolvidas
        ambiguidades = refinamento.get('ambiguidades', [])
        if len(ambiguidades) >= 2:
            sugestoes.append({
                'tipo': 'melhoria_comunicacao',
                'mensagem': '📝 Sugestão para melhorar comunicação futura:',
                'acoes': [
                    {
                        'acao': 'ser_especifico',
                        'descricao': 'Tente ser mais específico em solicitações futuras',
                        'exemplo': 'Em vez de "fazer odoo funcionar", diga "configurar odoo para接受 conexões externas"'
                    }
                ],
                'peso': 0.3,
                'prioridade': 'baixa',
                'categoria': 'comunicacao'
            })

        # 2. Se necessidades adicionais foram identificadas
        necessidades = refinamento.get('necessidades_adicionais', [])
        if necessidades:
            sugestoes.append({
                'tipo': 'preparacao_adicional',
                'mensagem': '📋 Para tornar sua próxima solicitação mais eficaz:',
                'acoes': [
                    {
                        'acao': 'inclua_contexto',
                        'descricao': 'Inclua contexto completo na solicitação',
                        'exemplo': 'Mencione ambiente, estado atual, erro exato'
                    }
                ],
                'peso': 0.4,
                'prioridade': 'media',
                'categoria': 'preparacao'
            })

        return sugestoes

    def _gerar_acoes_continuacao(self, ultima_intencao: str, ultimo_comando: str) -> List[Dict[str, Any]]:
        """
        Gera ações de continuação baseadas na última intenção.

        Args:
            ultima_intencao: Última intenção detectada
            ultimo_comando: Último comando executado

        Returns:
            Lista de ações de continuação sugeridas
        """

        acoes = []

        # Mapeamento de intenções para continuação
        mapeamento_continuacao = {
            'configuracao': [
                {'acao': 'verificar_status', 'descricao': 'Verificar se a configuração foi aplicada corretamente'},
                {'acao': 'testar_funcionalidade', 'descricao': 'Testar a funcionalidade configurada'},
                {'acao': 'documentar_mudanca', 'descricao': 'Documentar as mudanças realizadas'}
            ],
            'instalacao': [
                {'acao': 'verificar_instalacao', 'descricao': 'Verificar se instalação foi concluída'},
                {'acao': 'configurar_pos_instalacao', 'descricao': 'Configurar pós-instalação'},
                {'acao': 'testar_funcionalidade', 'descricao': 'Testar funcionamento básico'}
            ],
            'resolucao_problema': [
                {'acao': 'verificar_solucao', 'descricao': 'Verificar se problema foi resolvido'},
                {'acao': 'monitorar_estabilidade', 'descricao': 'Monitorar estabilidade da solução'},
                {'acao': 'documentar_solucao', 'descricao': 'Documentar solução para referência futura'}
            ],
            'otimizacao': [
                {'acao': 'medir_ganho', 'descricao': 'Medir ganho de performance obtido'},
                {'acao': 'monitorar_estabilidade', 'descricao': 'Monitorar estabilidade após otimização'},
                {'acao': 'documentar_antes_depois', 'descricao': 'Documentar métricas antes/depois'}
            ]
        }

        if ultima_intencao in mapeamento_continuacao:
            acoes.extend(mapeamento_continuacao[ultima_intencao])
        else:
            # Ações genéricas
            acoes.extend([
                {'acao': 'verificar_resultado', 'descricao': 'Verificar se a operação foi concluída com sucesso'},
                {'acao': 'testar_funcionalidade', 'descricao': 'Testar a funcionalidade relacionada'}
            ])

        return acoes[:3]  # Limitar a 3 ações

    def _deduplicar_e_ordenar(self, sugestoes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove sugestões duplicadas e ordena por prioridade.

        Args:
            sugestoes: Lista completa de sugestões

        Returns:
            Lista deduplicada e ordenada
        """

        # Deduplicação baseada em mensagem
        mensagens_vistas = set()
        sugestoes_unicas = []

        for sugestao in sugestoes:
            mensagem = sugestao.get('mensagem', '')
            if mensagem not in mensagens_vistas:
                sugestoes_unicas.append(sugestao)
                mensagens_vistas.add(mensagem)

        # Ordenar por: prioridade > peso > categoria
        prioridade_order = {'critica': 4, 'alta': 3, 'media': 2, 'baixa': 1}

        sugestoes_unicas.sort(key=lambda x: (
            prioridade_order.get(x.get('prioridade', 'media'), 2),
            x.get('peso', 0.5)
        ), reverse=True)

        return sugestoes_unicas

    # Métodos auxiliares para carregar conhecimento

    def _load_best_practices(self) -> Dict[str, Any]:
        """Carrega best practices conhecidas."""
        # Em implementação real, carregaríamos de arquivos de memória
        return {
            'odoo': {
                'producao': ['backup', 'monitoramento', 'manutencao'],
                'configuracao': ['teste_previo', 'documentacao', 'validacao']
            },
            'seguranca': {
                'banco': ['backup', 'acessos_limitados', 'criptografia'],
                'servidor': ['firewall', 'ssl', 'monitoramento']
            }
        }

    def _load_risk_patterns(self) -> Dict[str, Any]:
        """Carrega padrões de risco conhecidos."""
        return {
            'producao': ['backup', 'rollback', 'janela_manutencao'],
            'destrutivo': ['confirmacao', 'backup', 'dry_run'],
            'configuracao': ['backup', 'teste', 'validacao']
        }

    def _load_optimization_patterns(self) -> Dict[str, Any]:
        """Carrega padrões de otimização."""
        return {
            'performance': ['cache', 'indices', 'queries'],
            'recursos': ['monitoramento', 'workers', 'limpeza'],
            'automacao': ['scripts', 'aliases', 'agendamento']
        }


def main():
    """Função principal para testes."""
    project_root = Path(__file__).parent.parent.parent.parent

    engine = SuggestionsEngine(project_root)

    # Teste básico
    analise_mock = {
        'entidades': {
            'acoes': ['configurar'],
            'recursos': ['odoo'],
            'contextos': ['producao']
        },
        'contexto_session': {
            'ultimo_comando': 'configurar odoo',
            'ultima_intencao': 'configuracao',
            'erros_recentes': [],
            'sucessos_recentes': []
        },
        'padroes_usuario': []
    }

    sugestoes = engine.gerar_sugestoes_proativas(analise_mock)

    print("💡 Sugestões Proativas Geradas:")
    for i, sugestao in enumerate(sugestoes, 1):
        print(f"\n{i}. {sugestao.get('mensagem', 'Sem mensagem')}")
        for acao in sugestao.get('acoes', [])[:2]:
            print(f"   - {acao.get('descricao', 'Sem descrição')}")


if __name__ == "__main__":
    main()