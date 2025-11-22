"""
Generador de Datos Maestros para Supply Chain Analytics

Este script genera archivos CSV con datos de referencia estáticos:
- Products Master
- Suppliers Master
- Warehouses Master
- Demand Demographics

"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

# Configuración de semilla para reproducibilidad
np.random.seed(42)

# Configuración de rutas de salida
OUTPUT_DIR = "../output/master_data"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def generate_products_master(num_products=500):
    """
    Genera catálogo maestro de productos

    Args:
        num_products: Número de productos a generar

    Returns:
        DataFrame con información de productos
    """
    print(f"Generando {num_products} productos...")

    # Definir categorías y subcategorías
    categories = {
        'Electronics': ['Mobile Phones', 'Laptops', 'Tablets', 'Accessories', 'Smart Home'],
        'Food & Beverage': ['Dairy', 'Beverages', 'Snacks', 'Frozen Foods', 'Fresh Produce'],
        'Apparel': ['Clothing', 'Footwear', 'Accessories', 'Sportswear'],
        'Home & Garden': ['Furniture', 'Kitchen', 'Decor', 'Tools', 'Outdoor'],
        'Beauty & Health': ['Skincare', 'Cosmetics', 'Supplements', 'Personal Care'],
        'Toys & Games': ['Educational', 'Action Figures', 'Board Games', 'Outdoor Toys'],
        'Automotive': ['Parts', 'Accessories', 'Fluids', 'Tools'],
        'Books & Media': ['Books', 'Music', 'Movies', 'Software']
    }

    products = []
    product_id = 1

    for category, subcategories in categories.items():
        # Determinar cuántos productos por categoría
        products_per_category = num_products // len(categories)

        for _ in range(products_per_category):
            subcategory = np.random.choice(subcategories)

            # Generar características basadas en categoría
            if category == 'Electronics':
                unit_cost = np.random.uniform(50, 800)
                margin = np.random.uniform(1.3, 2.5)
                weight = np.random.uniform(0.1, 3.0)
                volume = np.random.uniform(0.0001, 0.01)
                perishable = 'no'
                shelf_life = None
                hs_code = '8517.12.00'
            elif category == 'Food & Beverage':
                unit_cost = np.random.uniform(0.5, 50)
                margin = np.random.uniform(1.2, 2.0)
                weight = np.random.uniform(0.1, 2.0)
                volume = np.random.uniform(0.0001, 0.005)
                perishable = 'yes' if subcategory in ['Dairy', 'Fresh Produce', 'Frozen Foods'] else 'no'
                shelf_life = np.random.randint(3, 90) if perishable == 'yes' else None
                hs_code = '0401.10.10'
            elif category == 'Apparel':
                unit_cost = np.random.uniform(5, 150)
                margin = np.random.uniform(2.0, 4.0)
                weight = np.random.uniform(0.1, 1.5)
                volume = np.random.uniform(0.001, 0.01)
                perishable = 'no'
                shelf_life = None
                hs_code = '6109.10.00'
            else:
                unit_cost = np.random.uniform(2, 200)
                margin = np.random.uniform(1.5, 3.0)
                weight = np.random.uniform(0.1, 10.0)
                volume = np.random.uniform(0.0001, 0.1)
                perishable = 'no'
                shelf_life = None
                hs_code = f"{np.random.randint(1000, 9999)}.{np.random.randint(10, 99)}.00"

            unit_price = round(unit_cost * margin, 2)

            # Crear ID de producto
            cat_prefix = category[:4].upper()
            prod_id = f"PRD-{cat_prefix}-{product_id:04d}"

            # Generar nombre de producto
            adjectives = ['Premium', 'Essential', 'Classic', 'Modern', 'Pro', 'Lite', 'Ultra', 'Eco']
            product_name = f"{np.random.choice(adjectives)} {subcategory} {np.random.randint(100, 999)}"

            products.append({
                'product_id': prod_id,
                'product_name': product_name,
                'category': category,
                'subcategory': subcategory,
                'unit_cost': round(unit_cost, 2),
                'unit_price': unit_price,
                'weight_kg': round(weight, 2),
                'volume_m3': round(volume, 4),
                'hs_code': hs_code,
                'perishable': perishable,
                'shelf_life_days': shelf_life if shelf_life else ''
            })

            product_id += 1

    df = pd.DataFrame(products)
    print(f" Generados {len(df)} productos en {df['category'].nunique()} categorías")
    return df


def generate_suppliers_master(num_suppliers=100):
    """
    Genera catálogo maestro de proveedores

    Args:
        num_suppliers: Número de proveedores a generar

    Returns:
        DataFrame con información de proveedores
    """
    print(f" Generando {num_suppliers} proveedores...")

    # Países principales de manufactura
    supplier_countries = {
        'China': ['Shenzhen', 'Shanghai', 'Guangzhou', 'Beijing', 'Dongguan'],
        'United States': ['Chicago', 'Los Angeles', 'New York', 'Houston', 'Seattle'],
        'Germany': ['Munich', 'Frankfurt', 'Hamburg', 'Berlin', 'Cologne'],
        'Japan': ['Tokyo', 'Osaka', 'Nagoya', 'Yokohama'],
        'South Korea': ['Seoul', 'Busan', 'Incheon'],
        'Vietnam': ['Ho Chi Minh City', 'Hanoi', 'Da Nang'],
        'India': ['Mumbai', 'Delhi', 'Bangalore', 'Chennai'],
        'Italy': ['Milan', 'Rome', 'Turin', 'Bologna'],
        'Mexico': ['Mexico City', 'Monterrey', 'Guadalajara'],
        'United Kingdom': ['London', 'Manchester', 'Birmingham']
    }

    company_types = ['Ltd', 'Corp', 'GmbH', 'Inc', 'Co', 'Industries', 'Manufacturing', 'Supply']
    company_prefixes = ['Tech', 'Global', 'Precision', 'Quality', 'Premier', 'Advanced', 'Elite', 'Supreme']
    company_suffixes = ['Solutions', 'Parts', 'Products', 'Manufacturing', 'Supply', 'Industries']

    suppliers = []

    for i in range(num_suppliers):
        country = np.random.choice(list(supplier_countries.keys()))
        city = np.random.choice(supplier_countries[country])

        # Generar nombre de compañía
        if country == 'Germany':
            company_type = 'GmbH'
        elif country in ['China', 'Japan', 'South Korea']:
            company_type = 'Ltd'
        else:
            company_type = np.random.choice(company_types)

        company_name = f"{np.random.choice(company_prefixes)}{np.random.choice(company_suffixes)} {company_type}"

        # ID de proveedor
        country_code = country[:2].upper()
        supplier_id = f"SUP-{country_code}-{i+1:03d}"

        # Rating influenciado por país (estereotipos de calidad)
        if country in ['Germany', 'Japan']:
            base_rating = np.random.uniform(4.0, 5.0)
        elif country in ['United States', 'South Korea', 'United Kingdom']:
            base_rating = np.random.uniform(3.5, 4.8)
        else:
            base_rating = np.random.uniform(3.0, 4.5)

        # Lead time influenciado por ubicación
        if country in ['China', 'Vietnam', 'India']:
            lead_time = np.random.randint(25, 60)
        elif country in ['Mexico']:
            lead_time = np.random.randint(10, 25)
        else:
            lead_time = np.random.randint(7, 30)

        # Mínimo de orden
        moq = np.random.choice([100, 250, 500, 1000, 2500, 5000, 10000])

        # Términos de pago
        payment_terms = np.random.choice(['Net 30', 'Net 45', 'Net 60', 'Net 90', '2/10 Net 30'])

        # Certificaciones
        certifications = np.random.choice([
            'ISO 9001',
            'ISO 9001 + ISO 14001',
            'ISO 9001 + ISO 14001 + ISO 45001',
            'ISO 9001 + IATF 16949',
            'None'
        ], p=[0.4, 0.3, 0.15, 0.10, 0.05])

        suppliers.append({
            'supplier_id': supplier_id,
            'supplier_name': company_name,
            'country': country,
            'city': city,
            'supplier_rating': round(base_rating, 1),
            'average_lead_time_days': lead_time,
            'minimum_order_quantity': moq,
            'payment_terms': payment_terms,
            'certification_level': certifications
        })

    df = pd.DataFrame(suppliers)
    print(f"Generados {len(df)} proveedores en {df['country'].nunique()} países")
    return df


def generate_warehouses_master(num_warehouses=50):
    """
    Genera catálogo maestro de almacenes/centros de distribución

    Args:
        num_warehouses: Número de almacenes a generar

    Returns:
        DataFrame con información de almacenes
    """
    print(f" Generando {num_warehouses} almacenes...")

    # Ubicaciones principales de distribución
    warehouse_locations = {
        'United States': [
            ('New York', 40.7128, -74.0060),
            ('Los Angeles', 34.0522, -118.2437),
            ('Chicago', 41.8781, -87.6298),
            ('Dallas', 32.7767, -96.7970),
            ('Atlanta', 33.7490, -84.3880),
            ('Seattle', 47.6062, -122.3321),
            ('Miami', 25.7617, -80.1918)
        ],
        'United Kingdom': [
            ('London', 51.5074, -0.1278),
            ('Manchester', 53.4808, -2.2426),
            ('Birmingham', 52.4862, -1.8904)
        ],
        'Germany': [
            ('Frankfurt', 50.1109, 8.6821),
            ('Hamburg', 53.5511, 9.9937),
            ('Munich', 48.1351, 11.5820)
        ],
        'China': [
            ('Shanghai', 31.2304, 121.4737),
            ('Shenzhen', 22.5431, 114.0579),
            ('Beijing', 39.9042, 116.4074),
            ('Guangzhou', 23.1291, 113.2644)
        ],
        'Japan': [
            ('Tokyo', 35.6762, 139.6503),
            ('Osaka', 34.6937, 135.5023)
        ],
        'Australia': [
            ('Sydney', -33.8688, 151.2093),
            ('Melbourne', -37.8136, 144.9631)
        ],
        'Canada': [
            ('Toronto', 43.6532, -79.3832),
            ('Vancouver', 49.2827, -123.1207)
        ],
        'Netherlands': [
            ('Rotterdam', 51.9225, 4.4792),
            ('Amsterdam', 52.3676, 4.9041)
        ],
        'Singapore': [
            ('Singapore', 1.3521, 103.8198)
        ],
        'United Arab Emirates': [
            ('Dubai', 25.2048, 55.2708)
        ]
    }

    warehouses = []
    wh_id = 1

    for country, locations in warehouse_locations.items():
        for city, lat, lon in locations:
            if wh_id > num_warehouses:
                break

            # Código de país
            country_code = country[:2].upper()
            city_code = city[:2].upper()

            warehouse_id = f"WH-{country_code}-{city_code}-{wh_id:03d}"

            # Nombre del almacén
            warehouse_types = ['Distribution Center', 'Fulfillment Hub', 'Warehouse',
                              'Logistics Center', 'Regional DC']
            warehouse_name = f"{city} {np.random.choice(warehouse_types)}"

            # Capacidad basada en importancia del mercado
            if country in ['United States', 'China']:
                capacity = np.random.randint(30000, 100000)
            else:
                capacity = np.random.randint(15000, 50000)

            # Número de muelles
            docks = int(capacity / 2500)  # Aproximadamente 1 muelle por 2500 m3
            docks = max(8, min(docks, 48))  # Entre 8 y 48 muelles

            # Operación 24/7 (más probable en hubs grandes)
            operates_24_7 = 'yes' if capacity > 50000 or np.random.random() > 0.6 else 'no'

            # Nivel tecnológico
            tech_level = np.random.choice(
                ['basic', 'advanced', 'automated'],
                p=[0.2, 0.5, 0.3]
            )

            warehouses.append({
                'warehouse_id': warehouse_id,
                'warehouse_name': warehouse_name,
                'country': country,
                'city': city,
                'latitude': round(lat, 4),
                'longitude': round(lon, 4),
                'storage_capacity_m3': capacity,
                'number_of_docks': docks,
                'operates_24_7': operates_24_7,
                'technology_level': tech_level
            })

            wh_id += 1

    df = pd.DataFrame(warehouses)
    print(f" Generados {len(df)} almacenes en {df['country'].nunique()} países")
    return df


def generate_demand_demographics(num_regions=50):
    """
    Genera datos demográficos y económicos por región

    Args:
        num_regions: Número de regiones a generar

    Returns:
        DataFrame con información demográfica
    """
    print(f" Generando datos demográficos para {num_regions} regiones...")

    # Datos reales aproximados de países principales
    real_demographics = {
        'United States': (331900000, 63543, 82.7, 67521, 76.2),
        'China': (1439323776, 10500, 61.4, 10410, 52.1),
        'Japan': (126476461, 40246, 91.8, 42274, 68.9),
        'Germany': (83783942, 46445, 77.5, 47730, 73.5),
        'United Kingdom': (67886011, 42330, 83.9, 44770, 82.5),
        'France': (65273511, 40494, 81.0, 42485, 71.3),
        'India': (1380004385, 1900, 35.0, 2150, 14.5),
        'Italy': (60461826, 33228, 71.0, 35220, 58.7),
        'Brazil': (212559417, 8717, 87.1, 9130, 41.2),
        'Canada': (37742154, 46195, 81.6, 50370, 85.1),
        'South Korea': (51269185, 31846, 81.4, 33590, 89.3),
        'Spain': (46754778, 29600, 80.8, 30090, 67.8),
        'Australia': (25499884, 51812, 86.2, 53320, 81.7),
        'Netherlands': (17134872, 52477, 92.2, 52960, 79.4),
        'Mexico': (128932753, 9946, 80.7, 9760, 35.8),
        'Indonesia': (273523615, 4136, 56.6, 4260, 19.3),
        'Turkey': (84339067, 9126, 75.6, 9610, 39.2),
        'Saudi Arabia': (34813871, 23186, 84.3, 23140, 48.5),
        'Switzerland': (8654622, 82796, 73.9, 85500, 82.3),
        'Poland': (37846611, 15656, 60.1, 15420, 54.1),
        'Belgium': (11589623, 46553, 98.0, 47260, 74.6),
        'Sweden': (10099265, 54146, 88.2, 54630, 83.9),
        'Argentina': (45195774, 10006, 92.1, 9930, 34.7),
        'UAE': (9890402, 43103, 87.0, 44315, 62.1),
        'Norway': (5421241, 75389, 83.1, 74940, 88.6),
        'Austria': (9006398, 50277, 58.5, 50870, 69.4),
        'Denmark': (5792202, 60494, 88.1, 61350, 84.2),
        'Singapore': (5850342, 59797, 100.0, 98520, 73.5),
        'Malaysia': (32365999, 11414, 77.2, 11200, 53.7),
        'Israel': (8655535, 43610, 92.6, 43610, 61.3),
        'Hong Kong': (7496981, 48517, 100.0, 48630, 71.8),
        'Finland': (5540720, 48461, 85.5, 47300, 77.9),
        'Chile': (19116201, 14896, 87.7, 14670, 45.6),
        'Portugal': (10196709, 23408, 66.3, 23210, 52.3),
        'Greece': (10423054, 18613, 79.7, 18090, 38.9),
        'Czech Republic': (10708981, 23494, 74.1, 23280, 63.4),
        'Romania': (19237691, 12896, 54.4, 12900, 42.1),
        'New Zealand': (4822233, 42018, 86.7, 41760, 79.8),
        'Vietnam': (97338579, 2715, 37.3, 2720, 31.4),
        'Philippines': (109581078, 3485, 47.4, 3430, 24.8),
        'Bangladesh': (164689383, 1961, 38.2, 1940, 9.7),
        'Egypt': (102334404, 3547, 42.8, 3520, 18.2),
        'Pakistan': (220892340, 1285, 37.2, 1260, 12.4),
        'Colombia': (50882891, 6131, 81.4, 6110, 28.9),
        'South Africa': (59308690, 6001, 67.4, 5900, 34.5),
        'Thailand': (69799978, 7806, 51.4, 7820, 42.8),
        'Peru': (32971854, 6692, 78.3, 6650, 31.2),
        'Kenya': (53771296, 1816, 27.5, 1800, 8.9),
        'Nigeria': (206139589, 2097, 52.0, 2100, 15.3),
        'Morocco': (36910560, 3204, 63.5, 3190, 22.7),
        'Ukraine': (43733762, 3726, 69.7, 3660, 28.1)
    }

    demographics = []

    for i, (country, (pop, gdp, urban, income, ecom)) in enumerate(real_demographics.items(), 1):
        if i > num_regions:
            break

        region_id = f"REG-{country[:2].upper()}-{i:03d}"

        # Añadir algo de variabilidad a los datos
        population = int(pop * np.random.uniform(0.95, 1.05))
        gdp_per_capita = round(gdp * np.random.uniform(0.95, 1.05), 2)
        urbanization = round(urban * np.random.uniform(0.98, 1.02), 1)
        avg_income = int(income * np.random.uniform(0.95, 1.05))
        ecommerce = round(ecom * np.random.uniform(0.95, 1.05), 1)

        demographics.append({
            'region_id': region_id,
            'country': country,
            'population': population,
            'gdp_per_capita': gdp_per_capita,
            'urbanization_rate': min(100.0, urbanization),
            'avg_household_income': avg_income,
            'ecommerce_penetration_rate': min(100.0, ecommerce)
        })

    df = pd.DataFrame(demographics)
    print(f" Generados datos demográficos para {len(df)} regiones")
    return df


def save_to_tsv_compressed(df, filename, subfolder=''):
    """
    Save DataFrame to compressed TSV file

    Args:
        df: DataFrame to save
        filename: File name (will be changed to .tsv.gz)
        subfolder: Subfolder within OUTPUT_DIR
    """
    # Change extension to .tsv.gz
    filename = filename.replace('.csv', '.tsv.gz')

    if subfolder:
        path = os.path.join(OUTPUT_DIR, subfolder)
        os.makedirs(path, exist_ok=True)
        filepath = os.path.join(path, filename)
    else:
        filepath = os.path.join(OUTPUT_DIR, filename)

    # Save as compressed TSV
    df.to_csv(filepath, sep='\t', index=False, encoding='utf-8', compression='gzip')
    file_size = os.path.getsize(filepath) / 1024  # KB
    print(f"Saved: {filepath} ({file_size:.1f} KB)")


def main():
    """
    Función principal para generar todos los datos maestros
    """
    print("=" * 70)
    print("GENERADOR DE DATOS MAESTROS - SUPPLY CHAIN ANALYTICS")
    print("Equivalente a Eurostat del proyecto COVID-19")
    print("=" * 70)
    print()

    # Generar cada dataset
    print("\n GENERANDO DATASETS...\n")

    # 1. Products Master
    products_df = generate_products_master(num_products=500)
    save_to_tsv_compressed(products_df, 'products_master.csv', 'products')

    print()

    # 2. Suppliers Master
    suppliers_df = generate_suppliers_master(num_suppliers=100)
    save_to_tsv_compressed(suppliers_df, 'suppliers_master.csv', 'suppliers')

    print()

    # 3. Warehouses Master
    warehouses_df = generate_warehouses_master(num_warehouses=50)
    save_to_tsv_compressed(warehouses_df, 'warehouses_master.csv', 'warehouses')

    print()

    # 4. Demand Demographics
    demographics_df = generate_demand_demographics(num_regions=50)
    save_to_tsv_compressed(demographics_df, 'demand_demographics.csv', 'demographics')

    # Resumen final
    print("\n" + "=" * 70)
    print(" GENERACIÓN COMPLETADA")
    print("=" * 70)
    print(f"\n RESUMEN:")
    print(f"  • Productos:    {len(products_df):,} registros")
    print(f"  • Proveedores:  {len(suppliers_df):,} registros")
    print(f"  • Almacenes:    {len(warehouses_df):,} registros")
    print(f"  • Regiones:     {len(demographics_df):,} registros")
    print(f"\n Ubicación: {OUTPUT_DIR}/")
    print("\n PRÓXIMO PASO: Subir estos archivos a Azure Blob Storage")
    print("=" * 70)


if __name__ == "__main__":
    main()
