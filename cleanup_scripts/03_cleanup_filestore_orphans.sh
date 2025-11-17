#!/bin/bash
# =====================================================
# LIMPEZA DE ARQUIVOS ÓRFÃOS NO FILESTORE
# =====================================================
# EXECUTAR SOMENTE APÓS:
# 1. Limpeza do database concluída (script 02)
# 2. Aguardar 7 dias sem problemas
# 3. Backup do filestore realizado
# =====================================================

set -e  # Para em caso de erro

echo "========================================="
echo "LIMPEZA DE ARQUIVOS ÓRFÃOS - FILESTORE"
echo "Data: $(date)"
echo "========================================="

# Configurações
FILESTORE_PATH="/odoo/filestore/filestore/realcred"
BACKUP_PATH="/tmp/orphan_files_backup_$(date +%Y%m%d)"
VALID_FILES_LIST="/tmp/valid_files.txt"
ORPHAN_FILES_LIST="/tmp/orphan_files.txt"

# Verificar se filestore existe
if [ ! -d "$FILESTORE_PATH" ]; then
    echo "❌ ERRO: Filestore não encontrado em $FILESTORE_PATH"
    exit 1
fi

echo "✅ Filestore encontrado: $FILESTORE_PATH"

# Passo 1: Obter lista de arquivos válidos do database
echo ""
echo "Passo 1: Obtendo lista de arquivos válidos do database..."
sudo -u postgres psql realcred -t -A -c "
SELECT DISTINCT store_fname
FROM ir_attachment
WHERE store_fname IS NOT NULL
  AND store_fname != ''
" > "$VALID_FILES_LIST"

VALID_COUNT=$(wc -l < "$VALID_FILES_LIST")
echo "✅ Arquivos válidos no database: $VALID_COUNT"

# Passo 2: Encontrar arquivos no filestore
echo ""
echo "Passo 2: Escaneando filestore (pode demorar)..."
cd "$FILESTORE_PATH"

TOTAL_FILES=$(find . -type f | wc -l)
echo "✅ Total de arquivos no filestore: $TOTAL_FILES"

# Passo 3: Identificar órfãos
echo ""
echo "Passo 3: Identificando arquivos órfãos..."
> "$ORPHAN_FILES_LIST"  # Limpar arquivo

find . -type f | while read filepath; do
    filename=$(basename "$filepath")

    # Verificar se arquivo está no database
    if ! grep -Fxq "$filename" "$VALID_FILES_LIST"; then
        echo "$filepath" >> "$ORPHAN_FILES_LIST"
    fi
done

ORPHAN_COUNT=$(wc -l < "$ORPHAN_FILES_LIST")
echo "✅ Arquivos órfãos encontrados: $ORPHAN_COUNT"

if [ "$ORPHAN_COUNT" -eq 0 ]; then
    echo "✅ Nenhum arquivo órfão encontrado! Filestore limpo."
    exit 0
fi

# Passo 4: Calcular espaço a recuperar
echo ""
echo "Passo 4: Calculando espaço a recuperar..."
ORPHAN_SIZE=$(cat "$ORPHAN_FILES_LIST" | xargs du -ch 2>/dev/null | tail -1 | cut -f1)
echo "📊 Espaço a recuperar: $ORPHAN_SIZE"

# Passo 5: Mostrar exemplos
echo ""
echo "Exemplos de arquivos órfãos (primeiros 10):"
head -10 "$ORPHAN_FILES_LIST"

# Passo 6: Confirmar antes de mover
echo ""
echo "========================================="
echo "RESUMO:"
echo "  Total de arquivos: $TOTAL_FILES"
echo "  Arquivos válidos: $VALID_COUNT"
echo "  Arquivos órfãos: $ORPHAN_COUNT"
echo "  Espaço a recuperar: $ORPHAN_SIZE"
echo "========================================="
echo ""
echo "⚠️  ATENÇÃO: Os arquivos serão MOVIDOS (não deletados)"
echo "   para: $BACKUP_PATH"
echo ""
echo "✅ Auto-confirmando limpeza (modo não-interativo)..."
confirm="SIM"

# Passo 7: Criar diretório de backup
echo ""
echo "Criando diretório de backup..."
mkdir -p "$BACKUP_PATH"
echo "✅ Backup path: $BACKUP_PATH"

# Passo 8: Mover arquivos órfãos (NÃO deletar!)
echo ""
echo "Movendo arquivos órfãos para backup..."
moved_count=0
error_count=0

cat "$ORPHAN_FILES_LIST" | while read filepath; do
    # Preservar estrutura de diretórios
    dirname=$(dirname "$filepath")
    mkdir -p "$BACKUP_PATH/$dirname"

    if mv "$filepath" "$BACKUP_PATH/$filepath" 2>/dev/null; then
        moved_count=$((moved_count + 1))

        # Mostrar progresso a cada 1000 arquivos
        if [ $((moved_count % 1000)) -eq 0 ]; then
            echo "  Movidos: $moved_count arquivos..."
        fi
    else
        error_count=$((error_count + 1))
    fi
done

echo "✅ Movidos: $moved_count arquivos"
if [ "$error_count" -gt 0 ]; then
    echo "⚠️  Erros: $error_count arquivos"
fi

# Passo 9: Verificar resultado
echo ""
echo "Verificando filestore após limpeza..."
NEW_TOTAL=$(find "$FILESTORE_PATH" -type f | wc -l)
echo "✅ Arquivos restantes no filestore: $NEW_TOTAL"

# Passo 10: Calcular espaço recuperado
echo ""
FILESTORE_SIZE_BEFORE=$(du -sh "$FILESTORE_PATH" 2>/dev/null | cut -f1)
echo "📊 Tamanho do filestore após limpeza: $FILESTORE_SIZE_BEFORE"

echo ""
echo "========================================="
echo "✅ LIMPEZA CONCLUÍDA COM SUCESSO!"
echo "========================================="
echo ""
echo "PRÓXIMOS PASSOS:"
echo "1. Verificar Odoo funciona normalmente"
echo "2. Aguardar 30 dias sem problemas"
echo "3. Após 30 dias, deletar backup:"
echo "   rm -rf $BACKUP_PATH"
echo ""
echo "Para RESTAURAR arquivos (se necessário):"
echo "   cp -r $BACKUP_PATH/* $FILESTORE_PATH/"
echo "   sudo chown -R odoo:odoo $FILESTORE_PATH"
echo ""
echo "========================================="

# Criar arquivo de log
cat > "${BACKUP_PATH}/cleanup_log.txt" << EOF
LIMPEZA DE FILESTORE - $(date)
========================================
Filestore path: $FILESTORE_PATH
Arquivos totais antes: $TOTAL_FILES
Arquivos válidos (DB): $VALID_COUNT
Arquivos órfãos: $ORPHAN_COUNT
Arquivos restantes: $NEW_TOTAL
Espaço recuperado: $ORPHAN_SIZE
Backup location: $BACKUP_PATH

Lista completa em: $ORPHAN_FILES_LIST

IMPORTANTE: Aguardar 30 dias antes de deletar backup!
EOF

echo "Log salvo em: ${BACKUP_PATH}/cleanup_log.txt"
