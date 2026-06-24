from typing import Annotated

from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel


app = FastAPI(title="Pokédex API de Diego Rami")

pokedex = {
    1: {"nombre": "Bulbasaur", "tipo": ["Planta", "Veneno"], "nivel": 5, "habilidad": "Piel verde", "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"], "ataque": 10, "defensa": 5},
    2: {"nombre": "Ivysaur", "tipo": ["Planta", "Veneno"], "nivel": 16, "habilidad": "Piel verde", "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"], "ataque": 10, "defensa": 5},
    3: {"nombre": "Venusaur", "tipo": ["Planta", "Veneno"], "nivel": 32, "habilidad": "Piel verde", "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"], "ataque": 10, "defensa": 5},
    4: {"nombre": "Charmander", "tipo": ["Fuego"], "nivel": 5, "habilidad": "Piel roja", "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"], "ataque": 10, "defensa": 5},
    5: {"nombre": "Charmeleon", "tipo": ["Fuego"], "nivel": 16, "habilidad": "Piel roja", "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"], "ataque": 10, "defensa": 5},
    6: {"nombre": "Charizard", "tipo": ["Fuego", "Volador"], "nivel": 32, "habilidad": "Piel roja", "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"], "ataque": 10, "defensa": 5},
    7: {"nombre": "Squirtle", "tipo": ["Agua"], "nivel": 5, "habilidad": "Piel azul", "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"], "ataque": 10, "defensa": 5},
    8: {"nombre": "Wartortle", "tipo": ["Agua"], "nivel": 5, "habilidad": "Piel azul", "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"], "ataque": 10, "defensa": 5},
    9: {"nombre": "Blastoise", "tipo": ["Agua"], "nivel": 5, "habilidad": "Piel azul", "movimientos": ["Placaje", "Gruñido", "Arañazo", "Látigo"], "ataque": 10, "defensa": 5}
}
# se declaran pokemons iniciales
pokemon_iniciales = {1, 4, 7}

class Pokemon(BaseModel):
    nombre: str
    tipo: list[str]
    nivel: int
    habilidad: str
    movimientos: list[str]
    ataque: int
    defensa: int


class PokemonParcial(BaseModel):
    nombre: str | None = None
    tipo: list[str] | None = None
    nivel: int | None = None
    habilidad: str | None = None
    movimientos: list[str] | None = None
    ataque: int | None = None
    defensa: int | None = None


@app.get("/")
def leer_raiz():
    return {
        "mensaje": (
            "¡Bienvenido a la Pokédex API! Mi nombre es Diego Rami "
            "y mi Pokémon favorito es Charizard"
        )
    }


@app.get("/pokemons/{pokemon_id}")
def obtener_por_id(pokemon_id: int):
    if pokemon_id not in pokedex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"El Pokémon con el ID #{pokemon_id} no existe en la región.",
        )
    return pokedex[pokemon_id]


@app.get("/pokemons")
def obtener_todos_los_pokemon(
    tipo: Annotated[str | None, Query(min_length=1)] = None,
    habilidad: Annotated[str | None, Query(min_length=1)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 5,
    offset: Annotated[int, Query(ge=0)] = 0,
):
    """Filtra la Pokédex y después pagina las coincidencias."""
    tipo_normalizado = tipo.strip().casefold() if tipo else None
    habilidad_normalizada = habilidad.strip().casefold() if habilidad else None

    if tipo_normalizado and not any(
        tipo_normalizado in (tipo_pokemon.casefold() for tipo_pokemon in pokemon["tipo"])
        for pokemon in pokedex.values()
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe ningún Pokémon de tipo '{tipo}' en la Pokédex.",
        )

    if habilidad_normalizada and not any(
        habilidad_normalizada == pokemon["habilidad"].casefold()
        for pokemon in pokedex.values()
    ):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe ningún Pokémon con la habilidad '{habilidad}' en la Pokédex.",
        )

    resultados = {
        pokemon_id: pokemon
        for pokemon_id, pokemon in pokedex.items()
        if (
            tipo_normalizado is None
            or tipo_normalizado
            in (tipo_pokemon.casefold() for tipo_pokemon in pokemon["tipo"])
        )
        and (
            habilidad_normalizada is None
            or habilidad_normalizada == pokemon["habilidad"].casefold()
        )
    }

    if not resultados:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No se encontraron Pokémon con la combinación de filtros "
                f"tipo='{tipo}' y habilidad='{habilidad}'."
            ),
        )

    coincidencias = list(resultados.items())
    resultados_paginados = dict(coincidencias[offset : offset + limit])

    return {
        "total_coincidencias": len(resultados),
        "limite": limit,
        "desplazamiento": offset,
        "resultados": resultados_paginados,
    }


@app.post("/pokemon/{pokemon_id}")
def registrar_nuevo_pokemon(pokemon_id: int, nuevo_pokemon: Pokemon):
    if pokemon_id in pokedex:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Ya existe un Pokémon con el ID #{pokemon_id}. "
                f"Se trata de {pokedex[pokemon_id]['nombre']}."
            ),
        )
    pokedex[pokemon_id] = nuevo_pokemon.model_dump()
    return {
        "mensaje": (
            f"¡Ya está! Nuevo Pokémon registrado con el ID #{pokemon_id} "
            f"y el nombre {pokedex[pokemon_id]['nombre']}."
        ),
        "datos": pokedex[pokemon_id],
    }


@app.put("/pokemons/{pokemon_id}")
def actualizar_pokemon_completo(pokemon_id: int, pokemon_actualizado: Pokemon):
    if pokemon_id not in pokedex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe el Pokémon #{pokemon_id} que se quiere actualizar en la Pokédex.",
        )
    pokedex[pokemon_id] = pokemon_actualizado.model_dump()

    return {
        "mensaje": "Reemplazo completado con éxito.",
        "datos": pokedex[pokemon_id],
    }


@app.patch("/pokemons/{pokemon_id}")
def actualizar_pokemon_parcial(pokemon_id: int, pokemon_actualizado: PokemonParcial):
    if pokemon_id not in pokedex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe el Pokémon #{pokemon_id} que se quiere actualizar en la Pokédex.",
        )

    datos_a_actualizar = pokemon_actualizado.model_dump(
        exclude_unset=True,
        exclude_none=True,
    )
    for llave, valor in datos_a_actualizar.items():
        pokedex[pokemon_id][llave] = valor

    return {
        "mensaje": "Actualización parcial exitosa.",
        "datos": pokedex[pokemon_id],
    }


@app.delete("/pokemons/{pokemon_id}")
def liberar_pokemon(pokemon_id: int):
    if pokemon_id not in pokedex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No existe el Pokémon #{pokemon_id} que se quiere borrar en la Pokédex.",
        )

    if pokemon_id in pokemon_iniciales:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para eliminar un Pokémon inicial.",
        )

    pokemon_liberado = pokedex.pop(pokemon_id)
    nombre = pokemon_liberado["nombre"]

    return {
        "mensaje": f"¡Adiós, {nombre}! Pokémon liberado exitosamente."
    }
