#!/bin/bash
# ============================================================================
# SCRIPT DE ROLLBACK - PERMISSÕES DE VENDAS
# ============================================================================
# Reverte todas as mudanças de permissões ao estado original
# Data do Backup: 16/11/2025
# ============================================================================

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║       ROLLBACK DE PERMISSÕES - ODOO 15 REALCRED                    ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "⚠️  ATENÇÃO: Este script vai REVERTER todas as mudanças de permissões"
echo "   feitas em 16/11/2025, voltando ao estado ORIGINAL."
echo ""
echo "📦 Backup: res_groups_users_rel_backup_20251116 (381 registros)"
echo ""

# Perguntar confirmação
read -p "Deseja continuar? (S/N): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[SsYy]$ ]]; then
    echo "❌ Rollback cancelado pelo usuário."
    exit 1
fi

echo ""
echo "🔄 Iniciando rollback..."
echo ""

# Executar o rollback
cat ~/ROLLBACK_PERMISSOES.sql | sudo -u postgres psql realcred

# Verificar resultado
if [ $? -eq 0 ]; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════════════╗"
    echo "║  ✅ ROLLBACK CONCLUÍDO COM SUCESSO!                                ║"
    echo "╚════════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "📊 As permissões foram restauradas ao estado de 16/11/2025"
    echo "   (ANTES das mudanças da reestruturação)"
    echo ""
    echo "📝 Próximos passos:"
    echo "   1. Verificar no Odoo se os vendedores voltaram ao acesso original"
    echo "   2. Se necessário, pode reaplicar as mudanças usando a documentação"
    echo ""
else
    echo ""
    echo "❌ ERRO no rollback! Verifique os logs acima."
    echo ""
    exit 1
fi
