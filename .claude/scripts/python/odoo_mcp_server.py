#!/usr/bin/env python3
"""
MCP Server para Odoo PostgreSQL - Interface Claude ↔ Odoo Database

Permite que Claude consulte informações do Odoo de forma segura e estruturada.

Uso:
    python3.11 odoo_mcp_server.py

Métodos disponíveis:
- odoo.list_models: Lista todos os modelos do Odoo
- odoo.model_fields: Lista campos de um modelo específico
- odoo.query: Executa SELECT query segura
- odoo.get_record: Busca registro específico por ID
- odoo.list_modules: Lista módulos instalados
- odoo.module_info: Informações de um módulo
"""

import sys
import json
import psycopg2
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OdooMCPServer:
    def __init__(self):
        """Inicializa o server MCP para Odoo"""
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.load_config()

    def load_config(self):
        """Carrega configuração do banco de dados"""
        # Tentar ler do environment ou arquivo de config
        self.db_config = {
            'host': os.getenv('ODOO_DB_HOST', 'localhost'),
            'port': os.getenv('ODOO_DB_PORT', '5432'),
            'database': os.getenv('ODOO_DB_NAME', 'testing_odoo'),
            'user': os.getenv('ODOO_DB_USER', 'odoo'),
            'password': os.getenv('ODOO_DB_PASSWORD', 'HI5Rdi5UikL9jjLy')
        }

        # Tentar ler do arquivo de configuração do Odoo se existir
        odoo_conf_path = self.project_root / 'odoo-server.conf'
        if odoo_conf_path.exists():
            self.parse_odoo_config(odoo_conf_path)

    def parse_odoo_config(self, config_path: Path):
        """Parse arquivo de configuração do Odoo"""
        try:
            with open(config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('db_host'):
                        self.db_config['host'] = line.split('=')[1].strip()
                    elif line.startswith('db_port'):
                        self.db_config['port'] = line.split('=')[1].strip()
                    elif line.startswith('db_name'):
                        self.db_config['database'] = line.split('=')[1].strip()
                    elif line.startswith('db_user'):
                        self.db_config['user'] = line.split('=')[1].strip()
                    elif line.startswith('db_password'):
                        self.db_config['password'] = line.split('=')[1].strip()
        except Exception as e:
            logger.warning(f"Não foi possível ler config do Odoo: {e}")

    def get_connection(self) -> psycopg2.extensions.connection:
        """Estabelece conexão com o PostgreSQL"""
        try:
            conn = psycopg2.connect(**self.db_config)
            conn.autocommit = False
            return conn
        except Exception as e:
            logger.error(f"Erro de conexão PostgreSQL: {e}")
            raise

    def handle_list_models(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista modelos do Odoo com estado e descrição"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT
                m.model,
                m.name,
                m.state,
                COALESCE(COUNT(f.id), 0) as field_count,
                COALESCE(COUNT(r.id), 0) as record_count
            FROM ir_model m
            LEFT JOIN ir_model_fields f ON m.id = f.model_id
            LEFT JOIN (
                SELECT model_id, COUNT(*) as record_count
                FROM (
                    SELECT id, model_id::integer as model_id
                    FROM ir_model_data
                    WHERE model_id IS NOT NULL
                ) r
                GROUP BY model_id
            ) r ON m.id = r.model_id
            WHERE m.state = 'base'
            GROUP BY m.id, m.model, m.name, m.state
            ORDER BY m.model
            """

            cursor.execute(query)
            results = cursor.fetchall()

            models = []
            for row in results:
                models.append({
                    'model': row[0],
                    'name': row[1],
                    'state': row[2],
                    'field_count': row[3],
                    'estimated_records': row[4]
                })

            return {
                'success': True,
                'count': len(models),
                'models': models
            }

        except Exception as e:
            logger.error(f"Erro em list_models: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if 'conn' in locals():
                conn.close()

    def handle_model_fields(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista campos de um modelo específico"""
        model_name = params.get('model')
        if not model_name:
            return {'success': False, 'error': 'Parâmetro "model" é obrigatório'}

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Primeiro verificar se o modelo existe
            cursor.execute(
                "SELECT id FROM ir_model WHERE model = %s",
                (model_name,)
            )
            model_result = cursor.fetchone()

            if not model_result:
                return {'success': False, 'error': f'Modelo "{model_name}" não encontrado'}

            model_id = model_result[0]

            # Buscar campos do modelo
            query = """
            SELECT
                f.name,
                f.field_description,
                f.ttype,
                f.required,
                f.readonly,
                f.translate,
                f.store,
                f.index,
                COALESCE(f.relation, '') as relation,
                COALESCE(f.relation_field, '') as relation_field,
                f.selection
            FROM ir_model_fields f
            WHERE f.model_id = %s
            ORDER BY f.name
            """

            cursor.execute(query, (model_id,))
            results = cursor.fetchall()

            fields = []
            for row in results:
                field_info = {
                    'name': row[0],
                    'description': row[1] or '',
                    'type': row[2],
                    'required': row[3],
                    'readonly': row[4],
                    'translate': row[5],
                    'store': row[6],
                    'indexed': row[7],
                    'relation': row[8] or None,
                    'relation_field': row[9] or None
                }

                # Parse selection se existir
                if row[10]:  # selection
                    try:
                        field_info['selection'] = json.loads(row[10].replace("'", '"'))
                    except:
                        field_info['selection'] = row[10]

                fields.append(field_info)

            return {
                'success': True,
                'model': model_name,
                'field_count': len(fields),
                'fields': fields
            }

        except Exception as e:
            logger.error(f"Erro em model_fields: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if 'conn' in locals():
                conn.close()

    def handle_query(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Executa SELECT query segura no Odoo"""
        query = params.get('query', '').strip()
        limit = min(params.get('limit', 50), 1000)  # Máximo 1000 registros

        if not query:
            return {'success': False, 'error': 'Parâmetro "query" é obrigatório'}

        # Apenas permitir SELECT queries
        if not query.upper().startswith('SELECT'):
            return {'success': False, 'error': 'Apenas queries SELECT são permitidas'}

        # Verificar queries perigosas
        dangerous_keywords = ['DELETE', 'UPDATE', 'INSERT', 'DROP', 'ALTER', 'TRUNCATE']
        for keyword in dangerous_keywords:
            if keyword in query.upper():
                return {'success': False, 'error': f'Keyword "{keyword}" não permitido'}

        # Adicionar LIMIT se não tiver
        if 'LIMIT' not in query.upper():
            query += f" LIMIT {limit}"

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Execute query com timeout
            cursor.execute(query)

            # Obter nomes das colunas
            columns = [desc[0] for desc in cursor.description]

            # Obter rows
            rows = cursor.fetchall()

            # Converter para lista de dicionários
            result_rows = []
            for row in rows:
                result_rows.append(dict(zip(columns, row)))

            return {
                'success': True,
                'query': query,
                'columns': columns,
                'row_count': len(result_rows),
                'rows': result_rows
            }

        except Exception as e:
            logger.error(f"Erro em query: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if 'conn' in locals():
                conn.close()

    def handle_get_record(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Busca registro específico por ID e modelo"""
        model_name = params.get('model')
        record_id = params.get('id')

        if not model_name or not record_id:
            return {'success': False, 'error': 'Parâmetros "model" e "id" são obrigatórios'}

        # Converter para nome de tabela Odoo
        table_name = model_name.replace('.', '_')

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            # Buscar registro
            query = f'SELECT * FROM {table_name} WHERE id = %s LIMIT 1'
            cursor.execute(query, (record_id,))

            result = cursor.fetchone()
            if not result:
                return {'success': False, 'error': f'Registro {record_id} não encontrado em {model_name}'}

            # Obter nomes das colunas
            columns = [desc[0] for desc in cursor.description]

            # Converter para dicionário
            record = dict(zip(columns, result))

            return {
                'success': True,
                'model': model_name,
                'id': record_id,
                'record': record
            }

        except Exception as e:
            logger.error(f"Erro em get_record: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if 'conn' in locals():
                conn.close()

    def handle_list_modules(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Lista módulos instalados no Odoo"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT
                name,
                shortdesc,
                state,
                latest_version,
                author,
                website,
                license,
                summary
            FROM ir_module_module
            ORDER BY name
            """

            cursor.execute(query)
            results = cursor.fetchall()

            modules = []
            for row in results:
                modules.append({
                    'name': row[0],
                    'shortdesc': row[1] or '',
                    'state': row[2],
                    'version': row[3] or '',
                    'author': row[4] or '',
                    'website': row[5] or '',
                    'license': row[6] or '',
                    'summary': row[7] or ''
                })

            return {
                'success': True,
                'count': len(modules),
                'modules': modules
            }

        except Exception as e:
            logger.error(f"Erro em list_modules: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if 'conn' in locals():
                conn.close()

    def handle_module_info(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Informaçõess detalhadas de um módulo"""
        module_name = params.get('module')
        if not module_name:
            return {'success': False, 'error': 'Parâmetro "module" é obrigatório'}

        try:
            conn = self.get_connection()
            cursor = conn.cursor()

            query = """
            SELECT
                name,
                shortdesc,
                state,
                latest_version,
                author,
                website,
                license,
                summary,
                description,
                depends,
                data,
                demo,
                auto_install,
                application
            FROM ir_module_module
            WHERE name = %s
            """

            cursor.execute(query, (module_name,))
            result = cursor.fetchone()

            if not result:
                return {'success': False, 'error': f'Módulo "{module_name}" não encontrado'}

            # Parse depends se existir
            dependencies = []
            if result[10]:  # depends
                try:
                    dependencies = result[10].split(',')
                except:
                    pass

            return {
                'success': True,
                'module': {
                    'name': result[0],
                    'shortdesc': result[1] or '',
                    'state': result[2],
                    'version': result[3] or '',
                    'author': result[4] or '',
                    'website': result[5] or '',
                    'license': result[6] or '',
                    'summary': result[7] or '',
                    'description': result[8] or '',
                    'dependencies': dependencies,
                    'has_data': bool(result[11]),
                    'has_demo': bool(result[12]),
                    'auto_install': bool(result[13]),
                    'is_application': bool(result[14])
                }
            }

        except Exception as e:
            logger.error(f"Erro em module_info: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if 'conn' in locals():
                conn.close()

    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Processa requisição MCP"""
        method = request.get('method', '')
        params = request.get('params', {})

        logger.info(f"Processando método: {method}")

        # Route para método apropriado
        if method == 'odoo.list_models':
            return self.handle_list_models(params)
        elif method == 'odoo.model_fields':
            return self.handle_model_fields(params)
        elif method == 'odoo.query':
            return self.handle_query(params)
        elif method == 'odoo.get_record':
            return self.handle_get_record(params)
        elif method == 'odoo.list_modules':
            return self.handle_list_modules(params)
        elif method == 'odoo.module_info':
            return self.handle_module_info(params)
        else:
            return {
                'success': False,
                'error': f'Método desconhecido: {method}',
                'available_methods': [
                    'odoo.list_models',
                    'odoo.model_fields',
                    'odoo.query',
                    'odoo.get_record',
                    'odoo.list_modules',
                    'odoo.module_info'
                ]
            }

    def run(self):
        """Inicia o MCP server loop"""
        logger.info("Iniciando Odoo MCP Server...")
        logger.info(f"Conectado em: {self.db_config['host']}:{self.db_config['port']}/{self.db_config['database']}")

        try:
            for line in sys.stdin:
                if not line.strip():
                    continue

                try:
                    request = json.loads(line.strip())
                    response = self.handle_request(request)

                    # Adicionar timestamp se sucesso
                    if response.get('success', False):
                        response['timestamp'] = str(Path(__file__).stat().st_mtime)

                    print(json.dumps(response), flush=True)
                    sys.stdout.flush()

                except json.JSONDecodeError as e:
                    error_response = {
                        'success': False,
                        'error': f'JSON decode error: {str(e)}'
                    }
                    print(json.dumps(error_response), flush=True)
                    sys.stdout.flush()

        except KeyboardInterrupt:
            logger.info("Encerrando Odoo MCP Server...")
        except Exception as e:
            logger.error(f"Erro no MCP server: {e}")

if __name__ == "__main__":
    server = OdooMCPServer()
    server.run()