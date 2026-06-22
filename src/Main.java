from fastapi import FastAPI

app = FastAPI(title="PokéDex API de Michi")

pokedex = {
        1: {
        "nombre": "Bulbasaur",
        "tipo": ["Planta", "Veneno"],
        "nivel": 5
        },
        4: {
        "nombre": "Charmander",
        "tipo": ["Fuego"],
        "nivel": 5
        },
        7: {
        "nombre": "Squirtle",
        "tipo": ["Agua"],
        "nivel": 5
        }

        }

@app.get("/")

def leer_raiz():
        return {"mensaje": "¡Bienvenido a la PokéDex API! Mi nombre es Michelle y mi pokemon favorito es Scorbunny" }

@app.get("/pokemons")

def obtener_todos():
        return pokedex