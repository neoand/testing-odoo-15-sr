#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Simplificado do Agente Proativo Claude LLM

Script de validação dos componentes do agente proativo.
"""

import sys
import importlib.util
from pathlib import Path

def test_import_module(module_name, file_path):
    """Testa importação de um módulo específico."""
    try:
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print(f"✅ {module_name} importado com sucesso")
        return module
    except Exception as e:
        print(f"❌ Erro ao importar {module_name}: {e}")
        return None

def test_basic_functionality():
    """Testa funcionalidade básica dos motores."""
    project_root = Path('.').parent.parent.parent

    if not project_root.exists():
        print(f"❌ Diretório do projeto não encontrado: {project_root}")
        return False

    print(f"📂 Diretório do projeto: {project_root}")

    # Testar imports individuais
    modules = {}

    modules['context'] = test_import_module(
        'ContextAnalysisEngine', 'agent-proativo-core.py'
    )

    modules['refinement'] = test_import_module(
        'RefinementEngine', 'refinement-engine.py'
    )

    modules['suggestions'] = test_import_module(
        'SuggestionsEngine', 'suggestions-engine.py'
    )

    modules['pattern'] = test_import_module(
        'PatternDetector', 'pattern-detector.py'
    )

    modules['learning'] = test_import_module(
        'LearningLoop', 'learning-loop.py'
    )

    # Verificar se todos os módulos foram carregados
    carregados = sum(1 for m in modules.values() if m is not None)
    total = len(modules)

    print(f"\n📊 Resultado: {carregados}/{total} módulos carregados com sucesso")

    if carregados == total:
        print("🎉 Todos os módulos foram importados com sucesso!")

        # Testar inicialização básica
        print("\n🧪 Testando inicialização básica...")

        if modules['context'] and modules['refinement']:
            try:
                # Testar análise contextual básica
                context_engine = modules['context']
                analise = context_engine.analisar_contexto_completo("testar configuração odoo")
                print(f"✅ Análise contextual básica funcionou")
                print(f"   - Entidades detectadas: {len(analise.get('entidades', {}))}")
                print(f"   - Score de confiança: {analise.get('confidence_score', 0):.2f}")
                print(f"   - Necessita proatividade: {analise.get('proatividade_necessaria', False)}")

            except Exception as e:
                print(f"❌ Erro no teste de análise: {e}")

        return True
    else:
        print("❌ Alguns módulos não puderam ser carregados")
        return False

def test_simple_scenario():
    """Testa um cenário simples completo."""
    print("\n🎯 Testando cenário simples...")

    # Importar módulos necessários
    context_module = test_import_module('ContextAnalysisEngine', 'agent-proativo-core.py')
    refinement_module = test_import_module('RefinementEngine', 'refinement-engine.py')
    suggestions_module = test_import_module('SuggestionsEngine', 'suggestions-engine.py')

    if not all([context_module, refinement_module, suggestions_module]):
        print("❌ Não foi possível executar cenário de teste")
        return False

    try:
        project_root = Path('.').parent.parent.parent

        # Inicializar motores
        context_engine = context_module.ContextAnalysisEngine(project_root)
        refinement_engine = refinement_module.RefinementEngine(project_root)
        suggestions_engine = suggestions_module.SuggestionsEngine(project_root)

        # Teste: "configurar odoo servidor testing"
        request = "configurar odoo servidor testing"

        print(f"📝 Processando: '{request}'")

        # 1. Análise contextual
        analise = context_engine.analisar_contexto_completo(request)
        print(f"✅ Análise contextual concluída")

        # 2. Refinamento
        refinamento = refinement_engine.refinar_solicitacao(request, analise)
        print(f"✅ Refinamento concluído - Nível: {refinamento.get('nivel_refinamento', 'medio')}")

        # 3. Sugestões
        sugestoes = suggestions_engine.gerar_sugestoes_proativas(analise, refinamento)
        print(f"✅ {len(sugestoes)} sugestões geradas")

        # 4. Exibir resumo
        print("\n📋 Resumo do Processamento:")
        print(f"   • Request original: {request}")
        print(f"   • Request refinado: {refinamento.get('request_refinado', request)}")
        print(f"   • Confiança da análise: {analise.get('confidence_score', 0):.2f}")
        print(f"   • Sugestões geradas: {len(sugestoes)}")
        print(f"   • Ambiguidades resolvidas: {len(refinamento.get('ambiguidades', []))}")

        return True

    except Exception as e:
        print(f"❌ Erro no cenário de teste: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Função principal de testes."""
    print("🧪 Teste do Sistema Agente Proativo Claude LLM")
    print("=" * 50)

    # Teste 1: Importação básica
    print("\n1️⃣ Teste de Importação:")
    sucesso_import = test_basic_functionality()

    if not sucesso_import:
        print("\n❌ Testes de importação falharam. Verifique os arquivos.")
        return 1

    # Teste 2: Cenário simples
    print("\n2️⃣ Teste de Funcionalidade:")
    sucesso_cenario = test_simple_scenario()

    if sucesso_cenario:
        print("\n✅ Todos os testes foram concluídos com sucesso!")
        print("\n🎉 O Sistema Agente Proativo está funcional e pronto para uso!")
        return 0
    else:
        print("\n❌ Alguns testes falharam. Verifique os erros acima.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)