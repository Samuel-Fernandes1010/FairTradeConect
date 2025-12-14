import sqlite3
import os

DB_NAME = "db_proj"

def criar_banco():
    
    # Conexão DB:
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 1. Habilitar Chaves Estrangeiras
    cursor.execute("PRAGMA foreign_key = ON;")
    
    # Criar tabela Produtor
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produtor (
        id_produtor INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(100) NOT NULL,
        cpf_cnpj VARCHAR(20) UNIQUE NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        senha VARCHAR(255) NOT NULL,
        telefone VARCHAR(30)
    );
    """)
    
    # Criar tabela Empresa
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS empresa (
        id_empresa INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(100) NOT NULL,
        cnpj VARCHAR(20) UNIQUE NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        senha VARCHAR(255) NOT NULL,
        telefone VARCHAR(30)
    );
    """)
    
    # Criar tabela Produto
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS produto (
        id_produto INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(100) NOT NULL,
        descricao TEXT,
        categoria VARCHAR(100),
        data_producao DATE,
        status_logistica VARCHAR(30),
        produtor_id INTEGER,
        FOREIGN KEY (produtor_id) REFERENCES produtor(id_produtor)
    );
    """)
    
    # Criar tabela Documento
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS documento (
        id_documento INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo VARCHAR(50) NOT NULL,
        arquivo TEXT,
        status VARCHAR(20),
        produtor_id INTEGER,
        FOREIGN KEY (produtor_id) REFERENCES produtor(id_produtor)
    );
    """)
    
    # Criar tabela Administrador
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS administrador (
        id_adm INTEGER PRIMARY KEY AUTOINCREMENT,
        nome VARCHAR(100) NOT NULL,
        email VARCHAR(150) UNIQUE NOT NULL,
        senha VARCHAR(255) NOT NULL
    );
    """)
    
    # Criar tabela Certificacao
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS certificacao (
        id_certificacao INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        administrador_id INTEGER,
        data_certificacao DATE,
        validade DATE,
        status VARCHAR(20),
        FOREIGN KEY (produto_id) REFERENCES produto(id_produto),
        FOREIGN KEY (administrador_id) REFERENCES administrador(id_adm)
    );
    """)
    
    # Criar tabela AnuncioMarketplace
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS anuncio_marketplace (
        id_anuncio INTEGER PRIMARY KEY AUTOINCREMENT,
        produto_id INTEGER,
        plataforma VARCHAR(100),
        url VARCHAR(255),
        data_publicacao DATE,
        status VARCHAR(20),
        FOREIGN KEY (produto_id) REFERENCES produto(id_produto)
    );
    """)
    
    # Commit e fechar conexão
    conn.commit()
    conn.close()
    print("Banco de dados criado com sucesso!")

if __name__ == "__main__":
    criar_banco()
    
    
