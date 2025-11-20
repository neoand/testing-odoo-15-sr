---
description: Debugar problemas e erros no código de forma sistemática
---

# Debug de Problemas

Investigar e resolver bugs, erros e comportamentos inesperados usando metodologia estruturada.

## Processo de Debug Sistemático

### 1. Coleta de Informações
- **Descrição do problema:** O que está acontecendo?
- **Logs de erro:** Mensagens, stack traces, códigos
- **Contexto:** Quando acontece? Quem afeta?
- **Reprodução:** Como reproduzir o problema?

### 2. Investigação Técnica
- **Reproduzir o problema:** Confirmar o bug
- **Analisar código relacionado:** Áreas afetadas
- **Verificar dependências:** Pacotes, versões, compatibilidade
- **Checar dados no banco:** Consistência dos dados

### 3. Diagnóstico
- **Identificar causa raiz:** Problema fundamental
- **Avaliar impacto:** O quão crítico é?
- **Propor soluções:** Múltiplas abordagens
- **Considerar trade-offs:** Tempo vs. qualidade

### 4. Resolução
- **Implementar correção:** Fix mínimo e seguro
- **Testar solução:** Verificar que resolve
- **Testar regressão:** Garantir que não quebra outros
- **Documentar fix:** Para referência futura

## Ferramentas de Debug

### Logs e Monitoramento
```bash
# Ver logs em tempo real
tail -f /var/log/odoo/odoo-server.log

# Logs de sistema
journalctl -u odoo -f

# Logs de aplicação específicos
grep -r "ERROR" /path/to/logs/
```

### Análise de Código
```bash
# Procurar padrões de erro
grep -r "exception\|error" /path/to/code/

# Ver commits recentes
git log --oneline -10

# Comparar versões
git diff HEAD~1 HEAD
```

### Banco de Dados
```sql
-- Verificar integridade dos dados
SELECT COUNT(*) FROM tabela WHERE condicao;

-- Procurar registros problemáticos
SELECT * FROM tabela WHERE campo IS NULL;

-- Verificar performance
EXPLAIN ANALYZE SELECT * FROM tabela;
```

### Python Debug
```python
# Usar pdb para debug
import pdb; pdb.set_trace()

# Logging estruturado
import logging
logger = logging.getLogger(__name__)
logger.info("Debug info: %s", variable)

# Try/except com logging detalhado
try:
    risky_operation()
except Exception as e:
    logger.exception("Error in risky_operation: %s", e)
```

## Checklist de Debug

### Antes de Começar
- [ ] Problema está claramente definido?
- [ ] É possível reproduzir consistentemente?
- [ ] Ambiente de teste isolado disponível?
- [ ] Backup feito antes de alterações?

### Durante Investigação
- [ ] Coletou logs e mensagens de erro?
- [ ] Identificou quando o problema começou?
- [ ] Verificou mudanças recentes no código?
- [ ] Testou em ambiente diferente?

### Ao Implementar Solução
- [ ] Solução é mínima e segura?
- [ ] Testou cenários de sucesso e falha?
- [ ] Verificou não introduzir novos bugs?
- [ ] Documentou a causa e solução?

## Padrões Comuns de Erros

### 1. Erros de Configuração
- **Sintomas:** Serviço não inicia, acesso negado
- **Causa:** Arquivos .conf, permissões, ambiente
- **Solução:** Verificar configuração, testar alterações

### 2. Erros de Rede
- **Sintomas:** Timeout, connection refused
- **Causa:** Firewall, portas, DNS, conectividade
- **Solução:** Testar conectividade, verificar regras

### 3. Erros de Dados
- **Sintomas:** Dados corrompidos, inconsistentes
- **Causa:** Migrações falhas, validação fraca
- **Solução:** Backup, restauração, validação

### 4. Erros de Performance
- **Sintomas:** Lentidão, timeouts
- **Causa:** Queries lentas, falta de índices
- **Solução:** Profile, otimizar queries, adicionar índices

## Comandos Úteis

### Análise Rápida
```bash
# Status geral dos serviços
systemctl status nginx postgresql odoo

# Recursos do sistema
top -p $(pgrep odoo)
df -h
free -m

# Portas em uso
netstat -tlnp | grep -E ':(80|443|5432|8069)'
```

### Debug Avançado
```bash
# Processos ativos
ps aux | grep -E '(odoo|postgres|nginx)'

# Conexões de banco
sudo -u postgres psql -c "SELECT * FROM pg_stat_activity;"

# Logs detalhados
tail -f /var/log/nginx/error.log &
tail -f /var/log/postgresql/postgresql-12-main.log &
tail -f /var/log/odoo/odoo-server.log &
```

## Padrão de Documentação de Fixes

Para cada bug resolvido, documentar:
```markdown
### [YYYY-MM-DD] Título do Bug

**Contexto:** Onde/quando aconteceu
**Sintoma:** Comportamento observado
**Causa Raiz:** Por que aconteceu
**Solução:** Como foi corrigido
**Comandos:** Específicos para debug/fix
**Prevenção:** Como evitar no futuro
**Tags:** #debug #categoria
```

## Melhores Práticas

1. **Não assumir:** Sempre investigar antes de concluir
2. **Testar isoladamente:** Isolar o problema do sistema
3. **Usar método científico:** Hipótese → Teste → Conclusão
4. **Documentar tudo:** Para referência e aprendizado
5. **Comunicação clara:** Explicar o problema e solução

## Ferramentas Específicas

### Para Web Applications
- Browser DevTools (Console, Network, Elements)
- curl/wget para testar endpoints
- Postman/Insomnia para APIs

### Para Backend Services
- strace/ltrace para system calls
- perf para profiling de performance
- gdb para debug binário

### Para Database Issues
- EXPLAIN ANALYZE para queries
- pg_stat_statements para estatísticas
- pgAdmin para interface gráfica
