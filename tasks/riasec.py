from tasks.questionnaire import QuestionnaireTask


class RIASEC(QuestionnaireTask):
    def __init__(self, screen, background):
        super(RIASEC, self).__init__(
            screen,
            background,
            title="RIASEC",
            statements_file_name="RIASEC.txt",
            instructions_text="Indica cuánto disfrutas realizar las siguientes actividades (1 Nada, 2 Algo, 3 Mucho).",
            response_options=[
                {"label": "1", "value": 1, "desc1": "Nada", "desc2": "", "keys": ["1"]},
                {"label": "2", "value": 2, "desc1": "Algo", "desc2": "", "keys": ["2"]},
                {"label": "3", "value": 3, "desc1": "Mucho", "desc2": "", "keys": ["3"]},
            ],
            expected_statement_count=36,
            keyboard_hint="Usa los números 1-3 del teclado para responder. Pulsa <<barra espaciadora>> para continuar.",
        )
