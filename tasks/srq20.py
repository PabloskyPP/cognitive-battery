from tasks.questionnaire import QuestionnaireTask


class SRQ20(QuestionnaireTask):
    def __init__(self, screen, background):
        super(SRQ20, self).__init__(
            screen,
            background,
            title="SRQ20",
            statements_file_name="SRQ-20.txt",
            instructions_text=(
                "Las siguientes cuestiones están relacionadas con ciertos malestares y problemas que puedes "
                "haber tenido en los últimos 30 días. Si crees que la pregunta aplica para ti y has presentado "
                "el problema descrito en los últimos 30 días, responda SÍ. Por el contrario, si no has tenido "
                "ese problema en los últimos 30 días, responda NO."
            ),
            response_options=[
                {"label": "SI", "value": "SI", "desc1": "", "desc2": "", "keys": ["s", "1"]},
                {"label": "NO", "value": "NO", "desc1": "", "desc2": "", "keys": ["n", "2"]},
            ],
            expected_statement_count=20,
            keyboard_hint="Usa S o N (también 1 o 2) para responder. Pulsa <<barra espaciadora>> para continuar.",
            item_prompt="¿En los últimos 30 días te ha pasado que...?",
        )
