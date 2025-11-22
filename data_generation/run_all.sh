#!/bin/bash

###############################################################################
# Script de Inicio Rápido - Supply Chain Analytics Data Generation
#
# Este script ejecuta todos los pasos necesarios para generar datos y
# iniciar la API REST
#
# Uso: ./run_all.sh [opción]
#   ./run_all.sh setup     - Instalar dependencias
#   ./run_all.sh master    - Generar solo datos maestros
#   ./run_all.sh trans     - Generar solo datos transaccionales
#   ./run_all.sh all       - Generar todos los datos
#   ./run_all.sh api       - Iniciar API REST
#   ./run_all.sh full      - Hacer todo (setup + generar + API)
###############################################################################

set -e  # Exit on error

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

# Función para verificar Python
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        print_error "Python no está instalado. Por favor instala Python 3.8+"
        exit 1
    fi

    print_success "Python encontrado: $PYTHON_CMD"
}

# Función para crear entorno virtual
setup_environment() {
    print_header "CONFIGURACIÓN DEL ENTORNO"

    check_python

    # Crear entorno virtual si no existe
    if [ ! -d "venv" ]; then
        print_info "Creando entorno virtual..."
        $PYTHON_CMD -m venv venv
        print_success "Entorno virtual creado"
    else
        print_warning "Entorno virtual ya existe"
    fi

    # Activar entorno virtual
    print_info "Activando entorno virtual..."
    source venv/bin/activate

    # Instalar dependencias
    print_info "Instalando dependencias..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt > /dev/null 2>&1
    print_success "Dependencias instaladas"

    echo ""
}

# Función para generar datos maestros
generate_master_data() {
    print_header "GENERACIÓN DE DATOS MAESTROS"

    cd master_data
    $PYTHON_CMD generate_master_data.py
    cd ..

    print_success "Datos maestros generados exitosamente"
    echo ""
}

# Función para generar datos transaccionales
generate_transactional_data() {
    print_header "GENERACIÓN DE DATOS TRANSACCIONALES"

    print_warning "Esto puede tomar 5-10 minutos..."

    cd transactional
    $PYTHON_CMD generate_transactional_data.py
    cd ..

    print_success "Datos transaccionales generados exitosamente"
    echo ""
}

# Función para iniciar API
start_api() {
    print_header "INICIANDO API REST"

    print_info "La API estará disponible en:"
    print_info "  • Swagger UI: http://localhost:8000/docs"
    print_info "  • ReDoc:      http://localhost:8000/redoc"
    print_info ""
    print_warning "Presiona Ctrl+C para detener el servidor"
    echo ""

    cd transactional
    $PYTHON_CMD supply_chain_api.py
}

# Función para mostrar estadísticas
show_statistics() {
    print_header "ESTADÍSTICAS DE DATOS GENERADOS"

    if [ -d "output/master_data" ]; then
        echo -e "${GREEN}📊 Datos Maestros:${NC}"

        if [ -f "output/master_data/products/products_master.csv" ]; then
            PRODUCTS=$(wc -l < output/master_data/products/products_master.csv)
            echo "  • Productos:    $((PRODUCTS - 1)) registros"
        fi

        if [ -f "output/master_data/suppliers/suppliers_master.csv" ]; then
            SUPPLIERS=$(wc -l < output/master_data/suppliers/suppliers_master.csv)
            echo "  • Proveedores:  $((SUPPLIERS - 1)) registros"
        fi

        if [ -f "output/master_data/warehouses/warehouses_master.csv" ]; then
            WAREHOUSES=$(wc -l < output/master_data/warehouses/warehouses_master.csv)
            echo "  • Almacenes:    $((WAREHOUSES - 1)) registros"
        fi

        if [ -f "output/master_data/demographics/demand_demographics.csv" ]; then
            DEMOGRAPHICS=$(wc -l < output/master_data/demographics/demand_demographics.csv)
            echo "  • Regiones:     $((DEMOGRAPHICS - 1)) registros"
        fi

        echo ""
    fi

    if [ -d "output/transactional_data" ]; then
        echo -e "${GREEN}📡 Datos Transaccionales:${NC}"

        if [ -d "output/transactional_data/shipments" ]; then
            SHIPMENT_FILES=$(find output/transactional_data/shipments -name "*.json" | wc -l)
            echo "  • Archivos de shipments:      $SHIPMENT_FILES días"
        fi

        if [ -d "output/transactional_data/purchase_orders" ]; then
            PO_FILES=$(find output/transactional_data/purchase_orders -name "*.json" | wc -l)
            echo "  • Archivos de purchase orders: $PO_FILES días"
        fi

        if [ -d "output/transactional_data/inventory" ]; then
            INV_FILES=$(find output/transactional_data/inventory -name "*.json" | wc -l)
            echo "  • Archivos de inventory:       $INV_FILES días"
        fi

        echo ""

        # Tamaño total
        TOTAL_SIZE=$(du -sh output/transactional_data 2>/dev/null | cut -f1)
        echo "  • Tamaño total: $TOTAL_SIZE"
        echo ""
    fi
}

# Función para mostrar uso
show_usage() {
    echo "Uso: ./run_all.sh [opción]"
    echo ""
    echo "Opciones disponibles:"
    echo "  setup     - Crear entorno virtual e instalar dependencias"
    echo "  tsv    - Generar solo datos comprimidos en formato tsv.gz"
    echo "  trans     - Generar solo datos transaccionales"
    echo "  all       - Generar todos los datos (maestros + transaccionales)"
    echo "  api       - Iniciar API REST (requiere datos generados)"
    echo "  full      - Ejecutar todo (setup + generar + API)"
    echo "  stats     - Mostrar estadísticas de datos generados"
    echo "  clean     - Limpiar datos generados"
    echo ""
    echo "Ejemplos:"
    echo "  ./run_all.sh setup    # Primera vez"
    echo "  ./run_all.sh all      # Generar todos los datos"
    echo "  ./run_all.sh api      # Iniciar servidor API"
    echo ""
}

# Función para limpiar datos
clean_data() {
    print_header "LIMPIANDO DATOS GENERADOS"

    if [ -d "output" ]; then
        print_warning "¿Estás seguro de que deseas eliminar todos los datos generados? (y/n)"
        read -r response
        if [[ "$response" == "y" ]] || [[ "$response" == "Y" ]]; then
            rm -rf output
            print_success "Datos eliminados"
        else
            print_info "Operación cancelada"
        fi
    else
        print_warning "No hay datos para limpiar"
    fi

    echo ""
}

# Main script
main() {
    case "$1" in
        setup)
            setup_environment
            ;;
        tsv)
            check_python
            generate_master_data
            show_statistics
            ;;
        trans)
            check_python
            generate_transactional_data
            show_statistics
            ;;
        all)
            check_python
            generate_master_data
            generate_transactional_data
            show_statistics
            ;;
        api)
            check_python
            start_api
            ;;
        full)
            setup_environment
            generate_master_data
            generate_transactional_data
            show_statistics
            print_info "Para iniciar la API, ejecuta: ./run_all.sh api"
            ;;
        stats)
            show_statistics
            ;;
        clean)
            clean_data
            ;;
        *)
            show_usage
            exit 1
            ;;
    esac
}

# Ejecutar script
main "$@"
