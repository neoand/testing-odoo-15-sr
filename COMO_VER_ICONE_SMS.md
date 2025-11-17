# 📱 Como Ver o Ícone do Módulo SMS

## ✅ Status Atual:

- Ícone SMS criado: `/odoo/custom/addons_custom/contact_center_sms/static/description/icon.png`
- Módulo instalado: `contact_center_sms`
- Odoo rodando normalmente

---

## 🔧 SOLUÇÕES PARA VER O ÍCONE:

### **Opção 1: Limpar Cache do Navegador** (MAIS RÁPIDO)

1. No Odoo (Apps page), pressione: **Ctrl + Shift + R** (Windows/Linux) ou **Cmd + Shift + R** (Mac)
   - Isso força recarregamento SEM cache

2. Se não funcionar, **apague cache completo**:
   - Chrome: ⚙️ > Mais ferramentas > Limpar dados de navegação
   - Marque "Imagens e arquivos em cache"
   - Período: "Última hora"
   - Click "Limpar dados"

3. **Feche e reabra o navegador**

4. Acesse novamente: https://odoo.semprereal.com/web#action=66&model=ir.module.module&view_type=kanban&menu_id=5

---

### **Opção 2: Atualizar Lista de Apps** (FORÇAR RELOAD)

1. Acesse: **Apps** (ícone de caixinhas no menu principal)

2. Click em **⚙️ (Configurações)** no canto superior direito

3. Click em **"Atualizar Lista de Apps"** (Update Apps List)

4. Aguarde processar (30 segundos)

5. Pesquise "Contact Center SMS" novamente

6. O ícone deve aparecer agora!

---

### **Opção 3: Ver Ícone Direto pela URL**

Acesse direto a URL do ícone no navegador:

```
https://odoo.semprereal.com/contact_center_sms/static/description/icon.png
```

Se aparecer o ícone, está funcionando! O problema é só cache do browser.

---

### **Opção 4: Modo Incógnito / Privado**

1. Abra janela anônima: **Ctrl + Shift + N** (Chrome) ou **Ctrl + Shift + P** (Firefox)

2. Faça login no Odoo

3. Vá em Apps

4. Pesquise "Contact Center SMS"

5. O ícone deve aparecer (sem cache)

---

## 🎯 Como Saber se Funcionou:

**ANTES** (ícone quebrado):
```
📱 [ícone genérico cinza]
```

**DEPOIS** (ícone correto):
```
💬 [ícone colorido de SMS/mensagem]
```

---

## 📊 Verificação Técnica:

Se quiser confirmar que o ícone existe no servidor:

```bash
ssh odoo-rc "ls -lh /odoo/custom/addons_custom/contact_center_sms/static/description/icon.png"
```

Deve mostrar:
```
-rw-r--r-- 1 odoo odoo 1.6K Nov 16 01:57 icon.png
```

---

## ⚠️ Se AINDA NÃO APARECER:

### Reinstalar Módulo (Último Recurso):

1. Apps > Contact Center SMS Integration

2. Click em **"Desinstalar"** (Uninstall)

3. Aguarde desinstalação

4. Pesquise novamente "Contact Center SMS"

5. Click em **"Instalar"** (Install)

6. Aguarde instalação

7. Limpe cache do navegador (Ctrl + Shift + R)

---

## 🔍 Debug - Verificar URL do Ícone:

No console do navegador (F12), rode:

```javascript
fetch('https://odoo.semprereal.com/contact_center_sms/static/description/icon.png')
  .then(r => console.log('Status:', r.status, r.ok ? '✅ OK' : '❌ ERRO'))
```

Deve mostrar: `Status: 200 ✅ OK`

---

## ✅ RESUMO RÁPIDO:

1. **Ctrl + Shift + R** na página de Apps
2. Se não funcionar: Limpar cache completo do navegador
3. Se ainda não: Atualizar Lista de Apps via ⚙️
4. Último caso: Reinstalar módulo

**O ícone ESTÁ no servidor e acessível!** É questão de cache do browser.

---

**Criado em:** 2025-11-16 02:20 UTC
**Localização do ícone:** `/odoo/custom/addons_custom/contact_center_sms/static/description/icon.png`
**URL pública:** https://odoo.semprereal.com/contact_center_sms/static/description/icon.png
