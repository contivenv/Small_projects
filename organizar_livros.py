import os
import re
from pathlib import Path

def adicionar_tags_massivamente(caminho_biblioteca):
    """
    Adiciona tags aos arquivos .md baseadas no nome da pasta que contém os EPUBs
    """
    
    biblioteca_path = Path(caminho_biblioteca)
    
    # Verifica se o caminho existe
    if not biblioteca_path.exists():
        print(f"Erro: Caminho não encontrado: {caminho_biblioteca}")
        return
    
    # Percorre todas as subpastas (gêneros)
    for genero_pasta in biblioteca_path.iterdir():
        if genero_pasta.is_dir():
            genero_nome = genero_pasta.name
            
            # Limpa o nome para criar uma tag válida
            tag_nome = limpar_nome_tag(genero_nome)
            
            print(f"Processando gênero: {genero_nome} -> Tag: #{tag_nome}")
            
            # Processa todos os arquivos .md na pasta do gênero
            for arquivo in genero_pasta.glob("*.md"):
                adicionar_tag_arquivo(arquivo, tag_nome, genero_nome)
    
    print("Processamento concluído!")

def limpar_nome_tag(nome):
    """
    Limpa o nome da pasta para criar uma tag válida no Obsidian
    """
    # Remove caracteres especiais e espaços, substitui por underscores
    tag_limpa = re.sub(r'[^\w\s-]', '', nome)
    tag_limpa = re.sub(r'[\s-]+', '_', tag_limpa)
    tag_limpa = tag_limpa.lower()
    
    return tag_limpa

def adicionar_tag_arquivo(arquivo_path, tag, genero_original):
    """
    Adiciona a tag ao arquivo .md se ela ainda não existir
    """
    try:
        # Lê o conteúdo atual do arquivo
        with open(arquivo_path, 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        # Verifica se a tag já exists
        if f"#{tag}" in conteudo or f"tags: {tag}" in conteudo:
            print(f"  Tag já existe em: {arquivo_path.name}")
            return
        
        # Verifica se já tem frontmatter
        if conteudo.startswith('---'):
            # Tem frontmatter, adiciona a tag na seção de tags
            conteudo_modificado = adicionar_tag_frontmatter(conteudo, tag)
        else:
            # Não tem frontmatter, cria um novo
            frontmatter = f"""---
tags: [{tag}]
genero: {genero_original}
---

"""
            conteudo_modificado = frontmatter + conteudo
        
        # Escreve o arquivo modificado
        with open(arquivo_path, 'w', encoding='utf-8') as f:
            f.write(conteudo_modificado)
        
        print(f"  ✓ Tag adicionada em: {arquivo_path.name}")
        
    except Exception as e:
        print(f"  ✗ Erro ao processar {arquivo_path.name}: {str(e)}")

def adicionar_tag_frontmatter(conteudo, nova_tag):
    """
    Adiciona tag ao frontmatter existente
    """
    linhas = conteudo.split('\n')
    
    # Encontra onde termina o frontmatter
    fim_frontmatter = -1
    for i, linha in enumerate(linhas[1:], 1):
        if linha.strip() == '---':
            fim_frontmatter = i
            break
    
    if fim_frontmatter == -1:
        # Frontmatter malformado, adiciona tag no final do frontmatter
        return conteudo.replace('---', f'tags: [{nova_tag}]\n---', 1)
    
    # Procura por linha de tags existente
    tags_linha_idx = -1
    for i in range(1, fim_frontmatter):
        if linhas[i].strip().startswith('tags:'):
            tags_linha_idx = i
            break
    
    if tags_linha_idx != -1:
        # Já tem linha de tags, adiciona a nova tag
        linha_tags = linhas[tags_linha_idx]
        if '[' in linha_tags and ']' in linha_tags:
            # Formato de lista
            linha_tags = linha_tags.replace(']', f', {nova_tag}]')
        else:
            # Formato simples, converte para lista
            tag_atual = linha_tags.split(':', 1)[1].strip()
            linha_tags = f"tags: [{tag_atual}, {nova_tag}]"
        
        linhas[tags_linha_idx] = linha_tags
    else:
        # Não tem linha de tags, adiciona uma nova
        linhas.insert(fim_frontmatter, f"tags: [{nova_tag}]")
    
    return '\n'.join(linhas)

def criar_notas_para_epubs(caminho_biblioteca):
    """
    Cria arquivos .md para cada .epub que não tenha nota correspondente
    """
    biblioteca_path = Path(caminho_biblioteca)
    
    for genero_pasta in biblioteca_path.iterdir():
        if genero_pasta.is_dir():
            genero_nome = genero_pasta.name
            tag_nome = limpar_nome_tag(genero_nome)
            
            # Procura por arquivos .epub
            for epub_file in genero_pasta.glob("*.epub"):
                md_file = epub_file.with_suffix('.md')
                
                if not md_file.exists():
                    # Cria nota básica para o EPUB
                    titulo_livro = epub_file.stem
                    
                    conteudo_nota = f"""---
tags: [{tag_nome}]
genero: {genero_nome}
tipo: livro
formato: epub
---

# {titulo_livro}

## Informações
- **Gênero**: {genero_nome}
- **Formato**: EPUB
- **Arquivo**: [[{epub_file.name}]]

## Notas de Leitura

## Citações Favoritas

## Avaliação
- [ ] Lido
- Nota: /10
"""
                    
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(conteudo_nota)
                    
                    print(f"  ✓ Nota criada para: {titulo_livro}")

if __name__ == "__main__":
    # Caminho para sua pasta Biblioteca no Fedora  
    caminho_biblioteca = "/home/guilherme/Documentos/Anotações/Anotações/Livros/Biblioteca"
    
    print("=== SCRIPT DE ORGANIZAÇÃO DE LIVROS NO OBSIDIAN ===\n")
    
    # Opção 1: Criar notas .md para EPUBs que não têm
    resposta = input("Deseja criar notas .md para EPUBs sem notas? (s/n): ")
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        print("\n--- Criando notas para EPUBs ---")
        criar_notas_para_epubs(caminho_biblioteca)
    
    # Opção 2: Adicionar tags baseadas nas pastas
    resposta = input("\nDeseja adicionar tags baseadas nos nomes das pastas? (s/n): ")
    if resposta.lower() in ['s', 'sim', 'y', 'yes']:
        print("\n--- Adicionando tags ---")
        adicionar_tags_massivamente(caminho_biblioteca)
    
    print("\n=== PROCESSAMENTO CONCLUÍDO ===")