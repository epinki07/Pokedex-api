from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel
from typing import List, Optional


app = FastAPI(title="PokéDex API de Diego Rami")

pokedex = {
    1: {
        "nombre": "Bulbasaur",
        "tipo": ["Planta", "Veneno"],
        "nivel": 5,
        "habilidad": "Espesura"},
    4: {
        "nombre": "Charmander",
        "tipo": ["Fuego"],
        "nivel": 5,
        "habilidad": "Blaze"},
    7: {
        "nombre": "Squirtle",
        "tipo": ["Agua"],
        "nivel": 5,
        "habilidad": "Torrente"}}

class Pokemon(BaseModel):
    nombre: str
    tipo: List[str]
    nivel: int
    habilidad: str


@app.get("/")

def leer_raiz():
    return {"mensaje": "¡Bienvenido a la PokéDex API! Mi nombre es Diego Rami y mi pokemon favorito es Charizard" }
@app.get("/pokemons/{pokemon_id}")


#Ejemplo de Path Parameter
def obtener_por_id(pokemon_id : int):
    if pokemon_id not in pokedex:
        raise HTTPException(status_code = 404, detail= f"El Pokemón con el ID#{pokemon_id} no existe en la región" )
    return pokedex[pokemon_id]

#Ejemplo de Query Parameter

@app.get("/pokemons")

def obtener_todos_los_pokemon(tipo : Optional[str] = None, habilidad : Optional[str] = None):
    #1. El usuario no especifico tipo
    if tipo is None and habilidad is None:
        return pokedex

    #2. El usuario especifico un tipo
    pokemon_filtrado = {}
    pokemon_tipo = {}
    pokemon_habilidad = {}

    for pokemon_id, datos in pokedex.items():
        if tipo is None or tipo.capitalize() in datos["tipo"]:
            pokemon_tipo[pokemon_id] = datos

    if not pokemon_tipo:
        raise HTTPException(
            status_code =404,
            detail = f"No existe ningún Pokemon de tipo {tipo}"
        )

    for pokemon_id, datos in pokedex.items():
        if habilidad is None or habilidad.capitalize() == datos["habilidad"]:
            pokemon_habilidad[pokemon_id] = datos


    if not pokemon_habilidad:
        raise HTTPException(
            status_code=404,
            detail = f"No existe ningún Pokemon con la habilidad {habilidad}"
        )

    for pokemon_id, datos in pokedex.items():
        if (tipo is None or tipo.capitalize() in datos["tipo"]) and (habilidad is None or habilidad.capitalize() == datos["habilidad"]):
            pokemon_filtrado[pokemon_id] = datos
    if not pokemon_filtrado:
        raise HTTPException(
            status_code=404,
            detail=f"No existe ningún Pokémon con los siguientes filtros: {tipo}, {habilidad}"
        )

    return pokemon_filtrado

# Endpoint para registrar nuevo Pokemon

@app.post("/pokemon/{pokemon_id}")

def registrar_nuevo_pokemon(pokemon_id : int, nuevo_pokemon : Pokemon):
    # Recibir un pokemon: Nombre, tipo, nivel, etc.
    # Reglas de negocio
    if pokemon_id in pokedex:
        raise HTTPException(
            status_code = 400,
            detail = f"Ya existe un Pokemon con el ID #{pokemon_id}. Se trata de {pokedex[pokemon_id]['nombre']}"
        )
    pokedex[pokemon_id] = nuevo_pokemon.model_dump() # Registro nuevo pokemon en la pokedex
    return {
         "mensaje": f"¡Ya está! Nuevo Pokemón registrado con el ID#{pokemon_id} con el nombre {pokedex[pokemon_id]['nombre']}",
         "datos": pokedex[pokemon_id]
     }

# 1. Modificar pokedex y agregar  4 movimientos [Lista : str]. Y agregar 2 parámetros de defensa, y ataque. Agregar un pokémon nuevo con lo mismo y que se muestre como se hizo.
# 2. Checar pk que no se registra.

#EndPoint para actualizar por COMPLETO un endpoint de la pokedex
@app.put("/pokemons/{pokemon.id}")
def actualizar_pokemon_completo(pokemon_id: int, Pokemon_actualizados: Pokemon)
    if (pokemon_id not in pokedex )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe el pokemon que se quiere actualizar en la pokedex."
        )
    pokedex[pokemon_id] = Pokemon_actualizados.model_dump()

    return {
        "Mensaje: Reemplazo completado con éxito. "}
        "datos": pokedex[pokemon.id]