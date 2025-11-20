# Odoo 502 Debug Workers Pattern - Aprendizado Cursor

**Data:** 2025-11-19
**Fonte:** Cursor IDE solução para erro 502
**Contexto:** Erro 502 Bad Gateway no Odoo que Claude não conseguiu resolver

## O QUE APRENDI

### Problema Identificado
- **Sintoma:** Odoo retornando 502 Bad Gateway
- **Causa Raiz:** Odoo rodando com `--workers=0` (modo debug)
- **Impacto:** Lentidão extrema e timeouts no Nginx

### Solução Aplicada pelo Cursor
1. Reiniciar Odoo com configuração de produção (9 workers)
2. Reiniciar Nginx para reconhecer o Odoo
3. Verificar conectividade HTTP 200 OK

### PATTERN CRÍTICO APRENDIDO

#### Erro Cometido por Claude:
```bash
# ❌ ERRADO - Modo debug em produção
sudo -u odoo python3 ./odoo-bin -c /etc/odoo-server.conf -d testing --workers=0
```

#### Solução Correta (Cursor):
```bash
# ✅ CORRETO - Configuração de produção
# Usar serviço systemd que já tem workers configurados
sudo systemctl restart odoo-server
# Ou manualmente com workers
sudo -u odoo python3 ./odoo-bin -c /etc/odoo-server.conf -d testing --workers=9
```

## DIAGNÓSTICO FUTURO

### Quando Suspeitar de Modo Debug:
1. Serviço ativo mas sem processos suficientes
2. `ps aux | grep odoo-bin` mostra apenas 1-2 processos
3. Erros 502 intermitentes
4. Respostas muito lentas

### Comando de Diagnóstico:
```bash
# Verificar número de workers
ps aux | grep '[o]doo-bin' | wc -l

# Deveria ser:
# - 1 processo: Modo debug (--workers=0)
# - 10+ processos: Modo produção (--workers=9 + gevent)

# Verificar se Nginx está conectando
curl -I http://localhost:8069
sudo systemctl status nginx
```

## COMANDOS QUE FUNCIONAM (Salvar em COMMAND-HISTORY.md)

### Reiniciar Odoo Corretamente:
```bash
# Método 1: Systemd (preferencial)
sudo systemctl restart odoo-server

# Método 2: Manual com workers
cd /odoo/odoo-server
sudo pkill -9 -f 'odoo-bin'
sudo -u odoo python3 ./odoo-bin -c /etc/odoo-server.conf -d testing --workers=9 &

# Método 3: Verificação completa
sudo systemctl restart odoo-server && sleep 10 && sudo systemctl restart nginx
```

### Diagnóstico Completo:
```bash
echo "=== Processos Odoo ==="
ps aux | grep '[o]doo-bin' | wc -l

echo "=== Porta 8069 ==="
sudo ss -tlnp | grep 8069

echo "=== Teste Local ==="
curl -I http://localhost:8069

echo "=== Status Nginx ==="
sudo systemctl status nginx --no-pager | head -5
```

## LIÇÕES CRÍTICAS

1. **Systemd vs Manual**: Sistema systemd já configura workers corretamente
2. **Debug vs Produção**: `--workers=0` é ONLY para debug, NUNCA para produção
3. **Nginx Integration**: Nginx precisa reiniciar se Odoo reinicia
4. **Process Count**: 1 processo = debug, 10+ = produção

## PREVENÇÃO FUTURA

### Sempre verificar:
- [ ]Número de processos odoo-bin (> 5 para produção)
- [ ]Nginx rodando e conectando
- [ ]Resposta HTTP 200 OK
- [ ]Logs sem errors críticos

### Nunca usar:
- `--workers=0` em produção
- Restart manual sem verificar Nginx
- Debug prolongado em servidor ativo

## IMPACTO

Este erro causou:
- X minutos de downtime
- Instalação de módulos atrasada
- Frustração do usuário

A solução correta restaura:
- Performance normal
- Disponibilidade do sistema
- Capacidade de instalar módulos

**TAGS:** #odoo #502 #nginx #workers #debug #produção #crítico