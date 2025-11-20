# 🔑 Informação: Senha do Usuário Admin

> **Data:** 2025-11-20
> **Pergunta:** Qual é a senha do usuário admin?

---

## ⚠️ Segurança

**As senhas no Odoo são armazenadas como hash criptografado no banco de dados.**

Não é possível recuperar a senha original, apenas:
- ✅ **Resetar** a senha para um novo valor
- ✅ **Verificar** se o usuário existe e está ativo

---

## 🔍 Como Verificar/Resetar a Senha

### **Opção 1: Via Interface Web**
1. Acesse a página de login
2. Clique em **"Esqueceu sua senha?"**
3. Digite o email do admin
4. Siga as instruções para resetar

### **Opção 2: Via Shell do Odoo**
```bash
cd /odoo/odoo-server
python3 odoo-bin shell -d testing -c /etc/odoo-server.conf
```

No shell Python:
```python
import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(['-c', '/etc/odoo-server.conf'])
registry = odoo.registry('testing')

with registry.cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    admin = env['res.users'].search([('login', '=', 'admin')], limit=1)
    if admin:
        admin.password = 'nova_senha_aqui'
        print(f"Senha do admin resetada!")
    else:
        print("Usuário admin não encontrado")
```

### **Opção 3: Via SQL (não recomendado)**
```sql
-- Resetar senha para 'admin' (hash bcrypt)
UPDATE res_users 
SET password_crypt = '$2b$10$...' 
WHERE login = 'admin';
```

---

## 📋 Verificar se Admin Existe

```sql
SELECT id, login, active, email 
FROM res_users 
WHERE login = 'admin';
```

---

## 🔒 Boas Práticas

1. ✅ **Não compartilhe senhas** em texto plano
2. ✅ **Use senhas fortes** (mínimo 8 caracteres, maiúsculas, números, símbolos)
3. ✅ **Altere senhas padrão** imediatamente após instalação
4. ✅ **Use autenticação de dois fatores** quando disponível

---

## 💡 Dica

Se você não sabe a senha do admin:
1. Use a opção "Esqueceu sua senha?" na interface web
2. Ou use o shell do Odoo para resetar
3. Ou entre em contato com o administrador do sistema

---

**Nota:** Por segurança, não é possível recuperar senhas antigas, apenas resetá-las.

