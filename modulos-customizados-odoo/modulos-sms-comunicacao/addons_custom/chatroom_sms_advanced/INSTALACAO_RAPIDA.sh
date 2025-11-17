#!/bin/bash
# -*- coding: utf-8 -*-
#
# INSTALAÇÃO RÁPIDA - chatroom_sms_advanced v15.0.2.0.0
# Data: 16/11/2025
# Autor: Anderson Oliveira
#
# IMPORTANTE: Leia CHECKLIST_PRE_INSTALACAO.md antes de executar!
#

set -e  # Exit on error

echo "=================================================="
echo "  INSTALAÇÃO chatroom_sms_advanced v15.0.2.0.0"
echo "=================================================="
echo ""

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para print colorido
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar se está no diretório correto
if [ ! -f "__manifest__.py" ]; then
    print_error "Execute este script de dentro do diretório chatroom_sms_advanced!"
    exit 1
fi

print_info "Diretório correto: $(pwd)"

# ==========================================
# PASSO 1: VALIDAÇÕES PRÉ-INSTALAÇÃO
# ==========================================

print_info "Validando sintaxe Python..."
if python3 -m py_compile models/*.py wizard/*.py 2>/dev/null; then
    print_info "✓ Sintaxe Python OK"
else
    print_error "✗ Erro na sintaxe Python!"
    exit 1
fi

print_info "Validando arquivos XML..."
if command -v xmllint &> /dev/null; then
    if xmllint --noout views/*.xml wizard/*.xml security/*.xml data/*.xml 2>/dev/null; then
        print_info "✓ Sintaxe XML OK"
    else
        print_error "✗ Erro na sintaxe XML!"
        exit 1
    fi
else
    print_warning "xmllint não encontrado - pulando validação XML"
fi

# ==========================================
# PASSO 2: CONFIRMAÇÃO
# ==========================================

echo ""
print_warning "ATENÇÃO: Este script irá:"
echo "  1. Fazer backup do banco de dados"
echo "  2. Enviar módulo para o servidor odoo-rc"
echo "  3. Instalar o módulo no Odoo"
echo ""
read -p "Deseja continuar? (s/N): " confirm

if [ "$confirm" != "s" ] && [ "$confirm" != "S" ]; then
    print_info "Instalação cancelada pelo usuário"
    exit 0
fi

# ==========================================
# PASSO 3: BACKUP DO BANCO DE DADOS
# ==========================================

print_info "Fazendo backup do banco de dados..."

BACKUP_DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="odoo_15_backup_${BACKUP_DATE}.sql"

ssh odoo-rc "sudo -u postgres pg_dump odoo_15 > /tmp/${BACKUP_FILE}" 2>/dev/null || {
    print_warning "Não foi possível fazer backup automático"
    print_warning "FAÇA BACKUP MANUAL antes de continuar!"
    read -p "Pressione ENTER para continuar..."
}

print_info "✓ Backup criado: /tmp/${BACKUP_FILE}"

# ==========================================
# PASSO 4: UPLOAD DO MÓDULO
# ==========================================

print_info "Enviando módulo para o servidor..."

# Limpar diretório temporário no servidor
ssh odoo-rc "rm -rf /tmp/chatroom_sms_advanced" || true

# Rsync do módulo
cd ..
rsync -avz --progress \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    --exclude='.git' \
    chatroom_sms_advanced/ odoo-rc:/tmp/chatroom_sms_advanced/

if [ $? -eq 0 ]; then
    print_info "✓ Módulo enviado com sucesso"
else
    print_error "✗ Erro ao enviar módulo"
    exit 1
fi

cd chatroom_sms_advanced

# ==========================================
# PASSO 5: MOVER PARA ADDONS_CUSTOM
# ==========================================

print_info "Instalando no servidor..."

ssh odoo-rc << 'EOF'
    # Backup do módulo antigo se existir
    if [ -d /odoo/custom/addons_custom/chatroom_sms_advanced ]; then
        echo "Fazendo backup do módulo antigo..."
        BACKUP_DATE=$(date +%Y%m%d)
        sudo cp -r /odoo/custom/addons_custom/chatroom_sms_advanced \
                   /odoo/custom/addons_custom/chatroom_sms_advanced.BACKUP_${BACKUP_DATE}
        sudo rm -rf /odoo/custom/addons_custom/chatroom_sms_advanced
    fi

    # Mover novo módulo
    sudo mv /tmp/chatroom_sms_advanced /odoo/custom/addons_custom/
    sudo chown -R odoo:odoo /odoo/custom/addons_custom/chatroom_sms_advanced
    sudo chmod -R 755 /odoo/custom/addons_custom/chatroom_sms_advanced

    echo "✓ Módulo instalado em: /odoo/custom/addons_custom/chatroom_sms_advanced"
EOF

# ==========================================
# PASSO 6: ATUALIZAR LISTA DE APPS
# ==========================================

print_info "Atualizando lista de apps..."

ssh odoo-rc << 'EOF'
    cd /odoo
    sudo -u odoo ./odoo-bin -c odoo.conf -d odoo_15 --stop-after-init --log-level=warn
EOF

if [ $? -eq 0 ]; then
    print_info "✓ Lista de apps atualizada"
else
    print_error "✗ Erro ao atualizar lista de apps"
    exit 1
fi

# ==========================================
# PASSO 7: OPÇÃO DE INSTALAÇÃO
# ==========================================

echo ""
print_info "Módulo enviado com sucesso!"
echo ""
print_warning "PRÓXIMO PASSO: Escolha como instalar:"
echo ""
echo "  OPÇÃO 1: Via Interface (RECOMENDADO)"
echo "    1. Acesse Odoo"
echo "    2. Apps > Update Apps List"
echo "    3. Remove filtro 'Apps'"
echo "    4. Busque 'SMS Advanced'"
echo "    5. Clique em Install"
echo ""
echo "  OPÇÃO 2: Via Linha de Comando"
echo "    Execute no servidor:"
echo "    ssh odoo-rc"
echo "    cd /odoo"
echo "    sudo -u odoo ./odoo-bin -c odoo.conf -d odoo_15 -i chatroom_sms_advanced --stop-after-init"
echo ""

read -p "Deseja instalar via linha de comando agora? (s/N): " install_now

if [ "$install_now" = "s" ] || [ "$install_now" = "S" ]; then
    print_info "Instalando módulo via linha de comando..."

    ssh odoo-rc << 'EOF'
        cd /odoo
        sudo -u odoo ./odoo-bin -c odoo.conf -d odoo_15 -i chatroom_sms_advanced --stop-after-init --log-level=info
EOF

    if [ $? -eq 0 ]; then
        print_info "✓ Módulo instalado com sucesso!"
    else
        print_error "✗ Erro durante instalação"
        print_error "Verifique os logs em: /var/log/odoo/odoo.log"
        exit 1
    fi
fi

# ==========================================
# PASSO 8: VERIFICAÇÃO PÓS-INSTALAÇÃO
# ==========================================

echo ""
print_info "Verificando instalação..."

ssh odoo-rc << 'EOF'
    # Verificar se módulo está instalado
    psql -U odoo odoo_15 -t -c "SELECT state FROM ir_module_module WHERE name = 'chatroom_sms_advanced';" | grep -q installed

    if [ $? -eq 0 ]; then
        echo "✓ Módulo instalado com sucesso no banco de dados"

        # Verificar modelos criados
        echo ""
        echo "Modelos criados:"
        psql -U odoo odoo_15 -c "SELECT table_name FROM information_schema.tables WHERE table_name LIKE 'sms_%' ORDER BY table_name;" | grep -E "sms_(scheduled|campaign|blacklist|dashboard)"

        # Verificar crons
        echo ""
        echo "Crons criados:"
        psql -U odoo odoo_15 -c "SELECT name, active, interval_type, interval_number FROM ir_cron WHERE name LIKE '%SMS Advanced%';"

    else
        echo "✗ Módulo NÃO foi instalado corretamente"
        exit 1
    fi
EOF

# ==========================================
# FINALIZAÇÃO
# ==========================================

echo ""
echo "=================================================="
print_info "INSTALAÇÃO CONCLUÍDA!"
echo "=================================================="
echo ""
print_info "PRÓXIMOS PASSOS:"
echo ""
echo "  1. Acesse Odoo e vá para: SMS Advanced"
echo "  2. Verifique se os menus aparecem:"
echo "     - Dashboard"
echo "     - Campaigns"
echo "     - Scheduled SMS"
echo "     - Send Bulk SMS"
echo "     - Configuration > Blacklist"
echo ""
echo "  3. Execute os testes do CHECKLIST_PRE_INSTALACAO.md"
echo ""
echo "  4. Configure o provider:"
echo "     - Balance Warning"
echo "     - DND (Do Not Disturb)"
echo ""
print_warning "  5. NÃO esqueça de testar em STAGING antes de produção!"
echo ""
echo "=================================================="
print_info "Backup do banco: /tmp/${BACKUP_FILE}"
print_info "Logs: /var/log/odoo/odoo.log"
echo "=================================================="
echo ""
print_info "Instalação finalizada com sucesso!"
echo ""
