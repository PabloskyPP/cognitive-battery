from tasks.questionnaire import QuestionnaireTask


class NeoPiR(QuestionnaireTask):
    def __init__(self, screen, background):
        super(NeoPiR, self).__init__(
            screen,
            background,
            title="NEO-PI-R",
            statements_file_name="NEOPIR.txt",
            instructions_text=(
                "Esto es un cuestionario de personalidad. El cuestionario consta de 240 enunciados ante "
                "los cuales tendrás que indicar tu grado de acuerdo o desacuerdo marcando un número del 1 al 5 "
                "que equivalen a: 1 = En total desacuerdo, 2 = En desacuerdo, 3 = Neutro, 4 = De acuerdo, 5 = Totalmente de acuerdo."
            ),
            response_options=[
                {"label": "1", "value": 1, "desc1": "En total", "desc2": "desacuerdo", "keys": ["1"]},
                {"label": "2", "value": 2, "desc1": "En", "desc2": "desacuerdo", "keys": ["2"]},
                {"label": "3", "value": 3, "desc1": "Neutro", "desc2": "", "keys": ["3"]},
                {"label": "4", "value": 4, "desc1": "De", "desc2": "acuerdo", "keys": ["4"]},
                {"label": "5", "value": 5, "desc1": "Totalmente", "desc2": "de acuerdo", "keys": ["5"]},
            ],
            expected_statement_count=240,
            keyboard_hint="Usa los números 1-5 del teclado para responder. Pulsa la barra espaciadora para continuar.",
        )
