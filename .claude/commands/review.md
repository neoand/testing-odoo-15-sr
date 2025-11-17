---
description: Fazer code review detalhado
---

# Code Review

Revisar código com olhar crítico e construtivo.

## Checklist de Review

### Funcionalidade
- [ ] Código faz o que deveria?
- [ ] Casos de borda tratados?
- [ ] Validações adequadas?

### Qualidade
- [ ] Legível e compreensível?
- [ ] Nomes descritivos?
- [ ] Comentários onde necessário?
- [ ] Sem código duplicado?

### Padrões Odoo
- [ ] Segue convenções Odoo?
- [ ] Models estruturados corretamente?
- [ ] Views seguem guidelines?
- [ ] Security configurado?

### Performance
- [ ] Queries otimizadas?
- [ ] Evita N+1?
- [ ] Usa cache adequadamente?

### Segurança
- [ ] Inputs sanitizados?
- [ ] Permissões corretas?
- [ ] Sem vulnerabilidades?

### Manutenibilidade
- [ ] Testável?
- [ ] Documentado?
- [ ] Fácil de estender?

## Output
- Lista de issues encontrados
- Sugestões de melhoria
- Código alternativo (quando relevante)
- Priorização (crítico, importante, nice-to-have)
