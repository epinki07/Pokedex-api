import copy
import unittest

from fastapi import HTTPException

import main


class PokedexApiTests(unittest.TestCase):
    def setUp(self):
        self.pokedex_original = copy.deepcopy(main.pokedex)

    def tearDown(self):
        main.pokedex.clear()
        main.pokedex.update(self.pokedex_original)

    def test_paginacion_devuelve_metadatos_y_resultados(self):
        primera_pagina = main.obtener_todos_los_pokemon(limit=5, offset=0)
        segunda_pagina = main.obtener_todos_los_pokemon(limit=5, offset=5)

        self.assertEqual(primera_pagina["total_coincidencias"], 9)
        self.assertEqual(len(primera_pagina["resultados"]), 5)
        self.assertEqual(len(segunda_pagina["resultados"]), 4)

    def test_catalogo_usa_page_y_size_por_defecto(self):
        respuesta = main.obtener_catalogo_pokemons()

        self.assertEqual(respuesta["pagina_actual"], 1)
        self.assertEqual(respuesta["tamano_pagina"], 3)
        self.assertEqual(set(respuesta["resultado"]), {1, 2, 3})

    def test_catalogo_calcula_indices_desde_page_y_size(self):
        respuesta = main.obtener_catalogo_pokemons(page=2, size=3)

        self.assertEqual(respuesta["pagina_actual"], 2)
        self.assertEqual(respuesta["tamano_pagina"], 3)
        self.assertEqual(set(respuesta["resultado"]), {4, 5, 6})

    def test_catalogo_rechaza_page_o_size_invalidos(self):
        casos_invalidos = [
            {"page": 0, "size": 3},
            {"page": -1, "size": 3},
            {"page": 1, "size": 0},
            {"page": 1, "size": -3},
        ]

        for caso in casos_invalidos:
            with self.subTest(caso=caso):
                with self.assertRaises(HTTPException) as contexto:
                    main.obtener_catalogo_pokemons(**caso)

                self.assertEqual(contexto.exception.status_code, 400)

    def test_catalogo_se_registra_antes_de_ruta_por_id(self):
        rutas = [ruta.path for ruta in main.app.routes]

        self.assertLess(
            rutas.index("/pokemons/catalogo"),
            rutas.index("/pokemons/{pokemon_id}"),
        )

    def test_filtros_son_combinables_e_ignoran_mayusculas(self):
        respuesta = main.obtener_todos_los_pokemon(
            tipo="AGUA",
            habilidad="piel AZUL",
            limit=10,
            offset=0,
        )

        self.assertEqual(respuesta["total_coincidencias"], 3)
        self.assertEqual(set(respuesta["resultados"]), {7, 8, 9})

    def test_filtro_inexistente_devuelve_404(self):
        with self.assertRaises(HTTPException) as contexto:
            main.obtener_todos_los_pokemon(
                tipo="Cósmico",
                limit=5,
                offset=0,
            )

        self.assertEqual(contexto.exception.status_code, 404)

    def test_ciclo_crud_completo(self):
        nuevo = main.Pokemon(
            nombre="Pikachu",
            tipo=["Eléctrico"],
            nivel=10,
            habilidad="Electricidad Estática",
            movimientos=["Impactrueno"],
            ataque=55,
            defensa=40,
        )

        main.registrar_nuevo_pokemon(25, nuevo)
        self.assertEqual(main.obtener_por_id(25)["nombre"], "Pikachu")

        main.actualizar_pokemon_parcial(
            25,
            main.PokemonParcial(nivel=12),
        )
        self.assertEqual(main.obtener_por_id(25)["nivel"], 12)

        reemplazo = nuevo.model_copy(update={"nombre": "Raichu", "nivel": 30})
        main.actualizar_pokemon_completo(25, reemplazo)
        self.assertEqual(main.obtener_por_id(25)["nombre"], "Raichu")

        main.liberar_pokemon(25)
        self.assertNotIn(25, main.pokedex)

    def test_no_permite_liberar_un_pokemon_inicial(self):
        with self.assertRaises(HTTPException) as contexto:
            main.liberar_pokemon(1)

        self.assertEqual(contexto.exception.status_code, 403)


if __name__ == "__main__":
    unittest.main()
