#!/bin/bash

# Script para restaurar backup do WhatsApp no Android
# Uso: ./restore_whatsapp.sh /caminho/para/backup/fedora

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

# Verificar se o caminho do backup foi fornecido
if [ $# -eq 0 ]; then
    print_error "Uso: $0 /caminho/para/backup/fedora"
    exit 1
fi

BACKUP_PATH="$1"

# Verificar se o diretório de backup existe
if [ ! -d "$BACKUP_PATH" ]; then
    print_error "Diretório de backup não encontrado: $BACKUP_PATH"
    exit 1
fi

print_status "Iniciando processo de restauração do WhatsApp..."

# Verificar se ADB está instalado
if ! command -v adb &> /dev/null; then
    print_error "ADB não encontrado. Instale com: sudo dnf install android-tools"
    exit 1
fi

# Verificar conexão com o dispositivo
print_status "Verificando conexão com dispositivo Android..."
if ! adb devices | grep -q "device$"; then
    print_error "Nenhum dispositivo Android conectado ou depuração USB não habilitada"
    print_warning "Certifique-se de:"
    echo "  1. Conectar o dispositivo via USB"
    echo "  2. Habilitar modo desenvolvedor"
    echo "  3. Ativar depuração USB"
    echo "  4. Autorizar o computador no dispositivo"
    exit 1
fi

print_status "Dispositivo Android conectado!"

# Criar estrutura de diretórios no Android (WhatsApp Media)
print_status "Criando estrutura de diretórios no Android..."
adb shell "mkdir -p /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Databases/"
adb shell "mkdir -p /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Backups/"
adb shell "mkdir -p /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Media/"

# Função para transferir arquivos por categoria
transfer_databases() {
    print_status "Transferindo arquivos de banco de dados..."
    
    # Verificar se a pasta Databases existe
    if [ -d "$BACKUP_PATH/Databases" ]; then
        # Transferir todos os arquivos da pasta Databases
        for file in "$BACKUP_PATH/Databases"/*; do
            if [ -f "$file" ]; then
                filename=$(basename "$file")
                print_status "  → $filename"
                adb push "$file" "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Databases/"
            fi
        done
        
        # Identificar e renomear o backup mais recente para msgstore.db.crypt14
        # Procurar pelo arquivo msgstore mais recente (com data)
        latest_backup=$(ls -t "$BACKUP_PATH/Databases"/msgstore-*.db.crypt14 2>/dev/null | head -1)
        if [ -n "$latest_backup" ]; then
            backup_name=$(basename "$latest_backup")
            print_status "Definindo $backup_name como backup principal..."
            adb shell "cd /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Databases/ && cp '$backup_name' msgstore.db.crypt14" 2>/dev/null
        elif [ -f "$BACKUP_PATH/Databases/wa.db.crypt14" ]; then
            print_status "Renomeando wa.db.crypt14 para msgstore.db.crypt14..."
            adb shell "cd /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Databases/ && mv wa.db.crypt14 msgstore.db.crypt14" 2>/dev/null
        fi
    else
        print_warning "Pasta Databases não encontrada em $BACKUP_PATH"
    fi
}

transfer_backups() {
    print_status "Transferindo arquivos de configuração..."
    
    # Verificar se a pasta Backups existe
    if [ -d "$BACKUP_PATH/Backups" ]; then
        # Transferir todos os arquivos da pasta Backups
        for file in "$BACKUP_PATH/Backups"/*; do
            if [ -f "$file" ]; then
                filename=$(basename "$file")
                print_status "  → $filename"
                adb push "$file" "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Backups/"
            fi
        done
    else
        print_warning "Pasta Backups não encontrada em $BACKUP_PATH"
    fi
}

transfer_media() {
    print_status "Transferindo mídia..."
    
    # Verificar se a pasta Media existe
    if [ -d "$BACKUP_PATH/Media" ]; then
        # Transferir todo o conteúdo da pasta Media
        print_status "  → Conteúdo da pasta Media"
        adb push "$BACKUP_PATH/Media/." "/storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Media/"
    else
        print_warning "Pasta Media não encontrada em $BACKUP_PATH"
    fi
}

# Executar transferências
transfer_databases
transfer_backups
transfer_media

print_status "Verificando arquivos transferidos..."
adb shell "ls -la /storage/emulated/0/Android/media/com.whatsapp/WhatsApp/Databases/"

print_status "✅ Backup restaurado com sucesso!"
print_warning "Próximos passos:"
echo "  1. Desinstale o WhatsApp do dispositivo Android"
echo "  2. Reinstale o WhatsApp da Play Store"
echo "  3. Configure com o mesmo número de telefone"
echo "  4. O WhatsApp detectará automaticamente o backup local"

print_warning "💡 Dica: Mantenha o dispositivo conectado até completar a instalação"
