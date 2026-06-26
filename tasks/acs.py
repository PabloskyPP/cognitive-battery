from tasks.questionnaire import QuestionnaireTask


class ACS(QuestionnaireTask):
    def __init__(self, screen, background):
        super(ACS, self).__init__(
            screen,
            background,
            title="ACS",
            statements_file_name="ACS.txt",
            instructions_text="Indica con qué frecuencia se cumplen en ti los siguientes enunciados (1 Nunca, 2 Poco, 3 Bastante, 4 Mucho).",
            response_options=[
                {"label": "1", "value": 1, "desc1": "Nunca", "desc2": "", "keys": ["1"]},
                {"label": "2", "value": 2, "desc1": "Poco", "desc2": "", "keys": ["2"]},
                {"label": "3", "value": 3, "desc1": "Bastante", "desc2": "", "keys": ["3"]},
                {"label": "4", "value": 4, "desc1": "Mucho", "desc2": "", "keys": ["4"]},
            ],
            expected_statement_count=20,
            keyboard_hint="Usa los números 1-4 del teclado para responder. Pulsa <<barra espaciadora>> para continuar.",
            item_prompt="¿Con qué frecuencia...?",
        )
