"""
Generador de Datos Transaccionales para Supply Chain Analytics

Este script genera datos transaccionales diarios:
- Shipments (Envíos)
- Purchase Orders (Órdenes de Compra)
- Daily Inventory Levels (Niveles de Inventario)

Los datos se generan para un período de tiempo específico y se guardan
en formato JSON por fecha (simulando respuestas de API)
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

# Configuración
np.random.seed(42)
OUTPUT_DIR = "../output/transactional_data"


class SupplyChainDataGenerator:
    """
    Clase principal para generar datos transaccionales de supply chain
    """

    def __init__(self, start_date, end_date, num_products=500, num_warehouses=50, num_suppliers=100):
        """
        Inicializa el generador

        Args:
            start_date: Fecha de inicio (string YYYY-MM-DD)
            end_date: Fecha de fin (string YYYY-MM-DD)
            num_products: Número de productos
            num_warehouses: Número de almacenes
            num_suppliers: Número de proveedores
        """
        self.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        self.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        self.num_products = num_products
        self.num_warehouses = num_warehouses
        self.num_suppliers = num_suppliers

        # Crear estructuras de datos base
        self.products = [f"PRD-{i:04d}" for i in range(1, num_products + 1)]
        self.warehouses = [f"WH-{i:03d}" for i in range(1, num_warehouses + 1)]
        self.suppliers = [f"SUP-{i:03d}" for i in range(1, num_suppliers + 1)]

        # Carriers comunes
        self.carriers = ['DHL Express', 'FedEx', 'UPS', 'Maersk', 'DB Schenker',
                        'XPO Logistics', 'C.H. Robinson', 'Kuehne+Nagel', 'DSV']

        # Modos de transporte
        self.transport_modes = ['air', 'sea', 'road', 'rail']

        # Contadores globales para IDs
        self.shipment_counter = 1
        self.po_counter = 1
        self.order_counter = 1

        # Estado de inventario (se actualiza dinámicamente)
        self.inventory_state = self._initialize_inventory()

        print(f"Período: {start_date} a {end_date}")
        print(f"Configuración: {num_products} productos, {num_warehouses} almacenes, {num_suppliers} proveedores")

    def _initialize_inventory(self):
        """
        Inicializa el estado de inventario para cada combinación producto-almacén
        """
        inventory = {}
        for warehouse in self.warehouses:
            for product in self.products:
                # Inventario inicial aleatorio
                initial_stock = np.random.randint(1000, 10000)
                inventory[(warehouse, product)] = {
                    'quantity_on_hand': initial_stock,
                    'quantity_reserved': 0,
                    'reorder_point': np.random.randint(500, 2000),
                    'safety_stock': np.random.randint(300, 1000)
                }
        return inventory

    def generate_shipments(self, date, num_shipments=None):
        """
        Genera envíos para una fecha específica

        Args:
            date: Fecha del envío
            num_shipments: Número de envíos (aleatorio si None)

        Returns:
            Lista de diccionarios con datos de envíos
        """
        if num_shipments is None:
            # Más envíos en días laborables
            if date.weekday() < 5:  # Lunes a Viernes
                num_shipments = np.random.randint(150, 250)
            else:  # Fin de semana
                num_shipments = np.random.randint(50, 100)

        shipments = []

        for _ in range(num_shipments):
            # Seleccionar almacén origen y destino
            origin_warehouse = np.random.choice(self.warehouses)

            # Destinos comunes (ciudades principales)
            destinations = [
                'New York, NY, USA', 'Los Angeles, CA, USA', 'Chicago, IL, USA',
                'London, UK', 'Paris, France', 'Berlin, Germany',
                'Tokyo, Japan', 'Shanghai, China', 'Mumbai, India',
                'São Paulo, Brazil', 'Toronto, Canada', 'Sydney, Australia'
            ]
            destination = np.random.choice(destinations)

            # Seleccionar producto y cantidad
            product_id = np.random.choice(self.products)
            quantity = np.random.randint(50, 2000)

            # Modo de transporte influye en costo y tiempo
            transport_mode = np.random.choice(self.transport_modes, p=[0.15, 0.30, 0.45, 0.10])

            # Calcular fechas de entrega
            if transport_mode == 'air':
                delivery_days = np.random.randint(1, 5)
                cost_per_unit = np.random.uniform(5, 15)
            elif transport_mode == 'road':
                delivery_days = np.random.randint(2, 10)
                cost_per_unit = np.random.uniform(1, 5)
            elif transport_mode == 'sea':
                delivery_days = np.random.randint(15, 45)
                cost_per_unit = np.random.uniform(0.5, 2)
            else:  # rail
                delivery_days = np.random.randint(5, 15)
                cost_per_unit = np.random.uniform(1, 4)

            scheduled_delivery = date + timedelta(days=delivery_days)

            # Simular retrasos (20% de probabilidad)
            if np.random.random() < 0.20:
                delay_days = np.random.randint(1, 7)
                actual_delivery = scheduled_delivery + timedelta(days=delay_days)
                status = 'delayed' if actual_delivery > datetime.now() else 'delivered'
            else:
                actual_delivery = scheduled_delivery
                delay_days = 0
                status = 'delivered' if actual_delivery < datetime.now() else 'in_transit'

            # Calcular costo total
            shipping_cost = round(quantity * cost_per_unit * np.random.uniform(0.8, 1.2), 2)

            # Crear orden relacionada
            order_id = f"ORD-{date.year}-{self.order_counter:06d}"
            self.order_counter += 1

            shipment = {
                'shipment_id': f"SHP-{date.year}-{self.shipment_counter:06d}",
                'order_id': order_id,
                'origin_warehouse': origin_warehouse,
                'destination_location': destination,
                'product_id': product_id,
                'quantity': quantity,
                'shipment_date': date.strftime('%Y-%m-%d'),
                'scheduled_delivery_date': scheduled_delivery.strftime('%Y-%m-%d'),
                'actual_delivery_date': actual_delivery.strftime('%Y-%m-%d'),
                'carrier': np.random.choice(self.carriers),
                'transportation_mode': transport_mode,
                'shipping_cost': shipping_cost,
                'status': status,
                'delay_days': delay_days
            }

            shipments.append(shipment)
            self.shipment_counter += 1

        return shipments

    def generate_purchase_orders(self, date, num_orders=None):
        """
        Genera órdenes de compra para una fecha específica

        Args:
            date: Fecha de la orden
            num_orders: Número de órdenes (aleatorio si None)

        Returns:
            Lista de diccionarios con datos de órdenes de compra
        """
        if num_orders is None:
            # Menos órdenes en fin de semana
            if date.weekday() < 5:
                num_orders = np.random.randint(50, 100)
            else:
                num_orders = np.random.randint(10, 30)

        purchase_orders = []

        for _ in range(num_orders):
            supplier_id = np.random.choice(self.suppliers)
            product_id = np.random.choice(self.products)

            # Cantidad ordenada (órdenes grandes)
            quantity = np.random.choice([500, 1000, 2500, 5000, 10000])

            # Precio unitario
            unit_price = round(np.random.uniform(5, 500), 2)
            total_cost = round(quantity * unit_price, 2)

            # Lead time depende del proveedor (simulado)
            lead_time = np.random.randint(7, 60)
            expected_delivery = date + timedelta(days=lead_time)

            # Simular entregas (80% completas, 15% retrasadas, 5% pendientes)
            status_prob = np.random.random()
            if status_prob < 0.80:
                status = 'completed'
                # Añadir variación en entrega
                actual_delay = np.random.randint(-3, 10)  # Puede llegar antes o después
                actual_delivery = expected_delivery + timedelta(days=actual_delay)
            elif status_prob < 0.95:
                status = 'delayed'
                actual_delay = np.random.randint(5, 20)
                actual_delivery = expected_delivery + timedelta(days=actual_delay)
            else:
                status = 'pending'
                actual_delivery = None
                actual_delay = 0

            po = {
                'po_id': f"PO-{date.year}-{self.po_counter:06d}",
                'supplier_id': supplier_id,
                'product_id': product_id,
                'order_date': date.strftime('%Y-%m-%d'),
                'quantity_ordered': quantity,
                'unit_price': unit_price,
                'total_cost': total_cost,
                'expected_delivery_date': expected_delivery.strftime('%Y-%m-%d'),
                'actual_delivery_date': actual_delivery.strftime('%Y-%m-%d') if actual_delivery else None,
                'order_status': status,
                'delay_days': actual_delay
            }

            purchase_orders.append(po)
            self.po_counter += 1

        return purchase_orders

    def generate_daily_inventory(self, date):
        """
        Genera niveles de inventario para una fecha específica

        Args:
            date: Fecha del snapshot de inventario

        Returns:
            Lista de diccionarios con datos de inventario
        """
        inventory_records = []

        # Simular cambios diarios en inventario
        for (warehouse, product), state in self.inventory_state.items():
            # Simular ventas/salidas diarias
            daily_sales = np.random.randint(0, 200)

            # Simular recepciones (menos frecuentes)
            if np.random.random() < 0.05:  # 5% de probabilidad
                receipt = np.random.randint(500, 5000)
            else:
                receipt = 0

            # Actualizar inventario
            state['quantity_on_hand'] = state['quantity_on_hand'] - daily_sales + receipt

            # Evitar inventario negativo
            if state['quantity_on_hand'] < 0:
                state['quantity_on_hand'] = 0

            # Simular reservas (órdenes pendientes)
            state['quantity_reserved'] = np.random.randint(0, int(state['quantity_on_hand'] * 0.3))

            # Calcular disponible
            quantity_available = state['quantity_on_hand'] - state['quantity_reserved']

            record = {
                'date': date.strftime('%Y-%m-%d'),
                'warehouse_id': warehouse,
                'product_id': product,
                'quantity_on_hand': state['quantity_on_hand'],
                'quantity_reserved': state['quantity_reserved'],
                'quantity_available': max(0, quantity_available),
                'reorder_point': state['reorder_point'],
                'safety_stock_level': state['safety_stock']
            }

            inventory_records.append(record)

        return inventory_records

    def save_daily_data(self, date, shipments, purchase_orders, inventory):
        """
        Guarda datos del día en formato JSON (simulando respuesta de API)

        Args:
            date: Fecha de los datos
            shipments: Lista de envíos
            purchase_orders: Lista de órdenes de compra
            inventory: Lista de registros de inventario
        """
        date_str = date.strftime('%Y-%m-%d')
        year = date.strftime('%Y')
        month = date.strftime('%m')
        day = date.strftime('%d')

        # Crear estructura de carpetas por fecha
        for dataset_name in ['shipments', 'purchase_orders', 'inventory']:
            path = Path(OUTPUT_DIR) / dataset_name / year / month / day
            path.mkdir(parents=True, exist_ok=True)

        # Guardar shipments
        shipments_data = {
            'date': date_str,
            'total_records': len(shipments),
            'data': shipments
        }
        filepath = Path(OUTPUT_DIR) / 'shipments' / year / month / day / f'shipments_{date_str}.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(shipments_data, f, indent=2, ensure_ascii=False)

        # Guardar purchase orders
        po_data = {
            'date': date_str,
            'total_records': len(purchase_orders),
            'data': purchase_orders
        }
        filepath = Path(OUTPUT_DIR) / 'purchase_orders' / year / month / day / f'po_{date_str}.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(po_data, f, indent=2, ensure_ascii=False)

        # Guardar inventory
        inventory_data = {
            'date': date_str,
            'total_records': len(inventory),
            'data': inventory
        }
        filepath = Path(OUTPUT_DIR) / 'inventory' / year / month / day / f'inventory_{date_str}.json'
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(inventory_data, f, indent=2, ensure_ascii=False)

    def generate_all(self):
        """
        Genera todos los datos para el rango de fechas completo
        """
        current_date = self.start_date
        total_days = (self.end_date - self.start_date).days + 1

        print(f"\n🔄 Generando datos para {total_days} días...\n")

        day_counter = 0
        while current_date <= self.end_date:
            day_counter += 1

            # Generar datos del día
            shipments = self.generate_shipments(current_date)
            purchase_orders = self.generate_purchase_orders(current_date)
            inventory = self.generate_daily_inventory(current_date)

            # Guardar datos
            self.save_daily_data(current_date, shipments, purchase_orders, inventory)

            # Progreso
            if day_counter % 30 == 0 or day_counter == total_days:
                progress = (day_counter / total_days) * 100
                print(f"📊 Progreso: {day_counter}/{total_days} días ({progress:.1f}%) - "
                      f"{current_date.strftime('%Y-%m-%d')}")

            current_date += timedelta(days=1)

        print(f"\n✅ Generación completada!")


def main():
    """
    Función principal
    """
    print("=" * 70)
    print("GENERADOR DE DATOS TRANSACCIONALES - SUPPLY CHAIN ANALYTICS")
    print("Equivalente a ECDC del proyecto COVID-19")
    print("=" * 70)
    print()

    # Configuración del período de datos
    # Generar 1 año de datos (similar al proyecto COVID-19)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)

    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Crear generador
    generator = SupplyChainDataGenerator(
        start_date=start_date_str,
        end_date=end_date_str,
        num_products=500,
        num_warehouses=50,
        num_suppliers=100
    )

    # Generar todos los datos
    generator.generate_all()

    # Estadísticas finales
    print("\n" + "=" * 70)
    print("📈 ESTADÍSTICAS FINALES")
    print("=" * 70)
    print(f"Total de envíos: ~{generator.shipment_counter - 1:,}")
    print(f"Total de órdenes de compra: ~{generator.po_counter - 1:,}")
    print(f"Snapshots de inventario: {(generator.num_products * generator.num_warehouses * 365):,}")
    print(f"\n📂 Ubicación: {OUTPUT_DIR}/")
    print("\n🎯 PRÓXIMO PASO: Crear API FastAPI para servir estos datos")
    print("=" * 70)


if __name__ == "__main__":
    main()
