# 🔧 Correção FileNotFoundError: sms_template_views.xml - 19/11/2025

## 📋 Problema Identificado

**Erro RPC:** `FileNotFoundError: File not found: sms_base_sr/views/sms_template_views.xml`

**Contexto:** Instalação do módulo `sms_base_sr` falhando durante carregamento de dados XML.

## 🔍 Causa Raiz

1. O arquivo `sms_template_views.xml` estava **declarado** no `__manifest__.py`:
   ```python
   'data': [
       'views/sms_template_views.xml',  # ← Declarado aqui
       ...
   ],
   ```

2. No servidor, o arquivo **não existia** como arquivo original:
   - Existia apenas como backup: `sms_template_views.xml.bak`
   - O Odoo tentava carregar e não encontrava

3. O arquivo existia **localmente** e estava correto

## ✅ Solução Aplicada

### 1. Verificação
- ✅ Arquivo local existe e está válido
- ✅ XML bem formado
- ✅ Declarado corretamente no manifest

### 2. Correção
```bash
# 1. Copiar arquivo local para servidor
gcloud compute scp sms_template_views_fixed.xml \
  odoo-sr-tensting:/tmp/sms_template_views.xml \
  --zone=southamerica-east1-b

# 2. Mover para local correto
sudo cp /tmp/sms_template_views.xml \
  /odoo/custom/addons_custom/sms_base_sr/views/sms_template_views.xml

# 3. Ajustar permissões
sudo chown odoo:odoo \
  /odoo/custom/addons_custom/sms_base_sr/views/sms_template_views.xml
sudo chmod 644 \
  /odoo/custom/addons_custom/sms_base_sr/views/sms_template_views.xml

# 4. Validar XML
python3 -c "import xml.etree.ElementTree as ET; \
  ET.parse('/odoo/custom/addons_custom/sms_base_sr/views/sms_template_views.xml'); \
  print('✅ XML válido!')"
```

### 3. Resultado
- ✅ Arquivo criado no servidor
- ✅ Permissões corretas (odoo:odoo, 644)
- ✅ XML validado e bem formado
- ✅ Módulo pode ser instalado agora

## 📝 Arquivo Corrigido

O arquivo `sms_template_views.xml` contém:
- Views para `sms.template` (modelo padrão do Odoo)
- Tree view e form view
- Action e menu item
- Usa campos padrão: `name`, `model_id`, `model`, `lang`, `body`

## 🔄 Próximos Passos

1. **Reinstalar o módulo** `sms_base_sr` no Odoo
2. **Verificar se não há outros arquivos faltando** no módulo
3. **Testar funcionalidade** de templates SMS

## 🚀 Comandos para Reinstalar

```bash
# Via interface web Odoo:
# Apps > sms_base_sr > Desinstalar > Instalar

# Ou via linha de comando:
gcloud compute ssh odoo-sr-tensting --zone=southamerica-east1-b \
  --command="cd /odoo/odoo-server && sudo -u odoo python3 odoo-bin \
  -c /etc/odoo-server.conf -d testing -u sms_base_sr --stop-after-init"
```

## 📊 Status

| Item | Status |
|------|--------|
| Arquivo criado no servidor | ✅ |
| Permissões corretas | ✅ |
| XML válido | ✅ |
| Módulo pode ser instalado | ✅ |
| Módulo reinstalado | ⏳ Pendente |

## 🔍 Verificação

Para verificar se o arquivo está correto:

```bash
# Verificar existência
ls -la /odoo/custom/addons_custom/sms_base_sr/views/sms_template_views.xml

# Validar XML
python3 -c "import xml.etree.ElementTree as ET; \
  ET.parse('/odoo/custom/addons_custom/sms_base_sr/views/sms_template_views.xml')"

# Verificar permissões
stat /odoo/custom/addons_custom/sms_base_sr/views/sms_template_views.xml
```

## 📅 Data da Correção
**19 de Novembro de 2025 - 18:33 UTC**

---

**Criado por:** Cursor AI + Anderson  
**Documentado em:** `.cursor/memory/errors/ERRORS-SOLVED.md`

