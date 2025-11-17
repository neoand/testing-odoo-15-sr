#!/bin/bash
# Comandos Úteis - Refatoração chatroom_sms_advanced
# Data: 16/11/2025

# ============================================================
# SEÇÃO 1: BACKUP E PREPARAÇÃO
# ============================================================

# 1.1 Backup local do módulo
backup_local() {
    cd /Users/andersongoliveira/odoo_15_sr/
    cp -r chatroom_sms_advanced chatroom_sms_advanced.BACKUP_$(date +%Y%m%d_%H%M%S)
    echo "✅ Backup local criado"
}

# 1.2 Backup no servidor
backup_servidor() {
    ssh odoo-rc "cd /odoo/custom/addons_custom && sudo cp -r chatroom_sms_advanced chatroom_sms_advanced.BACKUP_$(date +%Y%m%d)"
    echo "✅ Backup servidor criado"
}

# 1.3 Backup banco de dados
backup_bd() {
    ssh odoo-rc "sudo -u postgres pg_dump odoo_15 > /tmp/odoo_15_backup_$(date +%Y%m%d).sql"
    echo "✅ Backup BD criado em /tmp/"
}

# 1.4 Criar branch Git
criar_branch() {
    cd /Users/andersongoliveira/odoo_15_sr/
    git checkout -b refactor/chatroom_sms_advanced_v2
    git add -A
    git commit -m "chore: backup estado antes refatoração v2"
    echo "✅ Branch criado: refactor/chatroom_sms_advanced_v2"
}

# ============================================================
# SEÇÃO 2: ANÁLISE E INVESTIGAÇÃO
# ============================================================

# 2.1 Listar todos modelos SMS existentes
listar_modelos_sms() {
    ssh odoo-rc "find /odoo/custom/addons_custom/sms_* -name '*.py' -path '*/models/*' -type f | sort"
}

# 2.2 Ver estrutura sms_base_sr
ver_sms_base() {
    echo "=== MODELOS sms_base_sr ==="
    ssh odoo-rc "ls -la /odoo/custom/addons_custom/sms_base_sr/models/"
    echo ""
    echo "=== VIEWS sms_base_sr ==="
    ssh odoo-rc "ls -la /odoo/custom/addons_custom/sms_base_sr/views/"
}

# 2.3 Ver métodos KolmeyaAPI
ver_kolmeya_api() {
    ssh odoo-rc "cat /odoo/custom/addons_custom/sms_kolmeya/models/kolmeya_api.py | grep -E 'def (send_|get_|check_|add_|remove_)'"
}

# 2.4 Ver campos de sms.message
ver_campos_sms_message() {
    ssh odoo-rc "cat /odoo/custom/addons_custom/sms_base_sr/models/sms_message.py | grep -E '(^\s+[a-z_]+ = fields\.)'"
}

# 2.5 Contar linhas de código atual
contar_linhas() {
    echo "=== LINHAS DE CÓDIGO (antes) ==="
    find chatroom_sms_advanced/ -name "*.py" -type f -exec wc -l {} + | tail -1
    echo ""
    echo "=== ARQUIVOS PYTHON ==="
    find chatroom_sms_advanced/ -name "*.py" -type f | wc -l
}

# ============================================================
# SEÇÃO 3: DESENVOLVIMENTO E TESTES
# ============================================================

# 3.1 Sync código local → servidor
sync_para_servidor() {
    rsync -avz --delete \
        --exclude='*.pyc' \
        --exclude='__pycache__' \
        --exclude='.git' \
        /Users/andersongoliveira/odoo_15_sr/chatroom_sms_advanced/ \
        odoo-rc:/odoo/custom/addons_custom/chatroom_sms_advanced/
    echo "✅ Código sincronizado com servidor"
}

# 3.2 Atualizar módulo no Odoo (test_db)
atualizar_modulo_test() {
    ssh odoo-rc "cd /odoo && sudo -u odoo ./odoo-bin -c odoo.conf -d test_db -u chatroom_sms_advanced --stop-after-init --log-level=warn"
}

# 3.3 Atualizar módulo no Odoo (produção)
atualizar_modulo_prod() {
    echo "⚠️  ATENÇÃO: Atualizando PRODUÇÃO!"
    read -p "Confirma? (sim/não): " confirmacao
    if [ "$confirmacao" = "sim" ]; then
        ssh odoo-rc "cd /odoo && sudo -u odoo ./odoo-bin -c odoo.conf -d odoo_15 -u chatroom_sms_advanced --stop-after-init"
        echo "✅ Módulo atualizado em produção"
    else
        echo "❌ Cancelado"
    fi
}

# 3.4 Verificar logs Odoo
ver_logs() {
    ssh odoo-rc "tail -n 100 /var/log/odoo/odoo.log | grep -i -E '(chatroom_sms|error|warning)'"
}

# 3.5 Verificar logs em tempo real
ver_logs_realtime() {
    ssh odoo-rc "tail -f /var/log/odoo/odoo.log | grep --line-buffered -i chatroom_sms"
}

# 3.6 Reiniciar Odoo
reiniciar_odoo() {
    ssh odoo-rc "sudo systemctl restart odoo"
    echo "✅ Odoo reiniciado"
    sleep 3
    ssh odoo-rc "sudo systemctl status odoo | head -20"
}

# ============================================================
# SEÇÃO 4: BANCO DE DADOS
# ============================================================

# 4.1 Conectar ao PostgreSQL
conectar_psql() {
    ssh odoo-rc "sudo -u postgres psql odoo_15"
}

# 4.2 Verificar tabelas SMS
ver_tabelas_sms() {
    ssh odoo-rc "sudo -u postgres psql odoo_15 -c \"\\dt *sms*\""
}

# 4.3 Contar registros sms.message
contar_sms_messages() {
    ssh odoo-rc "sudo -u postgres psql odoo_15 -c 'SELECT COUNT(*) FROM sms_message;'"
}

# 4.4 Ver últimos SMS enviados
ver_ultimos_sms() {
    ssh odoo-rc "sudo -u postgres psql odoo_15 -c \"SELECT id, phone, state, sent_date FROM sms_message ORDER BY sent_date DESC LIMIT 10;\""
}

# 4.5 Ver estatísticas por estado
stats_por_estado() {
    ssh odoo-rc "sudo -u postgres psql odoo_15 -c \"SELECT state, COUNT(*) as total FROM sms_message GROUP BY state ORDER BY total DESC;\""
}

# ============================================================
# SEÇÃO 5: TESTES API KOLMEYA
# ============================================================

# 5.1 Testar conexão Kolmeya (Python shell)
testar_kolmeya() {
    cat << 'EOF' | ssh odoo-rc "cd /odoo && sudo -u odoo python3"
from addons.sms_kolmeya.models.kolmeya_api import KolmeyaAPI

# IMPORTANTE: Substituir TOKEN pelo token real
api = KolmeyaAPI("Bearer SEU_TOKEN_AQUI", 109)

# Testar saldo
try:
    balance = api.get_balance()
    print(f"✅ Saldo: R$ {balance['saldo']:.2f}")
except Exception as e:
    print(f"❌ Erro: {e}")
EOF
}

# 5.2 Consultar saldo via provider
consultar_saldo() {
    ssh odoo-rc "cd /odoo && sudo -u odoo python3 << 'EOF'
import odoo
from odoo import api, SUPERUSER_ID

db = 'odoo_15'
odoo.tools.config.parse_config(['-c', 'odoo.conf', '-d', db])

with api.Environment.manage():
    registry = odoo.registry(db)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})

        provider = env['sms.provider'].search([('provider_type', '=', 'kolmeya')], limit=1)
        if provider:
            provider.action_check_balance()
            print(f'Saldo: R$ {provider.kolmeya_balance:.2f}')
        else:
            print('Provider Kolmeya não encontrado')
EOF
"
}

# ============================================================
# SEÇÃO 6: GIT E CONTROLE DE VERSÃO
# ============================================================

# 6.1 Commit incremental
commit() {
    msg="$1"
    if [ -z "$msg" ]; then
        echo "❌ Uso: commit 'mensagem do commit'"
        return 1
    fi

    cd /Users/andersongoliveira/odoo_15_sr/
    git add chatroom_sms_advanced/
    git commit -m "$msg"
    echo "✅ Commit realizado: $msg"
}

# 6.2 Ver diferenças
ver_diff() {
    cd /Users/andersongoliveira/odoo_15_sr/
    git diff chatroom_sms_advanced/
}

# 6.3 Ver histórico
ver_historico() {
    cd /Users/andersongoliveira/odoo_15_sr/
    git log --oneline --graph --decorate --all -20
}

# 6.4 Voltar mudanças (CUIDADO!)
voltar_mudancas() {
    arquivo="$1"
    if [ -z "$arquivo" ]; then
        echo "❌ Uso: voltar_mudancas 'caminho/arquivo.py'"
        return 1
    fi

    echo "⚠️  ATENÇÃO: Vai DESCARTAR mudanças em $arquivo"
    read -p "Confirma? (sim/não): " confirmacao
    if [ "$confirmacao" = "sim" ]; then
        cd /Users/andersongoliveira/odoo_15_sr/
        git checkout -- "$arquivo"
        echo "✅ Mudanças descartadas"
    else
        echo "❌ Cancelado"
    fi
}

# ============================================================
# SEÇÃO 7: LIMPEZA E MANUTENÇÃO
# ============================================================

# 7.1 Limpar __pycache__
limpar_pycache() {
    find chatroom_sms_advanced/ -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null
    find chatroom_sms_advanced/ -name "*.pyc" -delete
    echo "✅ __pycache__ limpo"
}

# 7.2 Limpar __pycache__ no servidor
limpar_pycache_servidor() {
    ssh odoo-rc "find /odoo/custom/addons_custom/chatroom_sms_advanced/ -type d -name __pycache__ -exec sudo rm -rf {} + 2>/dev/null"
    ssh odoo-rc "find /odoo/custom/addons_custom/chatroom_sms_advanced/ -name '*.pyc' -exec sudo rm -f {} +"
    echo "✅ __pycache__ servidor limpo"
}

# 7.3 Verificar permissões servidor
verificar_permissoes() {
    ssh odoo-rc "ls -la /odoo/custom/addons_custom/chatroom_sms_advanced/ | head -20"
}

# 7.4 Corrigir permissões servidor
corrigir_permissoes() {
    ssh odoo-rc "sudo chown -R odoo:odoo /odoo/custom/addons_custom/chatroom_sms_advanced/"
    ssh odoo-rc "sudo chmod -R 755 /odoo/custom/addons_custom/chatroom_sms_advanced/"
    echo "✅ Permissões corrigidas"
}

# ============================================================
# SEÇÃO 8: ATALHOS WORKFLOW COMPLETO
# ============================================================

# 8.1 Workflow: Desenvolver → Testar
dev_test() {
    echo "🔧 Iniciando workflow dev → test..."

    # 1. Limpar pycache local
    limpar_pycache

    # 2. Sync para servidor
    sync_para_servidor

    # 3. Limpar pycache servidor
    limpar_pycache_servidor

    # 4. Atualizar módulo em test_db
    atualizar_modulo_test

    # 5. Ver logs
    echo ""
    echo "📋 Últimas linhas do log:"
    ver_logs

    echo ""
    echo "✅ Workflow concluído!"
}

# 8.2 Workflow: Commit → Deploy
commit_deploy() {
    msg="$1"
    if [ -z "$msg" ]; then
        echo "❌ Uso: commit_deploy 'mensagem do commit'"
        return 1
    fi

    echo "🚀 Iniciando workflow commit → deploy..."

    # 1. Commit
    commit "$msg"

    # 2. Sync
    sync_para_servidor

    # 3. Atualizar produção
    atualizar_modulo_prod

    # 4. Reiniciar Odoo
    reiniciar_odoo

    echo ""
    echo "✅ Deploy concluído!"
}

# ============================================================
# SEÇÃO 9: FERRAMENTAS DE DEBUG
# ============================================================

# 9.1 Shell Python Odoo (interativo)
odoo_shell() {
    ssh odoo-rc "cd /odoo && sudo -u odoo python3 << 'EOF'
import odoo
from odoo import api, SUPERUSER_ID

db = 'odoo_15'
odoo.tools.config.parse_config(['-c', 'odoo.conf', '-d', db])

with api.Environment.manage():
    registry = odoo.registry(db)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})

        # Exemplos:
        print('=== Providers SMS ===')
        providers = env['sms.provider'].search([])
        for p in providers:
            print(f'{p.id} - {p.name} ({p.provider_type})')

        print()
        print('=== Últimos SMS ===')
        sms = env['sms.message'].search([], limit=5, order='create_date desc')
        for s in sms:
            print(f'{s.id} - {s.phone} - {s.state}')
EOF
"
}

# 9.2 Verificar instalação módulo
verificar_instalacao() {
    ssh odoo-rc "cd /odoo && sudo -u odoo python3 << 'EOF'
import odoo
from odoo import api, SUPERUSER_ID

db = 'odoo_15'
odoo.tools.config.parse_config(['-c', 'odoo.conf', '-d', db])

with api.Environment.manage():
    registry = odoo.registry(db)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})

        module = env['ir.module.module'].search([('name', '=', 'chatroom_sms_advanced')])
        if module:
            print(f'Módulo: {module.name}')
            print(f'Estado: {module.state}')
            print(f'Versão: {module.latest_version}')
            print(f'Instalável: {module.installable}')
        else:
            print('Módulo não encontrado!')
EOF
"
}

# 9.3 Listar modelos do módulo
listar_modelos_modulo() {
    ssh odoo-rc "cd /odoo && sudo -u odoo python3 << 'EOF'
import odoo
from odoo import api, SUPERUSER_ID

db = 'odoo_15'
odoo.tools.config.parse_config(['-c', 'odoo.conf', '-d', db])

with api.Environment.manage():
    registry = odoo.registry(db)
    with registry.cursor() as cr:
        env = api.Environment(cr, SUPERUSER_ID, {})

        models = env['ir.model'].search([
            ('modules', 'ilike', 'chatroom_sms_advanced')
        ])

        print('=== Modelos do chatroom_sms_advanced ===')
        for model in models:
            print(f'{model.model} - {model.name}')
EOF
"
}

# ============================================================
# SEÇÃO 10: MENU DE AJUDA
# ============================================================

ajuda() {
    cat << 'EOF'
╔══════════════════════════════════════════════════════════════╗
║         COMANDOS ÚTEIS - chatroom_sms_advanced              ║
╚══════════════════════════════════════════════════════════════╝

📦 BACKUP E PREPARAÇÃO:
  backup_local              - Backup local do módulo
  backup_servidor           - Backup no servidor
  backup_bd                 - Backup banco de dados
  criar_branch              - Criar branch Git refatoração

🔍 ANÁLISE:
  listar_modelos_sms        - Lista todos modelos SMS
  ver_sms_base              - Ver estrutura sms_base_sr
  ver_kolmeya_api           - Ver métodos KolmeyaAPI
  ver_campos_sms_message    - Ver campos sms.message
  contar_linhas             - Contar linhas código atual

🔧 DESENVOLVIMENTO:
  sync_para_servidor        - Sync código local → servidor
  atualizar_modulo_test     - Atualizar módulo (test_db)
  atualizar_modulo_prod     - Atualizar módulo (produção)
  ver_logs                  - Ver logs Odoo
  ver_logs_realtime         - Ver logs em tempo real
  reiniciar_odoo            - Reiniciar Odoo

💾 BANCO DE DADOS:
  conectar_psql             - Conectar PostgreSQL
  ver_tabelas_sms           - Ver tabelas SMS
  contar_sms_messages       - Contar SMS no banco
  ver_ultimos_sms           - Ver últimos SMS
  stats_por_estado          - Estatísticas por estado

🧪 TESTES:
  testar_kolmeya            - Testar API Kolmeya
  consultar_saldo           - Consultar saldo Kolmeya
  odoo_shell                - Shell Python Odoo
  verificar_instalacao      - Verificar instalação módulo
  listar_modelos_modulo     - Listar modelos do módulo

📝 GIT:
  commit "mensagem"         - Commit incremental
  ver_diff                  - Ver diferenças
  ver_historico             - Ver histórico commits
  voltar_mudancas "arquivo" - Voltar mudanças (CUIDADO!)

🧹 LIMPEZA:
  limpar_pycache            - Limpar __pycache__ local
  limpar_pycache_servidor   - Limpar __pycache__ servidor
  verificar_permissoes      - Verificar permissões servidor
  corrigir_permissoes       - Corrigir permissões servidor

🚀 WORKFLOWS:
  dev_test                  - Dev → Test (completo)
  commit_deploy "msg"       - Commit → Deploy (completo)

❓ AJUDA:
  ajuda                     - Mostra este menu

╔══════════════════════════════════════════════════════════════╗
║  Para carregar: source COMANDOS_UTEIS.sh                    ║
╚══════════════════════════════════════════════════════════════╝
EOF
}

# ============================================================
# AUTO-LOAD: Mostrar ajuda ao carregar
# ============================================================

echo "✅ Comandos carregados! Digite 'ajuda' para ver menu completo."
echo ""

# EOF
