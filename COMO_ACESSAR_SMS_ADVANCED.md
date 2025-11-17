# 🎯 COMO ACESSAR O MÓDULO SMS ADVANCED

## ✅ Status: Módulo INSTALADO e Permissão CONFIGURADA

---

## 📍 PASSO A PASSO PARA ACESSAR

### 1. LIMPAR CACHE DO NAVEGADOR

**IMPORTANTE:** Odoo usa muito cache. Você precisa limpar:

**Opção A - Hard Refresh (RECOMENDADO):**
```
Windows/Linux: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

**Opção B - Limpar cache manual:**
1. Chrome: Ctrl+Shift+Delete > Limpar cache
2. Firefox: Ctrl+Shift+Delete > Limpar cache
3. Safari: Cmd+Option+E

---

### 2. FAZER LOGOUT E LOGIN NOVAMENTE

**Motivo:** O Odoo carrega permissões no login. Você precisa relogar para as novas permissões aparecerem.

**Como fazer:**
1. Clicar no seu nome (canto superior direito)
2. Clicar em "Log out"
3. Fazer login novamente com admin

---

### 3. ONDE ENCONTRAR O MENU

Após relogar, o menu **"SMS Advanced"** deve aparecer na **barra de menus principal** do Odoo.

**Localização:**
```
Barra de menus (topo da página)
├── Discuss
├── Calendar
├── Contacts
├── Sales
├── ...
├── SMS Advanced  ← AQUI! (pode estar no final)
└── ...
```

**Ícone:** Pode aparecer com ícone de SMS ou mensagem

---

### 4. SE AINDA NÃO APARECER - VERIFICAÇÃO MANUAL

#### Opção A: Buscar via Apps

1. Clicar no **ícone de 9 quadradinhos** (App Switcher) no canto superior esquerdo
2. Digitar "SMS" na busca
3. Deve aparecer "SMS Advanced"

#### Opção B: Acessar via URL Direta

Abrir no navegador:
```
https://seu-odoo.com.br/web#menu_id=936
```

Substitua `seu-odoo.com.br` pela URL do seu Odoo.

O número **936** é o ID do menu SMS Advanced.

---

### 5. SUBMENUS DISPONÍVEIS

Quando você clicar em "SMS Advanced", verá:

```
SMS Advanced
├── Dashboard          (Kanban com 3 cards + gráficos)
├── Campaigns          (Gerenciar campanhas)
├── Scheduled SMS      (SMS agendados)
├── Send Bulk SMS      (Envio em massa)
└── Configuration
    ├── Blacklist
    ├── Templates
    └── Providers
```

---

## 🔧 TROUBLESHOOTING

### Problema 1: "Menu não aparece mesmo após limpar cache"

**Solução 1 - Verificar modo desenvolvedor:**
```
1. Settings > Activate Developer Mode
2. Recarregar página (F5)
3. Verificar se apareceu
```

**Solução 2 - Forçar atualização de assets:**
```
1. Settings > Developer Mode > Activate Assets Debug Mode
2. Limpar cache do navegador
3. Fazer Hard Refresh (Ctrl+Shift+R)
```

**Solução 3 - Reiniciar Odoo (se necessário):**
```bash
ssh odoo-rc "sudo systemctl restart odoo-server"
```

Aguardar 30 segundos e recarregar página.

---

### Problema 2: "Menu aparece mas dá erro ao clicar"

**Solução - Ver logs de erro:**

Abrir console do navegador:
- Chrome/Firefox: F12 > Console
- Procurar erros em vermelho
- Me enviar o erro exato

---

### Problema 3: "Vejo o menu mas está vazio/sem dados"

**Normal!** O módulo acabou de ser instalado.

**Para popular com dados:**
1. Ir em "Campaigns" > Create
2. Criar primeira campanha de teste
3. Ou ir em "Send Bulk SMS" para envio rápido

---

## ✅ CONFIRMAÇÃO TÉCNICA

### Módulo Instalado:
```
Nome: chatroom_sms_advanced
Versão: 15.0.2.0.0
Estado: installed
```

### Grupo Adicionado ao Admin:
```
Grupo: SMS Advanced Manager
Usuário: admin
Status: ATIVO
```

### Menu Criado:
```
ID: 936
Nome: SMS Advanced
Parent: (raiz - menu principal)
Submenus: 5 (Dashboard, Campaigns, Scheduled, Bulk Send, Config)
```

---

## 📱 ACESSO RÁPIDO POR URL

Se preferir, pode acessar diretamente cada funcionalidade:

### Dashboard
```
/web#action=XXX&model=sms.dashboard
```

### Campanhas
```
/web#action=XXX&model=sms.campaign
```

### SMS Agendados
```
/web#action=XXX&model=sms.scheduled
```

### Blacklist
```
/web#action=XXX&model=sms.blacklist
```

*(Substitua XXX pelo action_id correto - vou buscar para você se precisar)*

---

## 🎨 APARÊNCIA ESPERADA

### Dashboard (primeira tela):
```
┌─────────────────────────────────────────┐
│         SMS Advanced Dashboard          │
├─────────────────────────────────────────┤
│  ┌──────┐  ┌──────┐  ┌──────┐          │
│  │ Card │  │ Card │  │ Card │          │
│  │  1   │  │  2   │  │  3   │          │
│  └──────┘  └──────┘  └──────┘          │
├─────────────────────────────────────────┤
│         📊 Gráficos e Estatísticas      │
└─────────────────────────────────────────┘
```

### Campanhas:
```
Lista de campanhas com:
- Nome da campanha
- Provider (Kolmeya)
- Status (Draft/Running/Done)
- Estatísticas (Sent/Delivered/Failed)
- Botão "Send Campaign"
```

---

## 📞 SE NADA FUNCIONAR

Envie para mim:

1. **Screenshot** da barra de menus do Odoo
2. **Console do navegador** (F12 > Console) com erros
3. **URL** que você está usando para acessar

E eu vou investigar mais a fundo!

---

## 🎉 PRÓXIMOS PASSOS (quando conseguir acessar)

1. **Testar Dashboard:**
   - Clicar em SMS Advanced > Dashboard
   - Ver os 3 cards no topo
   - Experimentar trocar para view Graph/Pivot

2. **Criar Primeira Campanha:**
   - SMS Advanced > Campaigns > Create
   - Preencher nome e template
   - Selecionar alguns parceiros
   - Save e "Send Campaign"

3. **Enviar SMS em Massa:**
   - Ir em Contacts
   - Selecionar vários contatos
   - Action > Send Bulk SMS
   - Escolher template
   - Send

---

**Desenvolvido por:** Anderson Oliveira + Claude AI
**Data:** 16/11/2025
**Suporte:** Este documento

---

## ⚡ COMANDO RÁPIDO (SE NECESSÁRIO)

Se precisar adicionar o grupo manualmente via SQL novamente:

```sql
-- Conectar ao PostgreSQL
ssh odoo-rc "sudo -u postgres psql realcred"

-- Verificar se admin tem o grupo
SELECT p.name, g.name as grupo
FROM res_users u
JOIN res_partner p ON p.id = u.partner_id
JOIN res_groups_users_rel r ON r.uid = u.id
JOIN res_groups g ON g.id = r.gid
WHERE u.login = 'admin' AND g.name LIKE '%SMS%Advanced%';

-- Se não aparecer nada, adicionar:
INSERT INTO res_groups_users_rel (gid, uid)
SELECT g.id, u.id
FROM res_groups g, res_users u
WHERE g.name = 'SMS Advanced Manager'
  AND u.login = 'admin'
  AND NOT EXISTS (
      SELECT 1 FROM res_groups_users_rel
      WHERE gid = g.id AND uid = u.id
  );
```

---

**FAÇA AGORA:**
1. ✅ Limpar cache do navegador (Ctrl+Shift+R)
2. ✅ Fazer logout
3. ✅ Fazer login novamente
4. ✅ Procurar "SMS Advanced" no menu principal

**Se aparecer:** 🎉 Sucesso! Comece a usar!
**Se não aparecer:** Me envie screenshot + console errors
