from collections import namedtuple
import datetime

def get_overlap(lowest_value, start1, end1, start2, end2):
    Range = namedtuple('Range', ['start', 'end'])
    r1 = Range(start=start1, end=end1)
    r2 = Range(start=start2, end=end2)
    latest_start = max(r1.start, r2.start)
    earliest_end = min(r1.end, r2.end)
    delta = (earliest_end - latest_start)
    return max(lowest_value, delta)

def sumar_horas(hora_inicio, minutos_inicio, incremento_hora, incremento_minuto):
    """
        parametro hora de inicio, minutos de inicio : es la hora de comienzo
        el incremento tambien esta parametrizado en horas y minutos
    """
    delta = datetime.timedelta(hours=incremento_hora, minutes=incremento_minuto)
    return datetime.datetime(1, 1, 1, hora_inicio, minutos_inicio) + delta
