import copy
import json
import urllib.error
import urllib.request
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, Header, HTTPException, Query, status
from pydantic import BaseModel


app = FastAPI(title="Pokédex API de Diego Ramirez Magaña")

ARCHIVO_DB = Path(__file__).with_name("pokedex.json")
CLAVE_SECRETA = "Mexico gana el mundial."
POKEMON_INICIALES = {1, 4, 7}

POKEDEX_INICIAL = {
    1: {
        "nombre": "Bulbasaur",
        "tipo": ["Planta", "Veneno"],
        "nivel": 5,
        "habilidad": "Piel verde",
        "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"],
        "ataque": 10,
        "defensa": 5,
    },
    2: {
        "nombre": "Ivysaur",
        "tipo": ["Planta", "Veneno"],
        "nivel": 16,
        "habilidad": "Piel verde",
        "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"],
        "ataque": 10,
        "defensa": 5,
    },
    3: {
        "nombre": "Venusaur",
        "tipo": ["Planta", "Veneno"],
        "nivel": 32,
        "habilidad": "Piel verde",
        "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"],
        "ataque": 10,
        "defensa": 5,
    },
    4: {
        "nombre": "Charmander",
        "tipo": ["Fuego"],
        "nivel": 5,
        "habilidad": "Piel roja",
        "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"],
        "ataque": 10,
        "defensa": 5,
    },
    5: {
        "nombre": "Charmeleon",
        "tipo": ["Fuego"],
        "nivel": 16,
        "habilidad": "Piel roja",
        "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"],
        "ataque": 10,
        "defensa": 5,
    },
    6: {
        "nombre": "Charizard",
        "tipo": ["Fuego", "Volador"],
        "nivel": 32,
        "habilidad": "Piel roja",
        "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"],
        "ataque": 10,
        "defensa": 5,
    },
    7: {
        "nombre": "Squirtle",
        "tipo": ["Agua"],
        "nivel": 5,
        "habilidad": "Piel azul",
        "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"],
        "ataque": 10,
        "defensa": 5,
    },
    8: {
        "nombre": "Wartortle",
        "tipo": ["Agua"],
        "nivel": 5,
        "habilidad": "Piel azul",
        "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"],
        "ataque": 10,
        "defensa": 5,
    },
    9: {
        "nombre": "Blastoise",
        "tipo": ["Agua"],
        "nivel": 5,
        "habilidad": "Piel azul",
        "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"],
        "ataque": 10,
        "defensa": 5,
    },
}


class Pokemon(BaseModel):
    nombre: str
    tipo: list[str]
    nivel: int
    habilidad: str
    movimientos: list[str]
    ataque: int
    defensa: int


class PokemonConId(Pokemon):
    id: int


class PokemonParcial(BaseModel):
    nombre: str | None = None
    tipo: list[str] | None = None
    nivel: int | None = None
    habilidad: str | None = None
    movimientos: list[str] | None = None
    ataque: int | None = None
    defensa: int | None = None


def guardar_pokedex(pokedex_actualizada: dict[int, dict]) -> None:
    with open(ARCHIVO_DB, "w", encoding="utf-8") as archivo:
        json.dump(pokedex_actualizada, archivo, ensure_ascii=False, indent=4)


def cargar_pokedex() -> dict[int, dict]:
    if not ARCHIVO_DB.exists():
        pokedex_inicial = copy.deepcopy(POKEDEX_INICIAL)
        guardar_pokedex(pokedex_inicial)
        return pokedex_inicial

    with open(ARCHIVO_DB, "r", encoding="utf-8") as archivo:
        datos_json = json.load(archivo)

    return {int(pokemon_id): datos for pokemon_id, datos in datos_json.items()}


def sincronizar_memoria(pokedex_local: dict[int, dict]) -> None:
    pokedex.clear()
    pokedex.update(pokedex_local)


def validar_api_key(x_api_key: str | None) -> None:
    if x_api_key != CLAVE_SECRETA:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acceso denegado. API key inválida o faltante.",
        )


pokedex = cargar_pokedex()


@app.get("/")
def leer_raiz():
    return {
        "mensaje": (
            "¡Bienvenido a la Pokédex API! Mi nombre es Diego Ramirez Magaña "
            "y mi Pokémon favorito es Charizard"
        )
    }


@app.get("/pokemons")
def obtener_todos_los_pokemon(
    tipo: Annotated[str | None, Query(min_length=1)] = None,
    habilidad: Annotated[str | None, Query(min_length=1)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 5,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    pokedex_local = cargar_pokedex()
    tipo_normalizado = tipo.strip().casefold() if tipo else None
    habilidad_normalizada = habilidad.strip().casefold() if habilidad else None

    resultados = {
        pokemon_id: pokemon
        for pokemon_id, pokemon in pokedex_local.items()
        if (
            tipo_normalizado is None
            or tipo_normalizado in (valor.casefold() for valor in pokemon["tipo"])
        )
        and (
            habilidad_normalizada is None
            or habilidad_normalizada == pokemon["habilidad"].casefold()
        )
    }

    if not resultados:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontraron Pokémon con los filtros solicitados.",
        )

    coincidencias = list(resultados.items())
    resultados_paginados = dict(coincidencias[offset : offset + limit])
    sincronizar_memoria(pokedex_local)

    return {
        "total_coincidencias": len(resultados),
        "limite": limit,
        "desplazamiento": offset,
        "resultados": resultados_paginados,
    }


@app.get("/pokemons/catalogo")
def obtener_catalogo_pokemons(page: int = 1, size: int = 3):
    if page <= 0 or size <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Los valores de pagina o tamaño deben ser mayores a cero.",
        )

    pokedex_local = cargar_pokedex()
    indice_inicial = (page - 1) * size
    indice_final = indice_inicial + size
    resultado_paginado = dict(list(pokedex_local.items())[indice_inicial:indice_final])
    sincronizar_memoria(pokedex_local)

    return {
        "pagina_actual": page,
        "tamano_pagina": size,
        "resultado": resultado_paginado,
    }


@app.get("/pokemons/{pokemon_id}")
def obtener_por_id(pokemon_id: int):
    pokedex_local = cargar_pokedex()

    if pokemon_id not in pokedex_local:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El Pokémon con el ID #{pokemon_id} no existe en la región.",
        )

    sincronizar_memoria(pokedex_local)
    return pokedex_local[pokemon_id]


@app.post("/pokemons")
def registrar_pokemon(
    nuevo_pokemon: PokemonConId,
    x_api_key: Annotated[str | None, Header()] = None,
):
    validar_api_key(x_api_key)
    pokedex_local = cargar_pokedex()
    pokemon_id = nuevo_pokemon.id

    if pokemon_id in pokedex_local:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Ya existe un Pokémon con el ID #{pokemon_id}. "
                f"Se trata de {pokedex_local[pokemon_id]['nombre']}."
            ),
        )

    pokedex_local[pokemon_id] = nuevo_pokemon.model_dump(exclude={"id"})
    guardar_pokedex(pokedex_local)
    sincronizar_memoria(pokedex_local)

    return {
        "mensaje": (
            f"¡Ya está! Nuevo Pokémon registrado con el ID #{pokemon_id} "
            f"y el nombre {pokedex_local[pokemon_id]['nombre']}."
        ),
        "datos": pokedex_local[pokemon_id],
    }


@app.put("/pokemons/{pokemon_id}")
def actualizar_pokemon_completo(pokemon_id: int, pokemon_actualizado: Pokemon):
    pokedex_local = cargar_pokedex()

    if pokemon_id not in pokedex_local:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe el Pokémon #{pokemon_id} que se quiere actualizar.",
        )

    pokedex_local[pokemon_id] = pokemon_actualizado.model_dump()
    guardar_pokedex(pokedex_local)
    sincronizar_memoria(pokedex_local)

    return {
        "mensaje": "Reemplazo completado con éxito.",
        "datos": pokedex_local[pokemon_id],
    }


@app.patch("/pokemons/{pokemon_id}")
def actualizar_pokemon_parcial(pokemon_id: int, pokemon_actualizado: PokemonParcial):
    pokedex_local = cargar_pokedex()

    if pokemon_id not in pokedex_local:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe el Pokémon #{pokemon_id} que se quiere actualizar.",
        )

    datos_a_actualizar = pokemon_actualizado.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )
    pokedex_local[pokemon_id].update(datos_a_actualizar)
    guardar_pokedex(pokedex_local)
    sincronizar_memoria(pokedex_local)

    return {
        "mensaje": "Actualización parcial exitosa.",
        "datos": pokedex_local[pokemon_id],
    }


@app.delete("/pokemons/{pokemon_id}")
def eliminar_pokemon(
    pokemon_id: int,
    x_api_key: Annotated[str | None, Header()] = None,
):
    validar_api_key(x_api_key)
    pokedex_local = cargar_pokedex()

    if pokemon_id not in pokedex_local:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe el Pokémon #{pokemon_id} que se quiere borrar.",
        )

    if pokemon_id in POKEMON_INICIALES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar un Pokémon inicial.",
        )

    pokemon_eliminado = pokedex_local.pop(pokemon_id)
    guardar_pokedex(pokedex_local)
    sincronizar_memoria(pokedex_local)

    return {
        "mensaje": f"¡Adiós, {pokemon_eliminado['nombre']}! Pokémon eliminado exitosamente."
    }


@app.get("/investigar/{nombre}", response_model=Pokemon)
def investigar_pokemon_externo(nombre: str):
    url_externa = f"https://pokeapi.co/api/v2/pokemon/{nombre.lower()}"
    solicitud = urllib.request.Request(
        url_externa,
        headers={"User-Agent": "PokemonClassAPI/1.0"},
    )

    try:
        with urllib.request.urlopen(solicitud, timeout=10) as respuesta:
            datos = json.load(respuesta)
    except urllib.error.HTTPError as error:
        if error.code == status.HTTP_404_NOT_FOUND:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No hay información de {nombre.capitalize()} en la PokéAPI.",
            ) from error
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="La PokéAPI no respondió correctamente.",
        ) from error
    except urllib.error.URLError as error:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No se pudo conectar con la PokéAPI.",
        ) from error

    estadisticas = {
        estadistica["stat"]["name"]: estadistica["base_stat"]
        for estadistica in datos["stats"]
    }

    return {
        "nombre": datos["name"].capitalize(),
        "tipo": [
            tipo_pokemon["type"]["name"].capitalize()
            for tipo_pokemon in datos["types"]
        ],
        "nivel": 1,
        "habilidad": datos["abilities"][0]["ability"]["name"].capitalize(),
        "movimientos": [
            movimiento["move"]["name"]
            for movimiento in datos["moves"][:4]
        ],
        "ataque": estadisticas["attack"],
        "defensa": estadisticas["defense"],
    }
