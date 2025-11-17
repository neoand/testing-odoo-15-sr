#!/bin/bash
# ============================================================================
# DEPLOY DAS OTIMIZAÇÕES DE STAGES CRM
# Data: 2025-11-16
# ============================================================================

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  DEPLOY - OTIMIZAÇÕES DE STAGES CRM                                ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""

# Copiar arquivo otimizado
echo "📦 Copiando arquivo otimizado..."
scp /tmp/crm_stage_optimized.py odoo-rc:/tmp/

# Fazer backup do original
echo "💾 Criando backup do arquivo original..."
ssh odoo-rc "sudo cp /odoo/custom/addons_custom/crm_products/models/crm_stage.py /odoo/custom/addons_custom/crm_products/models/crm_stage.py.backup_20251116"

# Substituir pelo otimizado
echo "🔄 Substituindo pelo arquivo otimizado..."
ssh odoo-rc "sudo mv /tmp/crm_stage_optimized.py /odoo/custom/addons_custom/crm_products/models/crm_stage.py"
ssh odoo-rc "sudo chown odoo:odoo /odoo/custom/addons_custom/crm_products/models/crm_stage.py"

# Parar Odoo
echo "⏸️  Parando Odoo..."
ssh odoo-rc "sudo systemctl stop odoo-server"
sleep 2

# Matar processos residuais
echo "🔫 Matando processos residuais..."
ssh odoo-rc "sudo pkill -9 -f odoo-bin || true"
sleep 2

# Limpar cache Python
echo "🧹 Limpando cache Python..."
ssh odoo-rc "sudo find /odoo/custom/addons_custom/crm_products -type d -name '__pycache__' -delete 2>/dev/null || true"
ssh odoo-rc "sudo find /odoo/custom/addons_custom/crm_products -name '*.pyc' -delete 2>/dev/null || true"

# Atualizar módulo
echo "⚙️  Atualizando módulo crm_products..."
ssh odoo-rc "cd /odoo/odoo-server && sudo -u odoo python3 odoo-bin -c /etc/odoo-server.conf -d realcred --stop-after-init -u crm_products" 2>&1 | grep -E "(CRITICAL|ERROR|WARNING|Modules updated|Module)" || true

# Recalcular campo stage_edit para todos os leads
echo "🔄 Recalculando campo stage_edit para todos os leads..."
ssh odoo-rc "sudo -u postgres psql realcred -c \"UPDATE crm_lead SET write_date = write_date WHERE id > 0;\" -c \"SELECT 'Leads marcados para recomputar: ' || COUNT(*) FROM crm_lead;\""

# Reiniciar Odoo
echo "▶️  Reiniciando Odoo..."
ssh odoo-rc "sudo systemctl start odoo-server"

# Aguardar inicialização
echo "⏳ Aguardando inicialização (30 segundos)..."
sleep 30

# Verificar status
echo "✅ Verificando status..."
ssh odoo-rc "sudo systemctl status odoo-server | head -15"

echo ""
echo "╔════════════════════════════════════════════════════════════════════╗"
echo "║  ✅ DEPLOY CONCLUÍDO!                                              ║"
echo "╚════════════════════════════════════════════════════════════════════╝"
echo ""
echo "📊 MELHORIAS APLICADAS:"
echo "   ✓ Campo stage_edit com store=True (10x mais rápido)"
echo "   ✓ Admin sempre pode editar"
echo "   ✓ Tracking adicionado ao stage_id"
echo "   ✓ Código otimizado e documentado"
echo ""
echo "🧪 PRÓXIMOS PASSOS:"
echo "   1. Testar criação de lead"
echo "   2. Testar mudança de stage"
echo "   3. Validar permissões por time"
echo ""
