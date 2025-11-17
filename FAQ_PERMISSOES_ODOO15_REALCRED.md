# FAQ - SISTEMA DE PERMISSÕES ODOO 15 REALCRED

**Versão:** 1.0
**Data:** 17/11/2025
**Público:** Usuários, Gerentes e Administradores
**Status:** ✅ Atualizado após FASE 1 de Reorganização

---

## 📋 ÍNDICE

1. [Perguntas Gerais](#perguntas-gerais)
2. [Perfis e Grupos de Acesso](#perfis-e-grupos-de-acesso)
3. [Módulos Específicos](#módulos-específicos)
4. [Problemas Comuns](#problemas-comuns)
5. [Solicitações e Mudanças](#solicitações-e-mudanças)
6. [Para Administradores](#para-administradores)

---

## 🔰 PERGUNTAS GERAIS

### 1. O que são permissões no Odoo?

Permissões controlam **o que você pode ver e fazer** no sistema Odoo. Elas determinam:
- Quais menus você vê
- Quais registros você pode visualizar
- Se você pode criar novos registros
- Se você pode editar registros existentes
- Se você pode deletar registros

### 2. Como sei qual é meu nível de acesso?

Para ver suas permissões:
1. Clique no seu **nome** no canto superior direito
2. Selecione **"Meu Perfil"** ou **"Preferências"**
3. Role até a seção **"Direitos de Acesso"**
4. Você verá todos os grupos dos quais faz parte

Alternativamente, se você **NÃO consegue ver um menu** que precisa, provavelmente não tem permissão para aquele módulo.

### 3. Por que não consigo ver um menu que meu colega vê?

Isso acontece porque vocês têm **grupos de acesso diferentes**. O Odoo mostra menus baseado nas suas permissões.

**Exemplo:**
- Vendedor vê: Menus de CRM e Vendas
- Financeiro vê: Menus de Faturamento e Contabilidade
- RH vê: Menus de Funcionários e Férias

### 4. Posso ter múltiplas permissões ao mesmo tempo?

**Sim!** Um usuário pode ter permissões em vários módulos simultaneamente.

**Exemplo:**
- João pode ser **Vendedor** (vê CRM) E **Usuário de RH** (vê férias)
- Maria pode ser **Líder de Vendas** (vê time todo) E ter acesso a **Relatórios Financeiros**

### 5. O que significa "Own Documents Only" vs "All Documents"?

| Tipo | O que você vê | Exemplo |
|------|---------------|---------|
| **Own Documents Only** | Apenas SEUS registros | Você só vê suas próprias oportunidades |
| **All Documents** | Registros do SEU TIME | Você vê todas as oportunidades do seu time |
| **Administrator** | TUDO | Você vê todas as oportunidades de todos os times |

---

## 👥 PERFIS E GRUPOS DE ACESSO

### 6. Quais são os perfis disponíveis para VENDAS?

| Perfil | Grupo Odoo | O que você vê/faz |
|--------|-----------|-------------------|
| **Vendedor Básico** | User: Own Documents Only | ✅ Vê apenas SUAS oportunidades<br>✅ Pode criar/editar/deletar SUAS oportunidades<br>❌ NÃO vê oportunidades de outros |
| **Vendedor Pleno / Líder** | User: All Documents | ✅ Vê TODAS as oportunidades do TIME<br>✅ Pode criar/editar/deletar do time<br>✅ Pode reatribuir oportunidades |
| **Gerente de Vendas** | Administrator | ✅ Vê TODAS as oportunidades (todos os times)<br>✅ Acesso total (CRUD)<br>✅ Pode configurar estágios, times, etc. |
| **Operacional** | Operacional (custom) | ✅ Vê TODAS as oportunidades CRM<br>✅ Vê TODOS os pedidos de venda<br>❌ NÃO pode deletar pedidos (só CRU) |

### 7. Quem pode acessar o módulo de CONTATOS?

**TODOS os usuários internos** têm acesso completo (criar/editar/deletar) aos contatos.

**Por quê?** Contatos são compartilhados entre TODOS os departamentos:
- Vendas precisa dos contatos dos clientes
- Financeiro precisa para emitir faturas
- RH pode precisar de contatos de candidatos
- Operações precisa de fornecedores

### 8. Quem pode acessar o módulo de RH?

**Apenas:**
- ✅ Equipe de RH (grupos: HR PRO / Manager, Employees / Administrator)
- ✅ Administrador do sistema

**Usuários comuns NÃO vêem:**
- ❌ Dados de outros funcionários
- ❌ Salários
- ❌ Avaliações de desempenho
- ❌ Férias de outros

**Exceção:** Você sempre pode ver e gerenciar suas PRÓPRIAS férias e dados pessoais.

### 9. Quem pode acessar dados FINANCEIROS?

| Perfil | O que vê |
|--------|----------|
| **Accountant (Contador)** | ✅ Todas as faturas, pagamentos, lançamentos contábeis<br>✅ Pode ler CRM (para saber contexto de vendas)<br>✅ Acesso total a módulos financeiros |
| **Billing (Faturamento)** | ✅ Pode criar e enviar faturas<br>⚠️ Acesso limitado a contabilidade |
| **Auditor** | ✅ Apenas leitura de tudo financeiro<br>❌ NÃO pode editar nada |
| **Vendedor** | ⚠️ Vê apenas valores de SUAS vendas<br>❌ NÃO vê contabilidade geral |

### 10. O que é um "Administrador"?

**Administrador** (Settings / Administration) tem **ACESSO TOTAL** ao sistema:
- ✅ Vê todos os menus
- ✅ Vê todos os registros (de todos os usuários)
- ✅ Pode criar/editar/deletar qualquer coisa
- ✅ Pode instalar/desinstalar módulos
- ✅ Pode gerenciar usuários e permissões
- ✅ Pode acessar configurações técnicas

⚠️ **ATENÇÃO:** Poder deve ser usado com responsabilidade!

---

## 📦 MÓDULOS ESPECÍFICOS

### 11. Por que não consigo criar uma oportunidade no CRM?

**Possíveis causas:**

#### A) Você não tem o grupo de Vendas
**Solução:** Solicite ao TI para adicionar você ao grupo "Sales / User"

#### B) Você tem "Own Documents Only" mas a oportunidade está sem vendedor
**Solução:** Ao criar, sempre preencha o campo "Vendedor" com SEU nome

#### C) Bug na configuração (corrigido em 17/11/2025)
**Se você tinha esse problema ANTES de 17/11:** Era um bug nas regras de permissão. Foi corrigido na Fase 1 de reorganização.

### 12. Por que não consigo ver pedidos de venda?

Você precisa ter o grupo **"Sales / User"** para ver o módulo de Vendas.

**Verificar:**
1. Vá em seu perfil → Direitos de Acesso
2. Procure por "Sales / User: Own Documents Only" ou "Sales / User: All Documents"
3. Se não tiver, solicite ao TI

### 13. Por que não consigo deletar um pedido de venda?

**Isso é proposital por segurança!**

Apenas **Gerentes de Vendas** (Sales / Administrator) podem deletar pedidos.

**Perfil "Operacional"** pode criar/editar pedidos mas **NÃO pode deletar** (para evitar exclusões acidentais).

**Se realmente precisa deletar:** Solicite a um gerente.

### 14. Por que não vejo dados de RH?

**Acesso a RH é restrito.** Apenas a equipe de RH e administradores vêem:
- Dados de funcionários
- Salários
- Férias de outros
- Avaliações

**Você PODE ver:**
- ✅ Seus próprios dados
- ✅ Suas próprias férias
- ✅ Suas próprias avaliações

### 15. Posso ver quanto meus colegas ganham?

**NÃO**, a menos que você seja:
- ✅ Da equipe de RH
- ✅ Administrador do sistema
- ✅ Diretor/Gerente com permissão específica

Dados salariais são **altamente confidenciais**.

---

## 🔧 PROBLEMAS COMUNS

### 16. Erro: "Você não tem permissão para executar esta ação"

**Causas comuns:**

#### A) Você não tem o grupo necessário
**Solução:** Identifique qual módulo/ação você estava tentando e solicite permissão ao TI

#### B) Você tem "Own Documents" mas está tentando editar registro de outro
**Solução:** Peça ao dono do registro para fazer a edição, ou solicite ao TI para mudar para "All Documents"

#### C) O registro está bloqueado (ex: pedido confirmado)
**Solução:** Alguns registros são bloqueados após confirmação. Cancele primeiro, depois edite.

### 17. Não consigo adicionar um usuário a um grupo

Apenas **Administradores** podem gerenciar usuários e grupos.

Se você não é administrador, solicite ao TI.

### 18. Minhas permissões mudaram e não sei por quê

**Possíveis causas:**

#### A) Reorganização de grupos (Fase 1 - 17/11/2025)
Houve uma limpeza massiva de permissões. Se você perdeu acesso a algo que tinha antes, contate o TI.

#### B) Seu cargo/função mudou
Gerentes podem ter ajustado suas permissões. Verifique com seu superior.

#### C) Mudança de equipe
Se você mudou de equipe de vendas, por exemplo, pode ver registros diferentes agora.

### 19. Cache: Mudaram minha permissão mas ainda não funciona

Às vezes o navegador **guarda informações antigas** (cache).

**Solução:**
1. **Faça logout** do Odoo
2. **Feche completamente o navegador**
3. **Reabra** o navegador
4. **Faça login** novamente

**Ou:**
1. Pressione **Ctrl + Shift + R** (Windows) ou **Cmd + Shift + R** (Mac) para forçar atualização

### 20. Ainda tenho problemas após limpar cache

**Passos:**
1. Verifique se você REALMENTE tem a permissão (Meu Perfil → Direitos de Acesso)
2. Se não tiver, solicite ao TI
3. Se tiver mas não funciona, pode ser um bug → contate TI imediatamente

---

## 📝 SOLICITAÇÕES E MUDANÇAS

### 21. Como solicito uma nova permissão?

**Passo a passo:**

1. **Identifique o que você precisa**
   - Qual módulo? (CRM, Vendas, RH, Financeiro, etc.)
   - Qual nível? (Ver apenas seus registros, do time, ou tudo?)
   - Pode editar? Pode criar? Pode deletar?

2. **Justifique a necessidade**
   - Por que você precisa dessa permissão?
   - Qual tarefa você não consegue fazer sem ela?

3. **Abra um chamado com TI**
   - Email: ti@semprereal.com
   - Inclua: Seu nome, módulo necessário, justificativa

4. **Aguarde aprovação**
   - TI pode pedir aprovação do seu gestor
   - Permissões são concedidas em até 24-48h

### 22. Meu pedido de permissão foi negado. Por quê?

**Razões comuns:**

#### A) Segregação de funções
Exemplo: Quem cria pedidos não deve aprovar pagamentos (segurança financeira)

#### B) Dados confidenciais
Exemplo: Salários, margens de lucro, dados pessoais de funcionários

#### C) Risco de erro
Exemplo: Permissão de deletar dados críticos é restrita para evitar perdas

#### D) Não faz parte da sua função
Se você é vendedor, provavelmente não precisa de acesso a contabilidade avançada

**Se discordar:** Converse com seu gestor para escalação.

### 23. Posso ter uma permissão "temporária"?

**Sim!** Para projetos específicos ou substituições.

**Exemplo:**
- Você está substituindo o gerente de vendas por 2 semanas
- TI pode dar permissão "Sales / Administrator" temporariamente
- Após 2 semanas, TI remove e você volta ao perfil normal

**Como solicitar:** Inclua no chamado que é temporário e por quanto tempo.

### 24. Como sei quem tem acesso ao quê?

**Apenas administradores** podem ver lista completa de permissões de todos.

**Você pode ver:**
- ✅ Suas próprias permissões
- ❌ Permissões de outros usuários (privacidade)

**Se é gerente e precisa saber:** Solicite ao TI relatório de permissões da sua equipe.

### 25. Mudei de cargo. Como atualizo minhas permissões?

**Processo:**

1. **Seu gestor** deve notificar o TI sobre mudança de cargo
2. **TI** ajusta suas permissões para o novo perfil
3. **Você** faz logout e login novamente
4. **Validação:** Verifique se tem acesso aos novos módulos

**Importante:** Permissões antigas do cargo anterior podem ser removidas!

---

## 🛠️ PARA ADMINISTRADORES

### 26. Como adiciono um usuário a um grupo?

**Via Interface:**
1. Configurações → Usuários & Empresas → Usuários
2. Clique no usuário
3. Tab "Direitos de Acesso"
4. Marque os grupos necessários
5. Salvar

**Via SQL (avançado):**
```sql
INSERT INTO res_groups_users_rel (uid, gid)
VALUES (<user_id>, <group_id>);
```

### 27. Qual é a diferença entre Access Rights e Record Rules?

| | Access Rights | Record Rules |
|---|---------------|--------------|
| **O quê** | Permissão de MODELO inteiro | Filtro de REGISTROS específicos |
| **Exemplo** | Grupo "Vendas" pode ler `crm.lead` | Vendedor só vê leads onde `user_id = ele mesmo` |
| **Nível** | CRUD (Create, Read, Update, Delete) | Domínio (condições) |
| **Onde configurar** | `ir.model.access.csv` | `security.xml` (ir.rule) |

**Analogia:**
- **Access Rights:** Chave do prédio (você pode entrar?)
- **Record Rules:** Chave dos apartamentos (quais apartamentos você pode abrir?)

### 28. Como crio um novo perfil/grupo?

**Via Módulo Customizado:**

1. Criar módulo: `/odoo/custom/addons_custom/meu_modulo/`
2. Criar arquivo: `security/security.xml`

```xml
<record id="group_meu_perfil" model="res.groups">
    <field name="name">Meu Perfil</field>
    <field name="category_id" ref="base.module_category_sales_sales"/>
    <field name="implied_ids" eval="[(4, ref('base.group_user'))]"/>
    <field name="comment">Descrição do perfil aqui</field>
</record>
```

3. Criar access rights: `security/ir.model.access.csv`
4. Instalar módulo

**IMPORTANTE:** Sempre documente o grupo (campo `comment`)!

### 29. Como faço rollback de permissões?

**Se você fez backup (recomendado):**

```sql
-- Restaurar ir_rule
DELETE FROM ir_rule;
INSERT INTO ir_rule SELECT * FROM ir_rule_backup_fase1_20251116;

-- Restaurar ir_model_access
DELETE FROM ir_model_access;
INSERT INTO ir_model_access SELECT * FROM ir_model_access_backup_fase1_20251116;

-- Restaurar res_groups_users_rel
DELETE FROM res_groups_users_rel;
INSERT INTO res_groups_users_rel SELECT * FROM res_groups_users_rel_backup_fase1_20251116;

-- Reiniciar Odoo
```

**Backup de 17/11/2025 está em:**
- Database: `/home/andlee21/backups/fase1_permissions_20251116_184902/realcred_database.sql.gz`
- Tabelas: `ir_rule_backup_fase1_20251116`, `ir_model_access_backup_fase1_20251116`, etc.

### 30. Quais foram as mudanças da Fase 1 (17/11/2025)?

**Resumo da Fase 1:**

| Ação | Antes | Depois | Impacto |
|------|-------|--------|---------|
| **Record Rules Bugadas** | 2 (IDs 443, 444) | 0 corrigidas | ✅ Usuários podem criar oportunidades normalmente |
| **Access Rights Duplicados** | 16 | 0 | ✅ Comportamento consistente |
| **Access Rights Inúteis** | 57 | 0 | ✅ Banco limpo, melhor performance |
| **Usuários Inativos c/ Grupos** | 171 usuários, 7.427 registros | 0 | ✅ 7.427 registros economizados |
| **Grupos Órfãos** | 2 (IDs 140, 142) | 0 | ✅ Limpeza organizacional |

**Total economizado:** 7.500 registros limpos!

**Para usuários:** Nenhuma mudança visível. Apenas correção de bugs.

---

## 📚 REFERÊNCIAS E RECURSOS

### Links Úteis

**Documentação Oficial Odoo:**
- [Security Overview](https://www.odoo.com/documentation/15.0/developer/reference/backend/security.html)
- [Access Rights](https://www.odoo.com/documentation/15.0/developer/reference/backend/security.html#access-rights)
- [Record Rules](https://www.odoo.com/documentation/15.0/developer/reference/backend/security.html#record-rules)

**Documentação Interna RealCred:**
- `PLANO_REORGANIZACAO_PERMISSOES_ODOO15.md` - Plano completo de reorganização
- `RELATORIO_AUDITORIA_PERMISSOES_ODOO15.md` - Auditoria de segurança
- `ODOO15_SECURITY_GRUPOS_PERMISSOES_GUIA_COMPLETO_AI_FIRST.md` - Guia para desenvolvedores

### Contatos

**Suporte Técnico:**
- Email: ti@semprereal.com
- Telefone: (XX) XXXX-XXXX

**Suporte Funcional (Dúvidas de uso):**
- Email: suporte@semprereal.com

**Emergências (Sistema fora do ar):**
- Telefone: (XX) XXXX-XXXX (24/7)

---

## 🔍 GLOSSÁRIO

| Termo | Significado |
|-------|-------------|
| **Access Right** | Permissão de acesso a um modelo (tabela) inteiro |
| **Record Rule** | Filtro que restringe quais registros você vê |
| **CRUD** | Create (Criar), Read (Ler), Update (Atualizar), Delete (Deletar) |
| **Group / Grupo** | Conjunto de permissões que pode ser atribuído a usuários |
| **Implied Group** | Grupo que é automaticamente incluído quando você tem outro grupo |
| **Own Documents** | Apenas seus próprios registros (onde você é o responsável) |
| **All Documents** | Todos os registros do seu time/departamento |
| **Administrator** | Acesso total sem restrições |
| **Internal User** | Usuário interno da empresa (vs Portal/Public) |
| **Portal User** | Cliente/Parceiro com acesso limitado via portal |
| **Model** | Tabela do banco de dados (ex: crm.lead, sale.order) |
| **Domain** | Condição de filtro (ex: user_id = você) |

---

## ❓ AINDA TEM DÚVIDAS?

### Sua pergunta não está aqui?

1. **Verifique a documentação interna** (arquivos .md no repositório)
2. **Pergunte ao seu gestor direto**
3. **Abra chamado com TI:** ti@semprereal.com

### Sugestões para este FAQ?

Envie email para: ti@semprereal.com com assunto "Sugestão FAQ Permissões"

---

## 📝 HISTÓRICO DE ATUALIZAÇÕES

| Data | Versão | Mudanças |
|------|--------|----------|
| 17/11/2025 | 1.0 | Criação inicial do FAQ após Fase 1 de reorganização |

---

**Última Atualização:** 17/11/2025 00:55 UTC
**Responsável:** TI RealCred
**Status:** ✅ Ativo e Atualizado
