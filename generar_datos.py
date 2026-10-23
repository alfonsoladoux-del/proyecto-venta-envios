import random, uuid  # Genera ventas_envios.csv (datos sinteticos, semilla fija)
import pandas as pd
from datetime import datetime, timedelta
random.seed(42)

catalog = {
 "Electronica": {"Celulares":["Smartphone","Funda protectora","Cargador rapido"],
                 "Computacion":["Notebook","Mouse inalambrico","Teclado mecanico","Monitor 24"],
                 "Audio":["Auriculares Bluetooth","Parlante portatil","Barra de sonido"]},
 "Hogar": {"Cocina":["Cafetera","Licuadora","Set de sartenes","Tostadora"],
           "Decoracion":["Lampara de mesa","Cuadro decorativo","Almohadon"],
           "Muebles":["Escritorio","Silla ergonomica","Estante"]},
 "Indumentaria": {"Hombre":["Remera algodon","Jean clasico","Campera"],
                  "Mujer":["Vestido","Blusa","Jean skinny"],
                  "Calzado":["Zapatillas running","Botas","Sandalias"]},
 "Deportes": {"Fitness":["Mancuernas","Colchoneta yoga","Banda elastica"],
              "Aire libre":["Mochila trekking","Carpa 3p","Botella termica"]},
 "Belleza": {"Cuidado facial":["Crema hidratante","Protector solar","Serum vitamina C"],
             "Cuidado capilar":["Shampoo","Acondicionador","Secador de pelo"]},
 "Juguetes": {"Juegos de mesa":["Juego de estrategia","Rompecabezas 1000"],
              "Infantil":["Bloques de construccion","Muneca","Auto a control remoto"]},
}
brands = ["Nova","Altiva","Kora","Vento","Urban Co","Lumen","Terra","Zenit","Aurea","Pico"]
groups = ["Essentials","Premium","Seasonal","Core","Limited"]
channels = ["Organic Search","Paid Search","Direct","Email","Social Media","Affiliates","Referral"]
countries = {"Argentina":(["Buenos Aires","Cordoba","Rosario","Mendoza","Tucuman"],"ARS",1.0),
             "Chile":(["Santiago","Valparaiso","Concepcion"],"CLP",0.9),
             "Uruguay":(["Montevideo","Salto"],"UYU",1.1),
             "Mexico":(["CDMX","Guadalajara","Monterrey"],"MXN",1.0),
             "Colombia":(["Bogota","Medellin","Cali"],"COP",0.95),
             "Espana":(["Madrid","Barcelona","Valencia"],"EUR",1.2)}
cweights=[35,15,8,18,14,10]
pays=["Tarjeta credito","Tarjeta debito","Mercado Pago","Transferencia","PayPal","Efectivo"]
ships=["Estandar","Express","Retiro en sucursal","Mismo dia"]
carriers=["Andreani","OCA","Correo Argentino","DHL","FedEx","UPS"]
wh=["WH-Buenos Aires","WH-Cordoba","WH-Santiago","WH-CDMX","WH-Madrid"]

# product master
products=[]; pid=100000
for cat,subs in catalog.items():
    for sub,names in subs.items():
        for n in names:
            for b in random.sample(brands,3):
                pid+=1
                products.append(dict(product_id=pid,category=cat,subcategory=sub,
                    product_name=f"{b} {n}",brand=b,product_group=random.choice(groups),
                    sust=random.random()<0.25,elev=random.random()<0.18,
                    price=round(random.uniform(8,900)*(3 if cat=="Electronica" else 1),2)))
customers=[f"C{n:06d}" for n in range(1,2201)]
shoppers={c:f"S{random.randint(10**6,10**7-1)}" for c in customers}

rows=[]; start=datetime(2025,1,1); span=(datetime(2026,10,14)-start).days
oid=500000
while len(rows)<5000:
    oid+=1
    cust=random.choice(customers)
    created=start+timedelta(days=random.randint(0,span),hours=random.randint(0,23),minutes=random.randint(0,59),seconds=random.randint(0,59))
    cart="CART-"+uuid.uuid4().hex[:10].upper()
    country=random.choices(list(countries),cweights)[0]
    cities,cur,fx=countries[country]
    city=random.choice(cities)
    chan=random.choices(channels,[28,22,18,12,10,6,4])[0]
    pay=random.choice(pays); ship=random.choices(ships,[55,25,12,8])[0]
    carrier=random.choice(carriers); whs=random.choice(wh)
    release=created+timedelta(hours=random.randint(1,72))
    delay={"Estandar":random.randint(3,9),"Express":random.randint(1,3),"Retiro en sucursal":random.randint(2,5),"Mismo dia":0}[ship]
    shipd=release+timedelta(hours=random.randint(2,24))
    deliv=shipd+timedelta(days=delay)
    status_roll=random.random()
    if (datetime(2026,10,15)-created).days<5 and status_roll<0.6: status="En preparacion"
    else: status=random.choices(["Entregado","En transito","Cancelado","Devuelto"],[84,5,6,5])[0]
    if status in("En preparacion","Cancelado"): shipd=deliv=None
    elif status=="En transito": deliv=None
    for i in range(random.choices([1,2,3,4],[55,28,12,5])[0]):
        if len(rows)>=5000: break
        p=random.choice(products); q=random.choices([1,2,3,4,5],[60,22,10,5,3])[0]
        disc=random.choice([0,0,0,5,10,15,20,30])
        unit=round(p["price"]*fx,2); sub=round(unit*q*(1-disc/100),2)
        rows.append(dict(
         order_item_key=f"{oid}-{i+1}-{p['product_id']}",customer_id=cust,order_shopper_id=shoppers[cust],
         order_null=f"ORD-{oid}",cart_id=cart,quantity=q,order_created_date=created.strftime("%Y-%m-%d"),
         order_release_date_utc=release.strftime("%Y-%m-%d %H:%M:%S"),category=p["category"],subcategory=p["subcategory"],
         product_id=p["product_id"],product_group=p["product_group"],is_sustainable_product=p["sust"],
         is_elevated_product=p["elev"],product_name=p["product_name"],channel_group=chan,country=country,
         brand=p["brand"],city=city,currency=cur,unit_price=unit,discount_pct=disc,total_amount=sub,
         payment_method=pay,order_status=status,shipping_method=ship,carrier=carrier,warehouse=whs,
         shipping_cost=round(0 if ship=="Retiro en sucursal" else random.uniform(3,25)*fx,2),
         ship_date=shipd.strftime("%Y-%m-%d") if shipd else None,
         delivery_date=deliv.strftime("%Y-%m-%d") if deliv else None,
         is_returned=status=="Devuelto",
         customer_rating=random.choice([None,None,3,4,4,5,5,5,2,1]) if status=="Entregado" else None))
df=pd.DataFrame(rows)
df.to_csv("ventas_envios.csv",index=False,encoding="utf-8-sig")

print(df.shape, df.order_item_key.is_unique, df.order_null.nunique())
print(df.head(3).T)
