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
