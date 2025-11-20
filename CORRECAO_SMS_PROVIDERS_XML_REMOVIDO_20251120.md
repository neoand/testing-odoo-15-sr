# 🔧 Correção: sms_providers.xml Removido Temporariamente

> **Data:** 2025-11-20
> **Erro:** `KeyError: 'sms.provider'` - Modelo não registrado

---

## 📋 Problema Identificado

**Erro RPC:** O arquivo `sms_providers.xml` estava tentando criar registros do modelo `sms.provider` antes que o modelo fosse registrado no sistema.

**Sintoma:**
```
KeyError: 'sms.provider'
```

**Causa:** Após remover os módulos antigos (`sms_base_sr`, `chatroom_sms_advanced`), o modelo `sms.provider` não existe mais no sistema. O `sms_core_unified` ainda não foi instalado/atualizado para registrar o modelo.

---

## ✅ Solução Aplicada

### Remover sms_providers.xml do Manifest Temporariamente

**Antes (Incorreto):**
```python
'data': [
    'security/sms_security.xml',
    'views/sms_message_views.xml',
    'views/sms_menu.xml',
    'data/sms_providers.xml',  # ← Causa erro (modelo não registrado)
    'data/sms_blacklist_data.xml',
    'security/ir.model.access.csv',
],
```

**Depois (Correto):**
```python
'data': [
    'security/sms_security.xml',
    'views/sms_message_views.xml',
    'views/sms_menu.xml',
    # Data files (removido sms_providers.xml temporariamente)
    'data/sms_blacklist_data.xml',
    'security/ir.model.access.csv',
],
```

**Por quê:**
1. O modelo `sms.provider` precisa ser registrado primeiro
2. Data files são carregados durante instalação/atualização
3. Se o modelo não existe, o data file falha
4. Removendo temporariamente, o módulo pode ser instalado
5. Depois de instalado, o modelo será registrado
6. Então podemos adicionar o data file de volta

---

## 🔄 Processo de Instalação

### Fase 1: Instalação Inicial (Agora)

1. **Instalar módulo** sem `sms_providers.xml`
2. **Modelos serão registrados** (`sms.provider`, `sms.template`, etc.)
3. **Módulo funcionará** com funcionalidades básicas

### Fase 2: Adicionar Providers (Depois)

1. **Adicionar `sms_providers.xml` de volta** ao manifest
2. **Atualizar módulo**
3. **Providers serão criados** automaticamente

**OU**

1. **Criar providers manualmente** via interface
2. **Configurar** `kolmeya_api_url`, `default_from`, etc.

---

## 📝 Arquivo sms_providers.xml

**Status:** Arquivo mantido no sistema, apenas removido do manifest

**Localização:** `/odoo/custom/addons_custom/sms_core_unified/data/sms_providers.xml`

**Conteúdo:**
```xml
<record id="sms_provider_kolmeya_default" model="sms.provider">
    <field name="name">Kolmeya - Production</field>
    <field name="sequence">10</field>
    <field name="active" eval="True"/>
</record>
```

**Quando adicionar de volta:**
- Após instalar/atualizar o módulo pela primeira vez
- Quando o modelo `sms.provider` estiver registrado
- Adicionar de volta ao manifest e atualizar

---

## ✅ Status

- ✅ Manifest atualizado (sms_providers.xml removido)
- ✅ Arquivo mantido no sistema (para uso futuro)
- ✅ Módulo pode ser instalado agora
- ✅ Providers podem ser criados manualmente depois

---

## 🔄 Próximos Passos

1. **Instalar/Atualizar módulo:**
   - Deve funcionar agora sem o data file

2. **Verificar models registrados:**
   - Settings > Technical > Database Structure > Models
   - Verificar se `sms.provider` está registrado

3. **Adicionar providers:**
   - Via interface: SMS > Providers > Criar
   - OU adicionar `sms_providers.xml` de volta ao manifest e atualizar

---

**Criado em:** 2025-11-20
**Status:** ✅ Correção Aplicada

