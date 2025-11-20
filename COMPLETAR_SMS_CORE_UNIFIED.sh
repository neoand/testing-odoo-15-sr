#!/bin/bash
# Script para completar módulo sms_core_unified
# Move arquivos da raiz para o módulo e organiza tudo

set -e

echo "🚀 COMPLETANDO MÓDULO SMS_CORE_UNIFIED"
echo "======================================"
echo ""

SERVER="odoo-sr-tensting"
ZONE="southamerica-east1-b"
MODULE_PATH="/odoo/custom/addons_custom/sms_core_unified"

# 1. Copiar models unificados
echo "1️⃣ Copiando models unificados..."
gcloud compute scp sms_provider_unified.py ${SERVER}:/tmp/sms_provider.py --zone=${ZONE}
gcloud compute scp sms_template_unified.py ${SERVER}:/tmp/sms_template.py --zone=${ZONE}
gcloud compute scp sms_blacklist_unified.py ${SERVER}:/tmp/sms_blacklist.py --zone=${ZONE}

gcloud compute ssh ${SERVER} --zone=${ZONE} --command="
sudo cp /tmp/sms_provider.py ${MODULE_PATH}/models/sms_provider.py
sudo cp /tmp/sms_template.py ${MODULE_PATH}/models/sms_template.py
sudo cp /tmp/sms_blacklist.py ${MODULE_PATH}/models/sms_blacklist.py
sudo chown odoo:odoo ${MODULE_PATH}/models/*.py
sudo chmod 644 ${MODULE_PATH}/models/*.py
echo '✅ Models copiados'
"

# 2. Atualizar __init__.py dos models
echo ""
echo "2️⃣ Atualizando __init__.py dos models..."
gcloud compute ssh ${SERVER} --zone=${ZONE} --command="
cat > /tmp/models_init.py << 'EOF'
# -*- coding: utf-8 -*-
from . import sms_message
from . import sms_provider
from . import sms_template
from . import sms_blacklist
EOF
sudo cp /tmp/models_init.py ${MODULE_PATH}/models/__init__.py
sudo chown odoo:odoo ${MODULE_PATH}/models/__init__.py
echo '✅ __init__.py atualizado'
"

# 3. Copiar security e views atualizados
echo ""
echo "3️⃣ Copiando security e views atualizados..."
gcloud compute scp sms_core_unified_security.xml ${SERVER}:/tmp/sms_security.xml --zone=${ZONE}
gcloud compute scp sms_core_unified_views.xml ${SERVER}:/tmp/sms_views.xml --zone=${ZONE}
gcloud compute scp sms_menu_unified.xml ${SERVER}:/tmp/sms_menu.xml --zone=${ZONE}

gcloud compute ssh ${SERVER} --zone=${ZONE} --command="
sudo cp /tmp/sms_security.xml ${MODULE_PATH}/security/sms_security.xml
sudo cp /tmp/sms_views.xml ${MODULE_PATH}/views/sms_message_views.xml
sudo cp /tmp/sms_menu.xml ${MODULE_PATH}/views/sms_menu.xml
sudo chown odoo:odoo ${MODULE_PATH}/security/*.xml ${MODULE_PATH}/views/*.xml
sudo chmod 644 ${MODULE_PATH}/security/*.xml ${MODULE_PATH}/views/*.xml
echo '✅ Security e views atualizados'
"

# 4. Atualizar __manifest__.py
echo ""
echo "4️⃣ Atualizando __manifest__.py..."
gcloud compute scp sms_core_unified_manifest.py ${SERVER}:/tmp/manifest_content.py --zone=${ZONE}

gcloud compute ssh ${SERVER} --zone=${ZONE} --command="
python3 << 'PYEOF'
import re

# Ler conteúdo do manifest atualizado
with open('/tmp/manifest_content.py', 'r') as f:
    content = f.read()

# Extrair apenas o dicionário (remover comentários/docstrings)
match = re.search(r'\{.*\}', content, re.DOTALL)
if match:
    manifest_dict = match.group(0)
    # Remover comentários de linha
    lines = manifest_dict.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remover comentários mas manter strings
        if '#' in line and not ('\"' in line or \"'\" in line):
            line = line.split('#')[0]
        cleaned_lines.append(line)
    manifest_dict = '\n'.join(cleaned_lines)
    
    # Escrever manifest
    with open('/tmp/__manifest__.py', 'w') as f:
        f.write('# -*- coding: utf-8 -*-\n')
        f.write(manifest_dict)
    print('✅ Manifest preparado')
else:
    print('❌ Erro ao extrair manifest')
PYEOF

sudo cp /tmp/__manifest__.py ${MODULE_PATH}/__manifest__.py
sudo chown odoo:odoo ${MODULE_PATH}/__manifest__.py
echo '✅ __manifest__.py atualizado'
"

# 5. Criar ir.model.access.csv se não existir
echo ""
echo "5️⃣ Verificando security/ir.model.access.csv..."
gcloud compute ssh ${SERVER} --zone=${ZONE} --command="
if [ ! -f ${MODULE_PATH}/security/ir.model.access.csv ]; then
    cat > /tmp/ir.model.access.csv << 'EOF'
id,name,model_id:id,group_id:id,perm_read,perm_write,perm_create,perm_unlink
access_sms_message_user,sms.message.user,model_sms_message,base.group_user,1,1,1,1
access_sms_provider_user,sms.provider.user,model_sms_provider,base.group_user,1,0,0,0
access_sms_provider_admin,sms.provider.admin,model_sms_provider,base.group_system,1,1,1,1
access_sms_template_user,sms.template.user,model_sms_template,base.group_user,1,1,1,1
access_sms_blacklist_user,sms.blacklist.user,model_sms_blacklist,base.group_user,1,1,1,1
EOF
    sudo cp /tmp/ir.model.access.csv ${MODULE_PATH}/security/ir.model.access.csv
    sudo chown odoo:odoo ${MODULE_PATH}/security/ir.model.access.csv
    echo '✅ ir.model.access.csv criado'
else
    echo '✅ ir.model.access.csv já existe'
fi
"

# 6. Limpar cache Python
echo ""
echo "6️⃣ Limpando cache Python..."
gcloud compute ssh ${SERVER} --zone=${ZONE} --command="
sudo rm -rf ${MODULE_PATH}/models/__pycache__
sudo rm -rf ${MODULE_PATH}/__pycache__
echo '✅ Cache limpo'
"

# 7. Verificar estrutura final
echo ""
echo "7️⃣ Verificando estrutura final..."
gcloud compute ssh ${SERVER} --zone=${ZONE} --command="
echo '📁 Estrutura do módulo:'
find ${MODULE_PATH} -type f -name '*.py' -o -name '*.xml' -o -name '*.csv' | sort
echo ''
echo '📊 Resumo:'
echo \"  Models: \$(find ${MODULE_PATH}/models -name '*.py' | grep -v __ | wc -l)\"
echo \"  Views: \$(find ${MODULE_PATH}/views -name '*.xml' | wc -l)\"
echo \"  Security: \$(find ${MODULE_PATH}/security -name '*.xml' -o -name '*.csv' | wc -l)\"
echo \"  Data: \$(find ${MODULE_PATH}/data -name '*.xml' | wc -l)\"
"

echo ""
echo "======================================"
echo "✅ MÓDULO SMS_CORE_UNIFIED COMPLETADO!"
echo ""
echo "📝 Próximos passos:"
echo "   1. Instalar módulo no Odoo"
echo "   2. Testar funcionalidades"
echo "   3. Validar envio de SMS"

