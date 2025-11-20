# Prompt: Code Review Odoo

Use este prompt para fazer code review sistemático de código Odoo.

## Instruções

Analise o código fornecido seguindo os critérios abaixo:

### 1. Funcionalidade
- O código faz o que deveria fazer?
- Casos de borda estão tratados?
- Validações estão presentes?
- Tratamento de erros adequado?

### 2. Padrões Odoo
- Segue convenções de nomenclatura?
- Usa APIs corretas?
- Herança implementada corretamente?
- Métodos override seguem padrão?

### 3. Segurança
- Inputs são validados/sanitizados?
- SQL injection prevenido?
- Permissões verificadas?
- Dados sensíveis protegidos?

### 4. Performance
- Queries otimizadas?
- Evita N+1 queries?
- Usa search_count quando apropriado?
- Cache utilizado adequadamente?

### 5. Manutenibilidade
- Código legível?
- Nomes descritivos?
- Comentários onde necessário?
- Sem código morto?
- DRY (Don't Repeat Yourself)?

### 6. Testes
- Testável?
- Testes existem?
- Coverage adequado?

## Output Esperado

Retorne:
1. **Resumo Geral** (1-2 parágrafos)
2. **Issues Críticos** (lista priorizada)
3. **Sugestões de Melhoria** (lista)
4. **Código Alternativo** (se aplicável)
5. **Score** (1-10)

## Exemplo

```python
# CÓDIGO A REVISAR
class CrmLead(models.Model):
    _inherit = 'crm.lead'

    custom_field = fields.Char('Custom')
```

**Review:**
- ✅ Herança correta
- ⚠️ Falta _description no campo
- ⚠️ Sem validação
- ⚠️ Sem tracking
- ❌ Campo muito genérico

**Sugestão:**
```python
custom_field = fields.Char(
    string='Campo Personalizado',
    help='Descrição do campo',
    tracking=True,
    required=False
)
```
