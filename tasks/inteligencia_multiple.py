from tasks.questionnaire import QuestionnaireTask


class InteligenciaMultiple(QuestionnaireTask):
    def __init__(self, screen, background):
        super(InteligenciaMultiple, self).__init__(
            screen,
            background,
            title="Inteligencia Multiple",
            statements_file_name="inteligencia multiple.txt",
            instructions_text="Indica cuan fácil te resulta realizar las siguientes actividades (1 Nada, 2 Algo, 3 Mucho).",
            response_options=[
                {"label": "1", "value": 1, "desc1": "Nada", "desc2": "", "keys": ["1"]},
                {"label": "2", "value": 2, "desc1": "Algo", "desc2": "", "keys": ["2"]},
                {"label": "3", "value": 3, "desc1": "Mucho", "desc2": "", "keys": ["3"]},
            ],
            expected_statement_count=24,
            keyboard_hint="Usa los números 1-3 del teclado para responder. Pulsa <<barra espaciadora>> para continuar.",
            item_prompt="¿Cuán fácil te resulta...?",
        )
