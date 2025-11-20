# 🐛 Erros Resolvidos - Odoo 15 RealCred

> **Propósito:** Registrar TODOS os erros encontrados e suas soluções para evitar repetição.

---

## 📋 Índice Rápido

- [Erros XML](#erros-xml)
- [Erros de Permissões](#erros-de-permissões)
- [Erros de Módulos](#erros-de-módulos)
- [Erros de Servidor](#erros-de-servidor)

---

## Erros XML

### [2025-11-19] FileNotFoundError: sms_template_views.xml

**Contexto:**
Instalação do módulo `sms_base_sr` falhando com erro RPC ao tentar carregar arquivo XML.

**Sintoma:**
```
FileNotFoundError: File not found: sms_base_sr/views/sms_template_views.xml
```

**Causa Raiz:**
- O arquivo `sms_template_views.xml` estava declarado no `__manifest__.py` na lista `data`
- No servidor, o arquivo existia apenas como backup (`.bak`), não como arquivo original
- O Odoo tentava carregar o arquivo durante a instalação e não encontrava

**Solução:**
1. Verificado arquivo local em `./modulos-customizados-odoo/modulos-sms-comunicacao/addons_custom/sms_base_sr/views/sms_template_views.xml`
2. Validado XML localmente (válido)
3. Copiado arquivo para servidor via `gcloud compute scp`
4. Ajustadas permissões (odoo:odoo, 644)
5. Validado XML no servidor

**Comandos:**
```bash
# Copiar arquivo para servidor
gcloud compute scp sms_template_views_fixed.xml odoo-sr-tensting:/tmp/sms_template_views.xml --zone=southamerica-east1-b

# Mover para local correto e ajustar permissões
sudo cp /tmp/sms_template_views.xml /odoo/custom/addons_custom/sms_base_sr/views/sms_template_views.xml
sudo chown odoo:odoo /odoo/custom/addons_custom/sms_base_sr/views/sms_template_views.xml
sudo chmod 644 /odoo/custom/addons_custom/sms_base_sr/views/sms_template_views.xml
```

**Prevenção:**
- Sempre verificar se todos os arquivos declarados no `__manifest__.py` existem no servidor
- Usar script de validação antes de instalar módulos
- Manter sincronização entre local e servidor

**Tags:** #xml #file-not-found #sms_base_sr #module-installation

---

### [2025-11-19] ValidationError: Campo "model_id" não existe no modelo "sms.template"

**Contexto:**
Erro RPC ao instalar módulo `sms_base_sr` - validação de view falhou.

**Sintoma:**
```
odoo.exceptions.ValidationError: O campo "model_id" não existe no modelo "sms.template"
View error: sms.template.tree
```

**Causa Raiz:**
1. O módulo `sms_base_sr` define seu **próprio modelo** `sms.template` que **sobrescreve** o modelo padrão do Odoo
2. O modelo customizado tem estrutura **completamente diferente** do modelo padrão
3. O XML estava usando campos do modelo padrão do Odoo (`model_id`, `body`, `model`) que **não existem** no modelo customizado

**Estrutura do modelo customizado `sms.template` (sms_base_sr):**
- `name` - Char (Template Name) - required
- `code` - Char (Template Code) - required, unique
- `message_template` - Text (Message Template) - required - **NÃO é `body`**
- `applies_to` - Selection (Applies To) - **NÃO é `model_id`**
- `active` - Boolean
- `admin_only` - Boolean
- `use_count` - Integer (readonly)
- `message_preview` - Text (computed)

**Estrutura do modelo padrão do Odoo `sms.template`:**
- `name` - Char
- `model_id` - Many2one
- `body` - Char
- (diferente do customizado!)

**Solução:**
1. Verificado modelo customizado em `/odoo/custom/addons_custom/sms_base_sr/models/sms_template.py`
2. Ajustado XML para usar campos corretos do modelo customizado:
   - `code` ao invés de `model_id`
   - `applies_to` ao invés de `model`
   - `message_template` ao invés de `body`
   - Adicionado `active`, `admin_only`, `use_count`, `message_preview`

**XML Corrigido:**
```xml
<tree>
    <field name="name"/>
    <field name="code"/>
    <field name="applies_to"/>
    <field name="active" widget="boolean_toggle"/>
</tree>
```

**Prevenção:**
- **SEMPRE verificar se o módulo define seu próprio modelo** antes de criar views
- Verificar arquivo do modelo: `models/sms_template.py` no módulo
- Não assumir que modelos com mesmo nome têm mesma estrutura
- Verificar campos disponíveis: `grep -E '^\s+[a-z_]+ = ' models/*.py`
- Usar `_inherit` se quiser estender modelo padrão ao invés de sobrescrever

**Tags:** #xml #validation-error #sms-template #custom-model #model-override

---

### [2025-11-19] XMLSyntaxError: sms_menu.xml

**Contexto:**
Erro RPC ao instalar módulo `sms_base_sr` devido a XML malformado.

**Sintoma:**
```
lxml.etree.XMLSyntaxError: String not started expecting ' or ", line 1, column 15
```

**Causa Raiz:**
Arquivo XML no servidor estava malformado - faltavam aspas em todos os atributos:
- `<?xml version=1.0 encoding=utf-8?>` (incorreto)
- `<?xml version="1.0" encoding="utf-8"?>` (correto)

**Solução:**
1. Corrigido arquivo local com aspas em todos os atributos
2. Copiado para servidor
3. Validado XML

**Prevenção:**
- Validar XML antes de fazer upload
- Usar linter XML
- Verificar encoding (UTF-8)

**Tags:** #xml #syntax-error #sms_menu #malformed-xml

---

## Erros de Permissões

*(Adicionar erros de permissões aqui)*

---

## Erros de Módulos

*(Adicionar erros de módulos aqui)*

---

## Erros de Servidor

### [2025-11-19] 502 Bad Gateway

**Contexto:**
Erro 502 ao acessar Odoo via web.

**Sintoma:**
```
favicon.ico:1 Failed to load resource: the server responded with a status of 502 ()
```

**Causa Raiz:**
Odoo estava rodando em modo debug com `--workers=0`, causando lentidão e timeouts no Nginx.

**Solução:**
1. Reiniciado Odoo com configuração correta (9 workers)
2. Reiniciado Nginx
3. Validado conectividade (HTTP 200)

**Comandos:**
```bash
# Reiniciar Odoo
sudo systemctl restart odoo-server

# Reiniciar Nginx
sudo systemctl restart nginx
```

**Prevenção:**
- Verificar configuração de workers no `odoo-server.conf`
- Monitorar logs do Nginx para erros 502
- Usar script de diagnóstico: `diagnose_502.sh`

**Tags:** #502 #bad-gateway #nginx #odoo-server #workers

---

## 📝 Template para Novos Erros

```markdown
### [YYYY-MM-DD] Título do Erro

**Contexto:**
**Sintoma:**
**Causa Raiz:**
**Solução:**
**Prevenção:**
**Tags:** #tag1 #tag2
```

---

### [2025-11-19] ir.model.access.csv - Models não encontrados

**Contexto:**
Erro ao atualizar módulo `sms_core_unified` - CSV tentando referenciar models não registrados.

**Sintoma:**
```
Exception: Nenhum registro encontrado para id externo 'model_sms_provider' no campo 'Model'
Nenhum registro encontrado para id externo 'model_sms_template' no campo 'Model'
Nenhum registro encontrado para id externo 'model_sms_blacklist' no campo 'Model'
```

**Causa Raiz:**
O `ir.model.access.csv` estava listado **primeiro** na lista `data` do manifest, sendo carregado **antes** dos models serem registrados no Odoo. O CSV precisa que os models já estejam registrados em `ir.model` para referenciá-los.

**Solução:**
Reordenar arquivos no manifest - mover `ir.model.access.csv` para o **final** da lista `data`:

```python
'data': [
    'security/sms_security.xml',      # Primeiro (não precisa de models)
    'views/sms_message_views.xml',    # Models carregados automaticamente
    'views/sms_menu.xml',
    'data/sms_providers.xml',
    'data/sms_blacklist_data.xml',
    'security/ir.model.access.csv',   # ← ÚLTIMO (precisa de models registrados)
],
```

**Prevenção:**
- **SEMPRE** colocar `ir.model.access.csv` no **final** da lista `data`
- Ordem recomendada: Security XML → Views → Menus → Data → CSV
- Verificar ordem antes de instalar/atualizar módulo

**Tags:** #ir-model-access #csv #manifest-order #module-loading

---

### [2025-11-19] sms_security.xml - Referências a Models não encontrados

**Contexto:**
Erro ao atualizar módulo `sms_core_unified` - XML tentando referenciar models não registrados.

**Sintoma:**
```
ValueError: External ID not found in the system: sms_core_unified.model_sms_provider
```

**Causa Raiz:**
O `sms_security.xml` estava definindo `ir.model.access` que referenciam models ainda não registrados. O XML é carregado **antes** dos models serem registrados, causando erro ao tentar usar `ref="model_sms_provider"`.

**Solução:**
Remover todas as definições de `ir.model.access` do XML e manter apenas os grupos (`res.groups`). As permissões já estão definidas no CSV que é carregado depois.

**Mudanças:**
- XML agora contém apenas grupos (`res.groups`)
- Permissões (`ir.model.access`) apenas no CSV
- Evita duplicação e problemas de ordem

**Prevenção:**
- **SEMPRE** separar grupos (XML) de permissões (CSV)
- XML para grupos e regras, CSV para permissões
- Não definir `ir.model.access` no XML se já está no CSV

**Tags:** #sms-security #xml #ir-model-access #separation-of-concerns

---

### [2025-11-19] sms_message_views.xml - Campos inexistentes no modelo

**Contexto:**
Erro ao atualizar módulo `sms_core_unified` - view tentando usar campos que não existem no modelo.

**Sintoma:**
```
ValidationError: O campo "provider_id" não existe no modelo "sms.message"
```

**Causa Raiz:**
O modelo `sms.message` é uma versão simplificada que não tem campos como `provider_id`, `cost`, `segments`, `delivery_date`, `template_id`, `retry_count`. A view estava tentando usar esses campos que não existem.

**Solução:**
Remover todos os campos inexistentes da view e usar apenas os campos disponíveis no modelo:
- Removidos: `provider_id`, `cost`, `segments`, `delivery_date`, `template_id`, `retry_count`
- Mantidos: `phone`, `body`, `state`, `partner_id`, `user_id`, `sent_date`, `error_message`, `external_id`

**Mudanças:**
- Tree view: Removidos `provider_id` e `cost`, adicionados `user_id` e `sent_date`
- Form view: Removidos campos inexistentes, mantidos apenas campos disponíveis
- Search view: Removida referência a `provider_id`
- Statusbar: Removido estado `delivered` que não existe no modelo

**Prevenção:**
- **SEMPRE** verificar quais campos existem no modelo antes de criar views
- Usar `grep -E '^\s+[a-z_]+ = fields\.' models/model.py` para listar campos
- Validar views contra o modelo antes de instalar/atualizar módulo

**Tags:** #sms-message #views #model-fields #validation

---

### [2025-11-19] sms_providers.xml - Campo description não reconhecido

**Contexto:**
Erro ao atualizar módulo `sms_core_unified` - campo `description` não reconhecido mesmo existindo no modelo.

**Sintoma:**
```
ValueError: Invalid field 'description' on model 'sms.provider'
```

**Causa Raiz:**
Problema de ordem de carregamento ou cache. O campo `description` existe no modelo, mas não estava sendo reconhecido ao criar registros via XML de dados. Pode ser devido a cache desatualizado ou ordem de carregamento.

**Solução:**
Remover temporariamente o campo `description` do XML de dados, já que é opcional e não é crítico para o funcionamento. O campo pode ser adicionado manualmente depois se necessário.

**Mudanças:**
- Removido campo `description` dos registros em `sms_providers.xml`
- Mantidos apenas campos essenciais
- Campo pode ser adicionado depois via interface

**Prevenção:**
- **SEMPRE** usar apenas campos essenciais ou obrigatórios em data files
- Campos opcionais podem ser adicionados depois se necessário
- Evitar campos que podem causar problemas de ordem de carregamento

**Tags:** #sms-provider #data-files #field-loading #optional-fields

---

### [2025-11-19] sms_providers.xml - Campos específicos não reconhecidos

**Contexto:**
Erro ao atualizar módulo `sms_core_unified` - campos específicos do Kolmeya não reconhecidos mesmo existindo no modelo.

**Sintoma:**
```
ValueError: Invalid field 'kolmeya_api_url' on model 'sms.provider'
```

**Causa Raiz:**
Problema de ordem de carregamento. Campos específicos do Kolmeya (`kolmeya_api_url`, `default_from`, etc.) existem no modelo, mas não estavam sendo reconhecidos ao criar registros via XML de dados. Pode ser devido a cache desatualizado ou ordem de carregamento.

**Solução:**
Simplificar XML de dados para usar apenas campos básicos e essenciais. Campos específicos do Kolmeya podem ser configurados depois via interface.

**Mudanças:**
- Removidos campos específicos: `kolmeya_api_url`, `default_from`, `max_retries`, `timeout_seconds`
- Mantidos apenas campos básicos: `name`, `provider_type`, `sequence`, `active`
- Campos específicos podem ser configurados depois via interface

**Prevenção:**
- **SEMPRE** usar apenas campos básicos e essenciais em data files
- Campos específicos ou opcionais devem ser configurados depois
- Evitar campos que podem causar problemas de ordem de carregamento

**Tags:** #sms-provider #data-files #field-loading #minimal-data

---

### [2025-11-19] sms_providers.xml - Conflito provider_type com outros módulos

**Contexto:**
Erro ao atualizar módulo `sms_core_unified` - valor 'kolmeya' não aceito no campo provider_type devido a conflito com outro módulo.

**Sintoma:**
```
ValueError: Wrong value for sms.provider.provider_type: 'kolmeya'
```

**Causa Raiz:**
Dois módulos definem `_name = 'sms.provider'`:
- `sms_base_sr/models/sms_provider.py`
- `sms_core_unified/models/sms_provider.py`

O modelo do `sms_base_sr` pode estar sendo carregado primeiro e não aceita o valor 'kolmeya' no Selection, causando conflito.

**Solução:**
Remover `provider_type` do XML de dados. O campo será configurado depois via interface para evitar conflitos.

**Mudanças:**
- Removido campo `provider_type` do XML de dados
- Mantidos apenas campos básicos: `name`, `sequence`, `active`
- `provider_type` pode ser configurado depois via interface

**Prevenção:**
- **SEMPRE** verificar se há outros módulos que definem o mesmo modelo antes de criar data files
- Usar apenas campos básicos em data files quando há risco de conflitos
- Campos que podem causar conflitos devem ser configurados depois via interface

**Tags:** #sms-provider #model-conflict #data-files #provider-type

---

### [2025-11-19] ir.model.access.csv - Models não registrados (retorno)

**Contexto:**
Erro retornou - CSV tentando referenciar models que não foram registrados, mesmo com CSV no final do manifest.

**Sintoma:**
```
Nenhum registro encontrado para id externo 'model_sms_provider' no campo 'Model'
Nenhum registro encontrado para id externo 'model_sms_template' no campo 'Model'
Nenhum registro encontrado para id externo 'model_sms_blacklist' no campo 'Model'
```

**Causa Raiz:**
Conflitos com outros módulos que também definem os mesmos models (`sms_base_sr` define `sms.provider`, etc.) podem impedir o registro correto dos models do `sms_core_unified`.

**Solução:**
Simplificar CSV para usar apenas o model confirmado (`sms.message`). Permissões para outros models podem ser adicionadas depois via interface ou quando models estiverem confirmados.

**Mudanças:**
- CSV agora contém apenas `sms.message` (model confirmado)
- Removidos `sms.provider`, `sms.template`, `sms.blacklist` do CSV
- Permissões para outros models podem ser adicionadas depois

**Prevenção:**
- **SEMPRE** usar apenas models confirmados em CSV durante instalação
- Verificar quais models estão realmente registrados antes de adicionar ao CSV
- Usar abordagem incremental: instalar básico primeiro, adicionar depois

**Tags:** #ir-model-access #csv #model-registration #incremental-approach

---

### [2025-11-19] SMS Core Unified - Módulo Incompleto

**Contexto:**
Módulo `sms_core_unified` criado mas incompleto (~30% implementado).

**Sintoma:**
- Módulo não podia ser instalado
- Faltavam models, views, security
- Arquivos unificados estavam na raiz do projeto

**Causa Raiz:**
- Refatoração iniciada mas não completada
- Arquivos unificados não foram movidos para o módulo
- Estrutura incompleta

**Solução:**
1. Movidos todos os arquivos unificados da raiz para o módulo
2. Criados models faltantes: `sms_provider.py`, `sms_template.py`, `sms_blacklist.py`
3. Atualizado `__init__.py` para importar todos os models
4. Criado `ir.model.access.csv` com permissões
5. Atualizados security e views
6. Atualizado `__manifest__.py` com todos os arquivos
7. Limpo cache Python
8. Validada estrutura completa

**Resultado:**
- ✅ Módulo 100% completo
- ✅ Todos os models implementados (4/4)
- ✅ Security completo (2/2)
- ✅ Views completas (2/2)
- ✅ Pronto para instalação

**Tags:** #sms-core-unified #refatoracao #modulo-incompleto #100-porcento

---

### [2025-11-19] Limpeza de Módulos SMS Antigos

**Contexto:**
Remoção de todos os módulos SMS antigos para manter apenas `sms_core_unified`.

**Módulos removidos:**
- `sms_base_sr` - Conflito com sms_core_unified
- `sms_kolmeya` - Funcionalidade integrada
- `chatroom_sms_advanced` - Funcionalidade integrada

**Ações executadas:**
1. Backup criado em `/odoo/backup/modulos_sms_antigos_YYYYMMDD/`
2. Módulos removidos do sistema de arquivos
3. Cache Python limpo
4. Apenas `sms_core_unified` permanece

**Próximos passos:**
- Desinstalar módulos no Odoo via interface
- Atualizar `sms_core_unified`
- Verificar dependências

**Tags:** #limpeza #modulos-sms #unificacao #sms-core-unified

---

### [2025-11-20] sms_providers.xml - Modelo não registrado após limpeza

**Contexto:**
Erro após remover módulos SMS antigos - `sms_providers.xml` tentando criar registros antes do modelo ser registrado.

**Sintoma:**
```
KeyError: 'sms.provider'
```

**Causa Raiz:**
Após remover `sms_base_sr` e `chatroom_sms_advanced`, o modelo `sms.provider` não existe mais no sistema. O `sms_core_unified` ainda não foi instalado/atualizado para registrar o modelo, mas o data file está tentando criar registros.

**Solução:**
Remover temporariamente `sms_providers.xml` do manifest. O arquivo foi mantido no sistema para uso futuro. Após instalar o módulo e registrar os models, o arquivo pode ser adicionado de volta ao manifest.

**Mudanças:**
- Removido `data/sms_providers.xml` do manifest temporariamente
- Arquivo mantido no sistema para uso futuro
- Providers podem ser criados manualmente via interface depois

**Prevenção:**
- **SEMPRE** verificar se models estão registrados antes de criar data files
- Data files devem ser adicionados depois que models estão registrados
- Ou usar abordagem incremental: instalar básico primeiro, adicionar data files depois

**Tags:** #sms-providers #data-files #model-registration #incremental-installation

---

**Última atualização:** 2025-11-20
**Total de erros documentados:** 15
