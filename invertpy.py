import investpy
import sqlite3
import sqlalchemy
from sqlalchemy import Column, Integer, String, ForeignKey, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import asyncio
import time
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import datetime
import json

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

with open("config.json") as json_data_file:
    data = json.load(json_data_file)

logger = logging.getLogger(__name__)
token = data["telegram"]["token"]
updater = Updater(token, use_context=True)
bot = telegram.Bot(token) 

engine = sqlalchemy.create_engine("sqlite:///"+data["inversting"]["db"])
base = declarative_base()

Session = sessionmaker(bind=engine)
session = Session()
        
class Periodicidad(base):
    __tablename__ = "periodicidad"
    id = Column(Integer, primary_key=True)
    periodicidad = Column(String)
    periodo = Column(String)
    def __repr__(self):
        return f"periodicidad: {self.periodicidad}"

class Cliente(base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True)
    cliente = Column(Integer)
    def __repr__(self):
        return f"{self.cliente}"  
    
class Estado(base):
    __tablename__ = "estado"
    id = Column(Integer, primary_key=True)
    estado = Column(Integer)
    def __repr__(self):
        return f"Estado: {self.estado}"  
    
class Emp(base):
    __tablename__ = "emp"
    id = Column(Integer, primary_key=True)
    empresa = Column(String)
    def __repr__(self):
        return f"Empresa: {self.empresa}"  

class Empresas(base):
    __tablename__ = "empresas"
    id = Column(Integer, primary_key=True)
    cliente = Column(Integer, ForeignKey("clientes.id"))
    empresa = Column(String, ForeignKey("emp.id"))
    periodicidad = Column(Integer, ForeignKey("periodicidad.id"))
    estado = Column(Integer, ForeignKey("estado.id"))
    
    cliente_id = relationship("Cliente")
    periodicidad_id = relationship("Periodicidad")
    estado_id = relationship("Estado")
    empresa_id = relationship("Emp")
    
    def __repr__(self):
        return f"Empresa: {self.empresa} cliente {self.cliente_id.cliente} y periodicidad {self.periodicidad_id.periodicidad}"

def start(update, context):
    try:
        query = session.query(Cliente).filter_by(cliente=str(update.message.chat.id))
        session.commit()
        try:
            if query[0].cliente == update.message.chat.id:
                update.message.reply_text('Cliente ya existente.')
        except:    
            cliente = Cliente(cliente = update.message.chat.id)
            session.add(cliente)
            session.commit()
            update.message.reply_text('Cliente agregado correctamente.')
    except:
        update.message.reply_text('No se ha podido cargar el cliente.')
def error(update, context):
     """Log Errors caused by Updates."""
     logger.warning('Update "%s" caused error "%s"', update, context.error)

def add(update, context):
    try:
        query = session.query(Cliente).filter_by(cliente=update.message.chat.id)
        session.commit()
        for client in query:
            if client.cliente == update.message.chat.id:
                nueva_empresa = update.message.text.replace("/add ","")
                try:
                    search_result = investpy.search_quotes(text=nueva_empresa, products=['stocks'],countries=['united states'], n_results=1)
                    print(search_result.name)
                    query2 = session.query(Emp).filter_by(empresa=search_result.name)
                    session.commit()
                    if(query2.count() == 0):
                        try:
                            empresa = Emp(empresa = search_result.name)
                            session.add(empresa)
                            session.commit()
                            query2 = session.query(Emp).filter_by(empresa=search_result.name)
                            session.commit()
                        except:
                            print("Empresa",nueva_empresa,"no encontrada en Inversting, pruebe de nuevo")
                            bot.sendMessage(chat_id = update.message.chat.id, text="Empresa " + nueva_empresa +" no encontrada en Inversting, pruebe de nuevo")
                    for emp in query2:
                        print("cliente:", client.id ,"Empresa:", emp.empresa,"id:",emp.id)
                        print("Empresa",emp.empresa,"encontrada")
                        agregar = Empresas(cliente = client.id, empresa = emp.id, periodicidad = 2, estado = 3)
                        session.add(agregar)
                        session.commit()
                        bot.sendMessage(chat_id = client.cliente, text= emp.empresa + ' agregada correctamente.')
                        break   
                except:
                    print("Empresa",nueva_empresa,"no encontrada en Inversting, pruebe de nuevo")
                    bot.sendMessage(chat_id=client.cliente, text="Empresa " + nueva_empresa +" no encontrada en Inversting, pruebe de nuevo")
            else:
                print("Usuario no encontrado")
    except:
        print("Debe iniciar el bot enviando /start para iniciar")

def rem(update, context):
    try:
        query = session.query(Cliente).filter_by(cliente=update.message.chat.id)
        session.commit()
        for client in query:
            if client.cliente == update.message.chat.id:
                nueva_empresa = update.message.text.replace("/rem ","")
                try:
                    search_result = investpy.search_quotes(text=nueva_empresa, products=['stocks'],countries=['united states'], n_results=1)
                    print(search_result.name)
                    query2 = session.query(Empresas).join(Empresas.empresa_id).filter_by(empresa=search_result.name).join(Empresas.cliente_id).filter_by(cliente=update.message.chat.id)
                    session.commit()
                    for empresa in query2:
                        print(empresa.cliente_id.cliente, empresa.empresa_id.empresa)
                        session.delete(empresa)
                        bot.sendMessage(chat_id=client.cliente, text="Empresa " + empresa.empresa_id.empresa +" eliminada correctamente.")
                except:
                    print("Empresa",nueva_empresa,"no encontrada en Inversting, pruebe de nuevo")
                    bot.sendMessage(chat_id=client.cliente, text="Empresa " + nueva_empresa +" no encontrada en Inversting, pruebe de nuevo")
            else:
                print("Usuario no encontrado")
    except:
        print("Debe iniciar el bot enviando /start para iniciar")
def update(update, context):
    try:
        query = session.query(Cliente).filter_by(cliente=update.message.chat.id)
        session.commit()
        for client in query:
            query2 = session.query(Empresas).filter_by(cliente=client.id).join(Empresas.empresa_id).order_by(Emp.empresa)
            session.commit()
            for cliente in query2:
                print(client.cliente, ":",cliente.empresa_id, ". ",cliente.estado_id,", periodicidad: ", cliente.periodicidad_id.periodo,".")
                bot.sendMessage(chat_id = client.cliente, text = cliente.empresa_id.empresa + " " + cliente.estado_id.estado + ", periodicidad: " + cliente.periodicidad_id.periodo + ".")
    except:
        print("Debe iniciar el bot enviando /start para iniciar")

def help(update, context):
    update.message.reply_text('\\start -> registrar usuario')
    update.message.reply_text('\\add + "empresa" -> Agregar empresa al usuario actual. Ejemplo: \add apple')
    update.message.reply_text('\\rem + "empresa" -> Eliminar empresa al usuario actual. Ejemplo: \rem apple')
    update.message.reply_text('\\update -> Eenvia el resumen actual')


def start_bot():
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("add", add))
    dp.add_handler(CommandHandler("update", update))
    dp.add_handler(CommandHandler("rem", rem))
    dp.add_handler(CommandHandler("help", help))
    dp.add_error_handler(error)
    updater.start_polling()

async def consulta():
    
    now=datetime.datetime.strftime(datetime.datetime.now(),'%H:%M')
    if int(now.split(":")[0]) > 19 or datetime.datetime.today().isoweekday() >= 6:
        print("Me voy a dormir")
        await asyncio.sleep(54000)
    Session = sessionmaker(bind=engine)
    session = Session()
    query = session.query(Empresas)
    session.commit()

    for empresa in query:
        try:
            search_result = investpy.search_quotes(text = empresa.empresa_id.empresa, products=['stocks'],
                                                countries=['united states'], n_results=1)
        except:
            print("Error al realizar la consulta de ", empresa.empresa_id.empresa)  
        technical_indicators = search_result.retrieve_technical_indicators(interval=empresa.periodicidad_id.periodicidad)
        compra = 0
        neutral = 0
        venta = 0
        for signal in technical_indicators['signal']:
            if signal == 'buy':
                compra += 1
            elif signal == 'sell':
                venta += 0
            else:  
                neutral += 1
        if compra > venta and compra > neutral:
            if compra >5:
                resultado = "compra fuerte"
            else:
                resultado = "compra"
        elif venta > compra and venta > neutral:
            if venta > 5:
                resultado = "venta fuerte"
            else:
                resultado = "venta"
        else:
            resultado = "neutral"

        if resultado !=  empresa.estado_id.estado:
            try:
                query = session.query(Estado)
                session.commit()
                for respuesta in query:
                    if respuesta.estado == resultado:
                        empresa.estado =respuesta.id
                        session.commit()
                print("Cliente: " + str(empresa.cliente_id.cliente) + "," + empresa.empresa_id.empresa + ' cambio su estado a ' + resultado + ".")
                bot.sendMessage(chat_id = empresa.cliente_id.cliente, text = empresa.empresa_id.empresa + ", periodicidad: " + empresa.periodicidad_id.periodo +  ' cambio su estado a ' + resultado + ".")
            except:
                print("Error al cambiar el estado")
        else:
            print("Cliente: " + str(empresa.cliente_id.cliente) + "," + empresa.empresa_id.empresa + ' sin cambios.')
        await asyncio.sleep(1)     
    await asyncio.sleep(1800)

async def main():
    start_bot()
    while 1:
        task_consulta = asyncio.create_task(consulta())
        await task_consulta

asyncio.run(main())
