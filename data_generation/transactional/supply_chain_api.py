"""
Supply Chain Transactional Data API
Equivalente al endpoint ECDC del proyecto COVID-19

Esta API REST simula un servicio que proporciona datos transaccionales
de supply chain, para ser consumidos por Azure Data Factory mediante HTTP Connector.

Endpoints:
- GET /api/v1/shipments?date={YYYY-MM-DD}
- GET /api/v1/purchase-orders?date={YYYY-MM-DD}
- GET /api/v1/inventory?date={YYYY-MM-DD}
- GET /api/v1/health (health check)

Autor: Supply Chain Analytics Project
Fecha: 2024-11-20
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from datetime import datetime, timedelta
from pathlib import Path
import json
from typing import Optional
import uvicorn

# Configuración
DATA_DIR = Path("../output/transactional_data")

# Crear aplicación FastAPI
app = FastAPI(
    title="Supply Chain Transactional Data API",
    description="API REST para datos transaccionales de Supply Chain Analytics (Equivalente a ECDC COVID-19)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)


def load_daily_data(dataset: str, date_str: str):
    """
    Carga datos de un día específico desde archivos JSON

    Args:
        dataset: Nombre del dataset ('shipments', 'purchase_orders', 'inventory')
        date_str: Fecha en formato YYYY-MM-DD

    Returns:
        Diccionario con los datos o None si no existe

    Raises:
        HTTPException si hay error
    """
    try:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de fecha inválido. Use YYYY-MM-DD"
        )

    # Construir ruta al archivo
    year = date_obj.strftime('%Y')
    month = date_obj.strftime('%m')
    day = date_obj.strftime('%d')

    # Nombres de archivo según dataset
    file_mapping = {
        'shipments': f'shipments_{date_str}.json',
        'purchase_orders': f'po_{date_str}.json',
        'inventory': f'inventory_{date_str}.json'
    }

    file_path = DATA_DIR / dataset / year / month / day / file_mapping[dataset]

    # Verificar si el archivo existe
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"No hay datos disponibles para {dataset} en la fecha {date_str}"
        )

    # Cargar datos
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al cargar datos: {str(e)}"
        )


@app.get("/")
async def root():
    """
    Endpoint raíz - Información de la API
    """
    return {
        "message": "Supply Chain Transactional Data API",
        "version": "1.0.0",
        "description": "API REST equivalente a ECDC para Azure Data Factory",
        "endpoints": [
            "/api/v1/shipments",
            "/api/v1/purchase-orders",
            "/api/v1/inventory",
            "/api/v1/health"
        ],
        "documentation": "/docs"
    }


@app.get("/api/v1/health")
async def health_check():
    """
    Health check endpoint
    """
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "Supply Chain Transactional Data API"
    }


@app.get("/api/v1/shipments")
async def get_shipments(
    date: Optional[str] = Query(
        None,
        description="Fecha de los envíos (YYYY-MM-DD). Si no se proporciona, usa la fecha de ayer",
        example="2024-01-15"
    )
):
    """
    Obtiene datos de envíos para una fecha específica

    Args:
        date: Fecha en formato YYYY-MM-DD (opcional, por defecto ayer)

    Returns:
        JSON con datos de envíos del día

    Example Response:
    ```json
    {
        "date": "2024-01-15",
        "total_records": 150,
        "data": [
            {
                "shipment_id": "SHP-2024-001234",
                "order_id": "ORD-2024-005678",
                "origin_warehouse": "WH-001",
                "destination_location": "New York, NY, USA",
                "product_id": "PRD-ELEC-001",
                "quantity": 500,
                "shipment_date": "2024-01-15",
                "scheduled_delivery_date": "2024-01-18",
                "actual_delivery_date": "2024-01-19",
                "carrier": "DHL Express",
                "transportation_mode": "air",
                "shipping_cost": 1250.00,
                "status": "delivered",
                "delay_days": 1
            }
        ]
    }
    ```
    """
    # Si no se proporciona fecha, usar ayer
    if date is None:
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    data = load_daily_data('shipments', date)

    return JSONResponse(
        content=data,
        headers={
            "X-Total-Records": str(data['total_records']),
            "X-Date": date
        }
    )


@app.get("/api/v1/purchase-orders")
async def get_purchase_orders(
    date: Optional[str] = Query(
        None,
        description="Fecha de las órdenes de compra (YYYY-MM-DD). Si no se proporciona, usa la fecha de ayer",
        example="2024-01-15"
    )
):
    """
    Obtiene datos de órdenes de compra para una fecha específica

    Args:
        date: Fecha en formato YYYY-MM-DD (opcional, por defecto ayer)

    Returns:
        JSON con datos de órdenes de compra del día

    Example Response:
    ```json
    {
        "date": "2024-01-15",
        "total_records": 75,
        "data": [
            {
                "po_id": "PO-2024-001234",
                "supplier_id": "SUP-CN-001",
                "product_id": "PRD-ELEC-001",
                "order_date": "2024-01-10",
                "quantity_ordered": 10000,
                "unit_price": 15.50,
                "total_cost": 155000.00,
                "expected_delivery_date": "2024-02-10",
                "actual_delivery_date": "2024-02-12",
                "order_status": "completed",
                "delay_days": 2
            }
        ]
    }
    ```
    """
    # Si no se proporciona fecha, usar ayer
    if date is None:
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    data = load_daily_data('purchase_orders', date)

    return JSONResponse(
        content=data,
        headers={
            "X-Total-Records": str(data['total_records']),
            "X-Date": date
        }
    )


@app.get("/api/v1/inventory")
async def get_inventory(
    date: Optional[str] = Query(
        None,
        description="Fecha del snapshot de inventario (YYYY-MM-DD). Si no se proporciona, usa la fecha de ayer",
        example="2024-01-15"
    ),
    warehouse_id: Optional[str] = Query(
        None,
        description="Filtrar por ID de almacén específico",
        example="WH-001"
    ),
    product_id: Optional[str] = Query(
        None,
        description="Filtrar por ID de producto específico",
        example="PRD-ELEC-001"
    )
):
    """
    Obtiene niveles de inventario para una fecha específica

    Args:
        date: Fecha en formato YYYY-MM-DD (opcional, por defecto ayer)
        warehouse_id: Filtrar por almacén específico (opcional)
        product_id: Filtrar por producto específico (opcional)

    Returns:
        JSON con datos de inventario del día

    Example Response:
    ```json
    {
        "date": "2024-01-15",
        "total_records": 500,
        "data": [
            {
                "date": "2024-01-15",
                "warehouse_id": "WH-001",
                "product_id": "PRD-ELEC-001",
                "quantity_on_hand": 5000,
                "quantity_reserved": 1200,
                "quantity_available": 3800,
                "reorder_point": 2000,
                "safety_stock_level": 1000
            }
        ]
    }
    ```
    """
    # Si no se proporciona fecha, usar ayer
    if date is None:
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    data = load_daily_data('inventory', date)

    # Aplicar filtros si se proporcionan
    filtered_data = data['data']

    if warehouse_id:
        filtered_data = [item for item in filtered_data if item['warehouse_id'] == warehouse_id]

    if product_id:
        filtered_data = [item for item in filtered_data if item['product_id'] == product_id]

    # Actualizar respuesta con datos filtrados
    response_data = {
        'date': date,
        'total_records': len(filtered_data),
        'filters_applied': {
            'warehouse_id': warehouse_id,
            'product_id': product_id
        } if (warehouse_id or product_id) else None,
        'data': filtered_data
    }

    return JSONResponse(
        content=response_data,
        headers={
            "X-Total-Records": str(len(filtered_data)),
            "X-Date": date
        }
    )


@app.get("/api/v1/dates/available")
async def get_available_dates(dataset: str = Query(..., description="Dataset a consultar")):
    """
    Obtiene lista de fechas disponibles para un dataset

    Args:
        dataset: Nombre del dataset ('shipments', 'purchase_orders', 'inventory')

    Returns:
        Lista de fechas disponibles
    """
    if dataset not in ['shipments', 'purchase_orders', 'inventory']:
        raise HTTPException(
            status_code=400,
            detail="Dataset debe ser 'shipments', 'purchase_orders' o 'inventory'"
        )

    dataset_path = DATA_DIR / dataset
    if not dataset_path.exists():
        return {"available_dates": [], "total": 0}

    # Buscar todos los archivos JSON
    dates = []
    for year_dir in dataset_path.iterdir():
        if year_dir.is_dir():
            for month_dir in year_dir.iterdir():
                if month_dir.is_dir():
                    for day_dir in month_dir.iterdir():
                        if day_dir.is_dir():
                            for file in day_dir.glob('*.json'):
                                # Extraer fecha del nombre del archivo
                                if dataset == 'shipments':
                                    date_str = file.stem.replace('shipments_', '')
                                elif dataset == 'purchase_orders':
                                    date_str = file.stem.replace('po_', '')
                                else:  # inventory
                                    date_str = file.stem.replace('inventory_', '')

                                dates.append(date_str)

    dates.sort()

    return {
        "dataset": dataset,
        "available_dates": dates,
        "total": len(dates),
        "first_date": dates[0] if dates else None,
        "last_date": dates[-1] if dates else None
    }


# Exception handler personalizado
@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request, exc):
    """
    Handler personalizado para excepciones HTTP
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "message": exc.detail,
            "timestamp": datetime.now().isoformat()
        }
    )


if __name__ == "__main__":
    """
    Ejecutar servidor de desarrollo
    """
    print("=" * 70)
    print("🚀 SUPPLY CHAIN TRANSACTIONAL DATA API")
    print("=" * 70)
    print("\n📡 Iniciando servidor FastAPI...")
    print(f"📂 Directorio de datos: {DATA_DIR.absolute()}")
    print("\n📚 Documentación disponible en:")
    print("   • Swagger UI: http://localhost:8000/docs")
    print("   • ReDoc:      http://localhost:8000/redoc")
    print("\n🔗 Endpoints disponibles:")
    print("   • GET /api/v1/shipments?date=YYYY-MM-DD")
    print("   • GET /api/v1/purchase-orders?date=YYYY-MM-DD")
    print("   • GET /api/v1/inventory?date=YYYY-MM-DD")
    print("   • GET /api/v1/health")
    print("=" * 70)
    print()

    # Ejecutar servidor
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
